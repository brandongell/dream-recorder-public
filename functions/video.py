import tempfile
import time
import os
import ffmpeg
import shutil
from datetime import datetime
from functions.config_loader import get_config

try:
    from google import genai
except ImportError:
    print("Warning: google-genai not installed. Run: pip install google-genai")
    genai = None

def process_video(input_path, logger=None):
    """Process the video using FFmpeg with specific filters from environment variables."""
    try:
        # Create a temporary file for the processed video
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_path = temp_file.name
        # Apply FFmpeg filters using environment variables
        stream = ffmpeg.input(input_path)
        # Only vibrance and noise filters are active
        # 1. Base color enhancement
        stream = ffmpeg.filter(stream, 'vibrance', intensity=float(get_config()['FFMPEG_VIBRANCE']))
        
        # 2. Chromatic aberration - subtle color fringing for dreamlike quality
        stream = ffmpeg.filter(stream, 'rgbashift', rh=1, gv=-1, bh=1, bv=0)
        
        # 3. Motion trails - creates ghosting effect for ethereal movement
        # stream = ffmpeg.filter(stream, 'lagfun', decay=0.5)  # Disabled - motion trails too distracting
        
        # 4. Hue cycling - gentle color breathing over time
        stream = ffmpeg.filter(stream, 'hue', s=1.1, h='3*sin(t/3)')
        
        # 5. Vignette - darkens edges for focus and dream-like tunnel vision
        stream = ffmpeg.filter(stream, 'vignette', angle='PI/4')
        
        # 6. Dreamy softness - selective blur for that hazy dream quality
        # stream = ffmpeg.filter(stream, 'unsharp', luma_msize_x=5, luma_msize_y=5, luma_amount=-0.5)  # Disabled - too soft
        
        # 7. Film grain - adds texture (keep last to preserve grain quality)
        stream = ffmpeg.filter(stream, 'noise', all_strength=float(get_config()['FFMPEG_NOISE_STRENGTH']))
        stream = ffmpeg.output(stream, temp_path)
        # Run FFmpeg
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
        # Replace the original file with the processed one
        shutil.move(temp_path, input_path)
        if logger:
            logger.info(f"Processed video saved to {input_path}")
        return input_path
    except Exception as e:
        if logger:
            logger.error(f"Error processing video: {str(e)}")
        raise

def process_thumbnail(video_path, logger=None):
    """Create a square thumbnail from the video at 1 second in."""
    try:
        # Get video dimensions using ffprobe
        probe = ffmpeg.probe(video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        width = int(video_info['width'])
        height = int(video_info['height'])
        # Calculate square crop dimensions based on the smaller dimension
        crop_size = min(width, height)
        # Calculate offsets to center the crop
        x_offset = (width - crop_size) // 2
        y_offset = (height - crop_size) // 2
        # Create output directory if it doesn't exist
        thumbs_dir = get_config()['THUMBS_DIR']
        os.makedirs(thumbs_dir, exist_ok=True)
        # Generate simple timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        thumb_filename = f"thumb_{timestamp}.png"
        thumb_path = os.path.join(thumbs_dir, thumb_filename)
        # Log the FFmpeg command for debugging
        if logger:
            logger.info(f"Generating thumbnail for video: {video_path}")
            logger.info(f"Video dimensions: {width}x{height}")
            logger.info(f"Output path: {thumb_path}")
            logger.info(f"Crop dimensions: {crop_size}x{crop_size} at offset ({x_offset}, {y_offset})")
        # Use FFmpeg to extract frame at 1 second and crop to square
        stream = ffmpeg.input(video_path, ss=1)
        stream = ffmpeg.filter(stream, 'crop', crop_size, crop_size, x_offset, y_offset)
        stream = ffmpeg.output(stream, thumb_path, vframes=1)
        # Run FFmpeg with stderr capture
        try:
            ffmpeg.run(stream, overwrite_output=True, capture_stderr=True)
        except ffmpeg.Error as e:
            if logger:
                logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise
        if logger:
            logger.info(f"Generated thumbnail saved to {thumb_path}")
        return thumb_filename
    except Exception as e:
        if logger:
            logger.error(f"Error generating thumbnail: {str(e)}")
        raise

def generate_video(prompt, filename=None, logger=None, config=None):
    """Generate a video using Google's VEO 3 API."""
    try:
        if genai is None:
            raise Exception("google-genai library not installed")
            
        # Initialize the client with API key
        client = genai.Client(api_key=get_config()['GOOGLE_AI_API_KEY'])
        
        # Create video generation request
        if logger:
            logger.info(f"Starting VEO 3 video generation with prompt: {prompt[:100]}...")
            
        operation = client.models.generate_videos(
            model=get_config()['VEO3_MODEL'],
            prompt=prompt,
        )
        
        if logger:
            logger.info(f"Video generation operation started: {operation.name}")
        
        # Poll for completion
        max_attempts = int(get_config()['VEO3_MAX_POLL_ATTEMPTS'])
        poll_interval = float(get_config()['VEO3_POLL_INTERVAL'])
        
        for attempt in range(max_attempts):
            # Check if done (operation.done might be None initially)
            if operation.done is True:
                break
                
            if logger:
                logger.info(f"Waiting for video generation... (attempt {attempt+1}/{max_attempts})")
                
            time.sleep(poll_interval)
            
            # Poll by getting a fresh operation object
            operation = client.operations.get(operation)
            
        if operation.done is not True:
            raise Exception(f"Video generation timed out after {max_attempts} attempts")
            
        # Check for errors
        if operation.error:
            raise Exception(f"Video generation failed: {operation.error}")
            
        # Get the generated video
        if not operation.response or not operation.response.generated_videos:
            raise Exception("No video was generated")
            
        generated_video = operation.response.generated_videos[0]
        
        # Download the video
        if logger:
            logger.info("Downloading generated video...")
            
        # Create filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generated_{timestamp}.mp4"
            
        os.makedirs(get_config()['VIDEOS_DIR'], exist_ok=True)
        video_path = os.path.join(get_config()['VIDEOS_DIR'], filename)
        
        # Download and save the video
        client.files.download(file=generated_video.video)
        generated_video.video.save(video_path)
        
        if logger:
            logger.info(f"Saved video to {video_path}")
            
        # Post-process the video
        processed_video_path = process_video(video_path, logger)
        if logger:
            logger.info(f"Processed video saved to {processed_video_path}")
            
        # Generate thumbnail
        thumb_filename = process_thumbnail(processed_video_path, logger)
        
        return filename, thumb_filename
        
    except Exception as e:
        if logger:
            logger.error(f"Error generating video: {str(e)}")
        raise
