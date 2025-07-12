
from datetime import date, timedelta
from flask_mail import Message
from models import db, Medication, MedicationNotification, Resident

def check_medication_expiry(mail, app_config):
    """Check for expiring medications and send notifications if needed"""
    today = date.today()
    seven_days_from_now = today + timedelta(days=7)
    
    medications = Medication.query.filter(Medication.expiration_date.isnot(None)).all()
    
    for med in medications:
        resident = Resident.query.get(med.resident_id)
        if not resident:
            continue
            
        # Check if medication is expired and we haven't sent expired notification
        if med.expiration_date < today:
            if not MedicationNotification.query.filter_by(
                medication_id=med.id, 
                notification_type='expired'
            ).first():
                send_expiry_email(med, resident, 'expired', mail, app_config)
                log_notification(med.id, 'expired')
                
        # Check if medication expires exactly 7 days from now
        elif med.expiration_date == seven_days_from_now:
            if not MedicationNotification.query.filter_by(
                medication_id=med.id, 
                notification_type='7_day_warning'
            ).first():
                send_expiry_email(med, resident, '7_day_warning', mail, app_config)
                log_notification(med.id, '7_day_warning')
                
        # Check if medication expires today
        elif med.expiration_date == today:
            if not MedicationNotification.query.filter_by(
                medication_id=med.id, 
                notification_type='expiration_day'
            ).first():
                send_expiry_email(med, resident, 'expiration_day', mail, app_config)
                log_notification(med.id, 'expiration_day')

def send_expiry_email(medication, resident, notification_type, mail, app_config):
    """Send medication expiry email notification"""
    try:
        if notification_type == '7_day_warning':
            subject = f"Medication Expiring Soon - {resident.name}"
            body = f"The medication '{medication.name}' for {resident.name} will expire in 7 days on {medication.expiration_date}."
        elif notification_type == 'expiration_day':
            subject = f"Medication Expires Today - {resident.name}"
            body = f"The medication '{medication.name}' for {resident.name} expires today ({medication.expiration_date})."
        elif notification_type == 'expired':
            subject = f"Expired Medication - {resident.name}"
            body = f"The medication '{medication.name}' for {resident.name} expired on {medication.expiration_date}."
        else:
            return
            
        msg = Message(subject, recipients=[app_config['MAIL_DEFAULT_SENDER']])
        msg.body = body
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send medication expiry email: {str(e)}")

def log_notification(medication_id, notification_type):
    """Log that a notification was sent"""
    notification = MedicationNotification(
        medication_id=medication_id,
        notification_type=notification_type,
        sent_date=date.today()
    )
    db.session.add(notification)
    db.session.commit()
