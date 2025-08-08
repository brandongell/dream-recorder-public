import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EmailNotifier:
    def __init__(self, config):
        self.enabled = config.get('EMAIL_NOTIFICATIONS_ENABLED', False)
        self.smtp_server = config.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = config.get('SMTP_PORT', 587)
        self.smtp_username = config.get('SMTP_USERNAME', '')
        self.smtp_password = config.get('SMTP_PASSWORD', '')
        self.from_email = config.get('FROM_EMAIL', '')
        self.to_emails = config.get('TO_EMAILS', [])
        self.dream_base_url = config.get('DREAM_BASE_URL', 'http://localhost:5000')
        
    def send_dream_notification(self, dream_data):
        """Send email notification for a new dream"""
        if not self.enabled:
            logger.info("Email notifications are disabled")
            return False
            
        if not all([self.smtp_username, self.smtp_password, self.from_email, self.to_emails]):
            logger.error("Email configuration is incomplete")
            return False
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"New Dream Recorded - {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails) if isinstance(self.to_emails, list) else self.to_emails
            
            # Create the body of the message
            dream_id = dream_data.get('id', 'unknown')
            transcription = dream_data.get('transcription', 'No transcription available')
            video_filename = dream_data.get('video_filename', '')
            
            # Plain text version
            text = f"""
A new dream has been recorded!

Transcription: {transcription}

View the dream: {self.dream_base_url}/dreams#{dream_id}
Direct video link: {self.dream_base_url}/media/video/{video_filename}

Dream ID: {dream_id}
Recorded: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
"""
            
            # HTML version
            html = f"""
<html>
  <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #4a5568;">🌙 New Dream Recorded</h2>
    
    <div style="background-color: #f7fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
      <h3 style="color: #2d3748; margin-top: 0;">Transcription:</h3>
      <p style="color: #4a5568; line-height: 1.6;">{transcription}</p>
    </div>
    
    <div style="margin: 30px 0;">
      <a href="{self.dream_base_url}/dreams#{dream_id}" 
         style="background-color: #4299e1; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
        View Dream in Library
      </a>
    </div>
    
    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #718096; font-size: 14px;">
      <p>Dream ID: {dream_id}</p>
      <p>Recorded: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
      <p><a href="{self.dream_base_url}/media/video/{video_filename}" style="color: #4299e1;">Direct video link</a></p>
    </div>
  </body>
</html>
"""
            
            # Attach parts
            part1 = MIMEText(text, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send the message
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                
                # Handle both string and list of recipients
                recipients = self.to_emails if isinstance(self.to_emails, list) else [self.to_emails]
                server.send_message(msg, from_addr=self.from_email, to_addrs=recipients)
                
            logger.info(f"Email notification sent successfully for dream {dream_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False
