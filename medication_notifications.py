from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_and_send_medication_alerts(db, mail, Medication, Document, Resident):
    """Check for medications that need alerts and send notifications"""
    try:
        from datetime import date
        today = date.today()
        seven_days_later = today + timedelta(days=7)
        
        # Check for medications expiring within 7 days
        expiring_medications = Medication.query.filter(
            Medication.expiration_date <= seven_days_later,
            Medication.expiration_date >= today
        ).all()
        
        # Check for expired documents
        expired_documents = Document.query.filter(
            Document.expiration_date < today
        ).all()
        
        alerts = []
        
        # Add medication alerts
        for med in expiring_medications:
            resident = Resident.query.get(med.resident_id)
            days_until_expiry = (med.expiration_date - today).days
            if days_until_expiry == 0:
                alert_text = f"{med.name} for {resident.name} expires today"
            else:
                alert_text = f"{med.name} for {resident.name} expires in {days_until_expiry} days"
            alerts.append(alert_text)
        
        # Add document alerts
        for doc in expired_documents:
            resident = Resident.query.get(doc.resident_id)
            days_expired = (today - doc.expiration_date).days
            alert_text = f"Document '{doc.name}' for {resident.name} expired {days_expired} days ago"
            alerts.append(alert_text)
        
        return alerts

        except Exception as e:
        logger.error(f"Error checking medication alerts: {e}")
        return []

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