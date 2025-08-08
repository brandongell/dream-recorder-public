# Email Setup Guide for Dream Recorder

## Required Information:

1. **Email Provider** - Choose one:
   - Gmail (recommended)
   - Outlook
   - Yahoo
   - Custom SMTP

2. **Email Credentials**:
   - Your email address (e.g., your.email@gmail.com)
   - App Password (NOT your regular password)

3. **Recipients**:
   - Email addresses to receive notifications

## For Gmail Users:

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification (if not already enabled)
3. Go to https://myaccount.google.com/apppasswords
4. Select "Mail" and your device
5. Generate an app password
6. Copy the 16-character password

## For Outlook Users:

1. Go to https://account.microsoft.com/security
2. Enable two-step verification
3. Create an app password
4. Use smtp-mail.outlook.com as the server

## For Yahoo Users:

1. Go to Yahoo Account Security
2. Generate an app password
3. Use smtp.mail.yahoo.com as the server

Once you have your app password, run:
./setup_email.py

And follow the prompts!
