
from datetime import date, timedelta
from flask_mail import Message
from models import db, Medication, Resident
import logging

def send_alert_email(mail, subject, body, sender_email):
    """Send alert email with error handling"""
    try:
        msg = Message(subject, recipients=[sender_email])
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        logging.error(f'Failed to send email: {str(e)}')
        return False

def check_medication_expiration_notifications(app, mail):
    """
    Check for medications that need expiration notifications.
    This should be called once per day, not on every page load.
    """
    with app.app_context():
        today = date.today()
        seven_days_from_now = today + timedelta(days=7)
        
        # Get all medications that have expiration dates
        medications = Medication.query.filter(Medication.expiration_date.isnot(None)).all()
        
        notifications_sent = []
        
        for med in medications:
            resident = Resident.query.get(med.resident_id)
            if not resident:
                continue
                
            # Skip if we already checked today
            if med.last_notification_check == today:
                continue
                
            notification_sent = False
            
            # Check for 7-day warning
            if (med.expiration_date == seven_days_from_now and 
                not med.seven_day_warning_sent):
                
                subject = f"Medication Expiring Soon - {resident.name}"
                body = (f"Medication Alert: {med.name} for {resident.name} "
                       f"will expire in 7 days on {med.expiration_date}.\n\n"
                       f"Dosage: {med.dosage or 'N/A'}\n"
                       f"Frequency: {med.frequency or 'N/A'}\n"
                       f"Please ensure renewal or replacement.")
                
                if send_alert_email(mail, subject, body, app.config['MAIL_DEFAULT_SENDER']):
                    med.seven_day_warning_sent = True
                    notification_sent = True
                    notifications_sent.append(f"7-day warning: {med.name} for {resident.name}")
            
            # Check for expiration day notification
            elif (med.expiration_date == today and 
                  not med.expiration_notification_sent):
                
                subject = f"Medication Expired Today - {resident.name}"
                body = (f"Medication Alert: {med.name} for {resident.name} "
                       f"expired today ({med.expiration_date}).\n\n"
                       f"Dosage: {med.dosage or 'N/A'}\n"
                       f"Frequency: {med.frequency or 'N/A'}\n"
                       f"Immediate action required - medication should not be administered.")
                
                if send_alert_email(mail, subject, body, app.config['MAIL_DEFAULT_SENDER']):
                    med.expiration_notification_sent = True
                    notification_sent = True
                    notifications_sent.append(f"Expiration day: {med.name} for {resident.name}")
            
            # Check for already expired medications (catch missed notifications)
            elif (med.expiration_date < today and 
                  not med.expired_notification_sent):
                
                days_expired = (today - med.expiration_date).days
                subject = f"Expired Medication Detected - {resident.name}"
                body = (f"Medication Alert: {med.name} for {resident.name} "
                       f"expired {days_expired} day(s) ago on {med.expiration_date}.\n\n"
                       f"Dosage: {med.dosage or 'N/A'}\n"
                       f"Frequency: {med.frequency or 'N/A'}\n"
                       f"This medication should not be administered. Please review and update.")
                
                if send_alert_email(mail, subject, body, app.config['MAIL_DEFAULT_SENDER']):
                    med.expired_notification_sent = True
                    notification_sent = True
                    notifications_sent.append(f"Expired medication: {med.name} for {resident.name}")
            
            # Update the last notification check date
            if notification_sent or med.last_notification_check != today:
                med.last_notification_check = today
        
        # Commit all changes
        if notifications_sent:
            db.session.commit()
            logging.info(f"Medication notifications sent: {notifications_sent}")
        
        return notifications_sent

def get_medication_alerts_for_display():
    """
    Get medication alerts for display on the homepage without sending emails.
    Returns alerts that should be shown to users.
    """
    today = date.today()
    soon_expire_days = 7
    soon_expire_date = today + timedelta(days=soon_expire_days)
    
    alerts = []
    
    # Get medications with expiration dates
    medications = Medication.query.filter(Medication.expiration_date.isnot(None)).all()
    
    for med in medications:
        resident = Resident.query.get(med.resident_id)
        if not resident:
            continue
            
        if med.expiration_date < today:
            alerts.append({
                'type': 'expired',
                'message': f"Expired medication: {med.name} for {resident.name}",
                'severity': 'danger'
            })
        elif med.expiration_date <= soon_expire_date:
            alerts.append({
                'type': 'expiring',
                'message': f"Medication expiring soon: {med.name} for {resident.name} (expires {med.expiration_date})",
                'severity': 'warning'
            })
    
    return alerts
