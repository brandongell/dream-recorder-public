// State manager for Dream Recorder
const StateManager = {
    // Possible states
    STATES: {
        STARTUP: 'startup',
        CLOCK: 'clock',
        RECORDING: 'recording',
        PROCESSING: 'processing',
        PLAYBACK: 'playback',
        ERROR: 'error',
        SCREEN_SLEEP: 'screen_sleep'
    },

    // Configuration (will be populated from server)
    config: {
    },

    // Input modes (kept for input simulator compatibility)
    MODES: {
        SINGLE_TAP: 'single_tap',
        DOUBLE_TAP: 'double_tap'
    },

    // Current state and mode
    currentState: 'startup',
    currentMode: 'single_tap',
    error: null,
    previousState: null,
    stateChangeCallbacks: [],
    playbackTimer: null,

    // Initialize state manager
    async init() {
        try {
            const response = await fetch('/api/config');
            const config = await response.json();
            this.config.playbackDuration = config.playback_duration;
            this.config.logoFadeInDuration = config.logo_fade_in_duration;
            this.config.logoFadeOutDuration = config.logo_fade_out_duration;
            this.config.clockFadeInDuration = config.clock_fade_in_duration;
            this.config.clockFadeOutDuration = config.clock_fade_out_duration;
            this.config.transitionDelay = config.transition_delay;
            this.config.screenSleepFadeOutDuration = config.screen_sleep_fade_out_duration || 300;
            this.config.screenWakeFadeInDuration = config.screen_wake_fade_in_duration || 300;
        } catch (error) {
            console.error('Failed to fetch config:', error);
        }

        // Set initial state to STARTUP
        this.currentState = this.STATES.STARTUP;
        this.updateStatus();

        // Start the startup sequence
        this.startStartupSequence();
    },

    // Handle startup sequence
    startStartupSequence() {
        const logo = document.querySelector('.startup-logo');
        const clockDisplay = document.getElementById('clockDisplay');

        // Ensure clock is hidden
        clockDisplay.style.display = 'none';
        clockDisplay.style.opacity = '0';

        // Reset logo styles
        logo.style.opacity = '0';
        logo.style.display = 'block';
        logo.style.transition = 'none';
        
        // Force a reflow to ensure styles are applied
        logo.offsetHeight;
        
        // Start the sequence
        this.fadeInLogo(logo);
    },

    // Fade in the logo
    fadeInLogo(logo) {
        // Set up transition for fade in
        logo.style.transition = `opacity ${this.config.logoFadeInDuration}ms ease-out`;
        logo.style.opacity = '1';

        // After fade in, wait and then fade out
        setTimeout(() => {
            this.fadeOutLogo(logo);
        }, this.config.logoFadeInDuration + this.config.transitionDelay);
    },

    // Fade out the logo
    fadeOutLogo(logo) {
        // Set up transition for fade out
        logo.style.transition = `opacity ${this.config.logoFadeOutDuration}ms ease-out`;
        logo.style.opacity = '0';

        // After fade out completes, transition to CLOCK state
        setTimeout(() => {
            logo.style.display = 'none';
            this.updateState(this.STATES.CLOCK);
        }, this.config.logoFadeOutDuration);
    },

    // Update state
    updateState(newState, errorMessage = null) {
        console.log(`State transition: ${this.currentState} -> ${newState}`);
        // Don't allow state changes during startup sequence
        if (this.currentState === this.STATES.STARTUP && newState !== this.STATES.CLOCK) {
            return;
        }

        // Clear any existing timers
        if (this.playbackTimer) {
            clearTimeout(this.playbackTimer);
            this.playbackTimer = null;
        }

        // Handle transitions
        this.handleStateTransition(newState);

        this.previousState = this.currentState;
        this.currentState = newState;
        this.error = errorMessage;
        this.updateStatus();
        
        // Handle icon animations based on state
        if (this.currentState === this.STATES.RECORDING) {
            IconAnimations.show(IconAnimations.TYPES.RECORDING);
        } else if (this.currentState === this.STATES.PROCESSING) {
            IconAnimations.show(IconAnimations.TYPES.GENERATING);
        } else if (this.currentState === this.STATES.ERROR) {
            IconAnimations.show(IconAnimations.TYPES.ERROR);
        } else {
            // Hide icons for all other states (STARTUP, CLOCK, PLAYBACK, etc.)
            IconAnimations.hideAll();
        }
        
        // Set up playback timer if entering playback state
        if (this.currentState === this.STATES.PLAYBACK) {
            this.playbackTimer = setTimeout(() => {
                this.updateState(this.STATES.CLOCK);
            }, this.config.playbackDuration * 1000); // Convert to milliseconds
        }
        
        // Notify all registered callbacks
        this.stateChangeCallbacks.forEach(callback => callback(this.currentState, this.previousState));
        
        // Emit state change event
        const event = new CustomEvent('stateChange', { 
            detail: { 
                state: this.currentState, 
                error: this.error,
                mode: this.currentMode
            } 
        });
        document.dispatchEvent(event);

        // Hide errorDiv if leaving ERROR state
        if (this.currentState !== this.STATES.ERROR && window.errorDiv) {
            window.errorDiv.style.display = 'none';
        }
    },

    // Handle state transitions
    handleStateTransition(newState) {
        const clockDisplay = document.getElementById('clockDisplay');
        const videoContainer = document.getElementById('videoContainer');
        const video = document.getElementById('generatedVideo');

        // Handle video container
        if (videoContainer) {
            if (newState === this.STATES.PLAYBACK) {
                // Show video container
                videoContainer.style.display = 'block';
                
                // Force a reflow to ensure transition works
                videoContainer.offsetHeight;
                
                // Fade in video container
                videoContainer.style.opacity = '1';
                
                // After container is visible, fade in video
                setTimeout(() => {
                    if (video) {
                        video.style.opacity = '1';
                        if (video.paused) {
                            video.play().catch(error => console.error('Error playing video:', error));
                        }
                    }
                }, this.config.transitionDelay);
            } else if (this.currentState === this.STATES.PLAYBACK) {
                // Reset server playback state when leaving PLAYBACK
                if (window.socket) {
                    window.socket.emit("reset_playback_state");
                }
                // Fade out video first
                if (video) {
                    video.style.opacity = '0';
                }
                
                // Then fade out container
                videoContainer.style.opacity = '0';
                setTimeout(() => {
                    if (this.currentState !== this.STATES.PLAYBACK) {
                        videoContainer.style.display = 'none';
                        if (video) {
                            video.pause();
                            video.currentTime = 0;
                        }
                    }
                }, this.config.logoFadeOutDuration);
            }
        }

        // Handle screen sleep state
        if (newState === this.STATES.SCREEN_SLEEP) {
            // Add screen-sleep class to body
            document.body.classList.add('screen-sleep');
            
            // Hide all UI elements
            if (clockDisplay) {
                clockDisplay.style.transition = `opacity ${this.config.screenSleepFadeOutDuration}ms ease-out`;
                clockDisplay.style.opacity = '0';
                setTimeout(() => {
                    if (this.currentState === this.STATES.SCREEN_SLEEP) {
                        clockDisplay.style.display = 'none';
                    }
                }, this.config.screenSleepFadeOutDuration);
            }
            
            // Clean up clock to save resources
            if (window.Clock && window.Clock.cleanup) {
                window.Clock.cleanup();
            }
        } else if (this.currentState === this.STATES.SCREEN_SLEEP && newState === this.STATES.CLOCK) {
            // Wake from sleep
            document.body.classList.remove('screen-sleep');
            
            // Reinitialize clock
            if (clockDisplay) {
                clockDisplay.style.display = 'block';
                clockDisplay.style.transition = `opacity ${this.config.screenWakeFadeInDuration}ms ease-out`;
                // Force reflow
                clockDisplay.offsetHeight;
                clockDisplay.style.opacity = '1';
                
                if (window.Clock && !window.Clock.clockInterval) {
                    window.Clock.init();
                }
            }
        }
        
        // Handle clock display
        if (clockDisplay) {
            console.log(`Handling clock display for state: ${newState}`);
            if (newState === this.STATES.CLOCK && this.currentState !== this.STATES.SCREEN_SLEEP) {
                // Fade in clock
                clockDisplay.style.transition = `opacity ${this.config.clockFadeInDuration}ms ease-out`;
                clockDisplay.style.display = 'block';
                // Force reflow
                clockDisplay.offsetHeight;
                clockDisplay.style.opacity = '1';
                clockDisplay.style.zIndex = '10'; // Below video when playing

                // Initialize clock if needed
                if (window.Clock && !window.Clock.clockInterval) {
                    window.Clock.init();
                }
            } else if (this.currentState === this.STATES.CLOCK && newState !== this.STATES.SCREEN_SLEEP) {
                // Fade out clock
                clockDisplay.style.transition = `opacity ${this.config.clockFadeOutDuration}ms ease-out`;
                clockDisplay.style.opacity = '0';
                setTimeout(() => {
                    if (this.currentState !== this.STATES.CLOCK) {
                        clockDisplay.style.display = 'none';
                    }
                }, this.config.clockFadeOutDuration);
            }
        }
    },

    // Update the status display
    updateStatus() {
        const statusDiv = document.getElementById('status');
        if (!statusDiv) return;
        let statusText = `${this.currentState.charAt(0).toUpperCase() + this.currentState.slice(1)}`;
        
        if (this.currentState === this.STATES.ERROR && this.error) {
            statusText += ` - ${this.error}`;
        }
        
        statusDiv.textContent = statusText;
    },

    // Play latest video
    playLatestVideo() {
        console.log('Playing latest video');
        // Request the latest video from server
        if (window.socket) {
            window.socket.emit('show_previous_dream');
            this.updateState(this.STATES.PLAYBACK);
        }
    },

    // Play previous video
    playPreviousVideo() {
        console.log('Playing previous video');
        // Request the previous video from server
        if (window.socket) {
            window.socket.emit('show_previous_dream');
            this.updateState(this.STATES.PLAYBACK);
        }
    },

    // Handle recording start
    startRecording() {
        if (this.currentState === this.STATES.RECORDING) {
            console.log(`Already recording`);
            return;
        }

        this.updateState(this.STATES.RECORDING);
        
        if (window.startRecording) {
            window.startRecording();
        }
    },

    // Handle recording stop
    stopRecording() {
        if (this.currentState !== this.STATES.RECORDING) {
            console.log(`Cannot stop recording in ${this.currentState} state`);
            return;
        }

        this.updateState(this.STATES.PROCESSING);
        
        if (window.stopRecording) {
            window.stopRecording();
        }
    },

    // Stop playback
    stopPlayback() {
        if (this.playbackTimer) {
            clearTimeout(this.playbackTimer);
            this.playbackTimer = null;
        }
        
        // Reset server playback state
        if (window.socket) {
            window.socket.emit("reset_playback_state");
        }
    },

    // Handle device events based on mode
    handleDeviceEvent(eventType) {
        console.log(`Handling device event: ${eventType}`);
        console.log(`Current state: ${this.currentState}`);
        
        switch (eventType) {
            case 'single_tap':
                if (this.currentState === this.STATES.RECORDING) {
                    // Any tap during recording stops it
                    this.stopRecording();
                } else if (this.currentState === this.STATES.PLAYBACK) {
                    // Single tap during playback shows previous video
                    this.playPreviousVideo();
                } else if (this.currentState === this.STATES.CLOCK) {
                    // Single tap in clock state plays most recent video
                    this.playLatestVideo();
                } else if (this.currentState === this.STATES.ERROR) {
                    // Hide errorDiv and return to clock
                    if (window.errorDiv) {
                        window.errorDiv.style.display = 'none';
                    }
                    this.updateState(this.STATES.CLOCK);
                } else if (this.currentState === this.STATES.SCREEN_SLEEP) {
                    // Single tap in sleep state wakes to clock
                    this.updateState(this.STATES.CLOCK);
                }
                break;
                
            case 'double_tap':
                if (this.currentState === this.STATES.CLOCK) {
                    // Double tap in clock state starts recording
                    this.startRecording();
                } else if (this.currentState === this.STATES.PLAYBACK) {
                    // Double tap in playback state stops playback and goes to clock
                    this.stopPlayback();
                    this.updateState(this.STATES.CLOCK);
                } else if (this.currentState === this.STATES.SCREEN_SLEEP) {
                    // Double tap in sleep state wakes and starts recording
                    this.updateState(this.STATES.CLOCK);
                    setTimeout(() => {
                        this.startRecording();
                    }, this.config.screenWakeFadeInDuration);
                } else if (this.currentState === this.STATES.RECORDING) {
                    // Double tap during recording cancels and returns to clock
                    if (window.stopRecording) {
                        window.stopRecording();
                    }
                    this.updateState(this.STATES.CLOCK);
                }
                break;
                
            case 'long_tap':
                if (this.currentState === this.STATES.CLOCK) {
                    // Long tap in clock state enters sleep mode
                    this.updateState(this.STATES.SCREEN_SLEEP);
                }
                break;
                
            default:
                console.log(`Unhandled event type: ${eventType}`);
        }
    },

    // Register a callback for state changes
    registerStateChangeCallback(callback) {
        this.stateChangeCallbacks.push(callback);
    }
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    StateManager.init();
});

// Make StateManager globally accessible
window.StateManager = StateManager;
