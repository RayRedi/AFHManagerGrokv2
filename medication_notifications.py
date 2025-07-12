from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_send_medication_alerts():
    """Check for medications that need alerts and send notifications"""
    try:
        # Database connection
        engine = create_engine('sqlite:///afh.db')

        # Get current time
        now = datetime.now()

        # Query for medications that need alerts
        with engine.connect() as conn:
            # Check for medications expiring soon (within 7 days)
            expiring_query = text("""
                SELECT m.name, m.expiration_date, r.name as resident_name
                FROM medication m
                JOIN resident r ON m.resident_id = r.id
                WHERE m.expiration_date <= :expiry_date
                AND m.expiration_date >= :today
            """)

            expiry_date = (now + timedelta(days=7)).date()
            expiring_meds = conn.execute(expiring_query, {
                'expiry_date': expiry_date,
                'today': now.date()
            }).fetchall()

            if expiring_meds:
                send_expiration_alerts(expiring_meds)

    except Exception as e:
        logger.error(f"Error checking medication alerts: {e}")

def send_expiration_alerts(medications):
    """Send email alerts for expiring medications"""
    try:
        # Email configuration (you'll need to set these up)
        smtp_server = "smtp.gmail.com"  # Update with your SMTP server
        smtp_port = 587
        sender_email = "your-email@gmail.com"  # Update with your email
        sender_password = "your-password"  # Update with your password
        recipient_email = "admin@afh.com"  # Update with admin email

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "Medication Expiration Alert"

        # Create message body
        body = "The following medications are expiring soon:\n\n"
        for med in medications:
            body += f"- {med.name} for {med.resident_name} (expires: {med.expiration_date})\n"

        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()

        logger.info(f"Sent expiration alert for {len(medications)} medications")

    except Exception as e:
        logger.error(f"Error sending email alert: {e}")