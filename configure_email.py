#!/usr/bin/env python3
import json

# EDIT THESE VALUES WITH YOUR INFORMATION
EMAIL_CONFIG = {
    "EMAIL_NOTIFICATIONS_ENABLED": True,
    
    # For Gmail, use these settings:
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": 587,
    
    # Your email credentials
    "SMTP_USERNAME": "your.email@gmail.com",  # <-- CHANGE THIS
    "SMTP_PASSWORD": "your-app-password-here", # <-- CHANGE THIS (16-char app password)
    "FROM_EMAIL": "your.email@gmail.com",      # <-- CHANGE THIS (usually same as username)
    
    # Who should receive notifications (can be multiple)
    "TO_EMAILS": ["recipient@example.com"],    # <-- CHANGE THIS
    
    # Your Dream Recorder URL (already configured)
    "DREAM_BASE_URL": "https://dreams.[YOUR-DOMAIN]"
}

# Don't edit below this line
print("Configuring email notifications...")

# Read current config
with open('config.json', 'r') as f:
    config = json.load(f)

# Update with email settings
config.update(EMAIL_CONFIG)

# Save updated config
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("\n✅ Email configuration saved!")
print(f"\nEmail notifications will be sent from: {EMAIL_CONFIG['FROM_EMAIL']}")
print("To the following recipients:")
for email in EMAIL_CONFIG['TO_EMAILS']:
    print(f"  - {email}")
print(f"\nDreams will link to: {EMAIL_CONFIG['DREAM_BASE_URL']}/dreams")
print("\nRestart the service to apply changes:")
print("  sudo systemctl restart dream-recorder")
