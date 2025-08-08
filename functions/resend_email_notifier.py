import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ResendEmailNotifier:
    def __init__(self, config):
        self.enabled = config.get('EMAIL_NOTIFICATIONS_ENABLED', False)
        self.api_key = config.get('RESEND_API_KEY', '')
        self.from_email = config.get('FROM_EMAIL', 'dreams@[YOUR-DOMAIN]')
        self.to_emails = config.get('TO_EMAILS', [])
        self.dream_base_url = config.get('DREAM_BASE_URL', 'https://dreams.[YOUR-DOMAIN]')
        
    def send_dream_notification(self, dream_data):
        """Send email notification using Resend API"""
        if not self.enabled:
            logger.info("Email notifications are disabled")
            return False
            
        if not self.api_key:
            logger.error("Resend API key not configured")
            return False
            
        try:
            dream_id = dream_data.get('id', 'unknown')
            transcription = dream_data.get('transcription', 'No transcription available')
            video_filename = dream_data.get('video_filename', '')
            timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
            
            # HTML email content
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #4a5568;">🌙 New Dream Recorded</h2>
                <p style="color: #718096;">Recorded on {timestamp}</p>
                
                <div style="background: #f7fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2d3748; margin-top: 0;">Dream Transcription:</h3>
                    <p style="color: #4a5568; line-height: 1.6;">{transcription}</p>
                </div>
                
                <a href="{self.dream_base_url}/dreams#{dream_id}" 
                   style="display: inline-block; background: #4299e1; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 6px; margin: 20px 0;">
                    View Dream
                </a>
                
                <p style="color: #718096; font-size: 14px;">
                    Dream ID: {dream_id}<br>
                    Direct link: {self.dream_base_url}/media/video/{video_filename}
                </p>
            </div>
            """
            
            # Send via Resend API
            response = requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'from': self.from_email,
                    'to': self.to_emails,
                    'subject': f'New Dream - {timestamp}',
                    'html': html_content
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Email sent successfully for dream {dream_id}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
