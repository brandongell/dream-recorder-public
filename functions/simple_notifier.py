import json
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleNotifier:
    def __init__(self, config):
        self.enabled = config.get('SIMPLE_NOTIFICATIONS_ENABLED', False)
        self.webhook_url = config.get('NOTIFICATION_WEBHOOK_URL', '')
        self.notification_method = config.get('NOTIFICATION_METHOD', 'webhook')  # webhook, ntfy, or pushover
        self.dream_base_url = config.get('DREAM_BASE_URL', 'https://dreams.[YOUR-DOMAIN]')
        
    def send_dream_notification(self, dream_data):
        """Send notification for a new dream using simple methods"""
        if not self.enabled:
            logger.info("Simple notifications are disabled")
            return False
            
        try:
            dream_id = dream_data.get('id', 'unknown')
            transcription = dream_data.get('transcription', 'No transcription available')
            video_filename = dream_data.get('video_filename', '')
            timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
            
            # Prepare notification content
            title = f"New Dream Recorded - {timestamp}"
            message = f"{transcription}\n\nView: {self.dream_base_url}/dreams#{dream_id}"
            
            if self.notification_method == 'ntfy':
                # ntfy.sh - simple push notifications (no email needed!)
                response = requests.post(
                    f"https://ntfy.sh/{self.webhook_url}",
                    data=message.encode('utf-8'),
                    headers={
                        "Title": title,
                        "Priority": "default",
                        "Tags": "moon,sparkles",
                        "Click": f"{self.dream_base_url}/dreams#{dream_id}"
                    }
                )
                logger.info(f"Sent ntfy notification: {response.status_code}")
                return response.status_code == 200
                
            elif self.notification_method == 'webhook':
                # Generic webhook (Discord, Slack, Make.com, Zapier, etc.)
                payload = {
                    "title": title,
                    "description": transcription,
                    "url": f"{self.dream_base_url}/dreams#{dream_id}",
                    "video_url": f"{self.dream_base_url}/media/video/{video_filename}",
                    "timestamp": timestamp,
                    "dream_id": dream_id
                }
                
                response = requests.post(self.webhook_url, json=payload)
                logger.info(f"Sent webhook notification: {response.status_code}")
                return response.status_code < 300
                
            elif self.notification_method == 'pushover':
                # Pushover - simple mobile notifications
                response = requests.post(
                    "https://api.pushover.net/1/messages.json",
                    data={
                        "token": self.webhook_url.split(':')[0],  # app token
                        "user": self.webhook_url.split(':')[1],   # user key
                        "title": title,
                        "message": message,
                        "url": f"{self.dream_base_url}/dreams#{dream_id}",
                        "url_title": "View Dream"
                    }
                )
                logger.info(f"Sent Pushover notification: {response.status_code}")
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False
