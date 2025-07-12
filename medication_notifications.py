
from datetime import date, timedelta
from flask import current_app
from flask_mail import Message
import logging

def check_and_send_medication_alerts(db, mail, Medication, Document, Resident):
    try:
    """
    Check for expiring medications and documents, send alerts only when appropriate.
    Tracks sent notifications to prevent duplicates.
    """
    today = date.today()
    seven_days_out = today + timedelta(days=7)
    alerts = []
    
    try:
        # Check medications
        medications = Medication.query.all()
        for med in medications:
            if not med.expiration_date:
                continue
                
            resident = Resident.query.get(med.resident_id)
            if not resident:
                continue
                
            # Create unique alert key
            alert_key = f"med_{med.id}_{med.expiration_date}"
            
            if med.expiration_date == today:
                # Medication expires today
                if not has_alert_been_sent(db, alert_key, 'expiry'):
                    send_medication_alert(mail, resident.name, med.name, med.expiration_date, 'expired')
                    mark_alert_as_sent(db, alert_key, 'expiry')
                    alerts.append(f"EXPIRED: Medication {med.name} for {resident.name} expired today")
                else:
                    alerts.append(f"Expired medication: {med.name} for {resident.name}")
                    
            elif med.expiration_date == seven_days_out:
                # Medication expires in 7 days
                if not has_alert_been_sent(db, alert_key, '7day'):
                    send_medication_alert(mail, resident.name, med.name, med.expiration_date, '7-day warning')
                    mark_alert_as_sent(db, alert_key, '7day')
                    alerts.append(f"7-DAY WARNING: Medication {med.name} for {resident.name} expires on {med.expiration_date}")
                else:
                    alerts.append(f"Medication expiring soon: {med.name} for {resident.name} (expires {med.expiration_date})")
                    
            elif med.expiration_date < today:
                # Already expired - send one-time notification
                if not has_alert_been_sent(db, alert_key, 'expired_notification'):
                    send_medication_alert(mail, resident.name, med.name, med.expiration_date, 'overdue')
                    mark_alert_as_sent(db, alert_key, 'expired_notification')
                    alerts.append(f"OVERDUE: Medication {med.name} for {resident.name} expired on {med.expiration_date}")
                else:
                    alerts.append(f"Expired medication: {med.name} for {resident.name}")
                    
            elif med.expiration_date <= seven_days_out:
                # Expiring within 7 days (but not exactly 7 days)
                alerts.append(f"Medication expiring soon: {med.name} for {resident.name} (expires {med.expiration_date})")
        
        # Check documents
        documents = Document.query.all()
        for doc in documents:
            if not doc.expiration_date:
                continue
                
            resident = Resident.query.get(doc.resident_id)
            if not resident:
                continue
                
            alert_key = f"doc_{doc.id}_{doc.expiration_date}"
            
            if doc.expiration_date == today:
                # Document expires today
                if not has_alert_been_sent(db, alert_key, 'expiry'):
                    send_document_alert(mail, resident.name, doc.name, doc.expiration_date, 'expired')
                    mark_alert_as_sent(db, alert_key, 'expiry')
                    alerts.append(f"EXPIRED: Document {doc.name} for {resident.name} expired today")
                else:
                    alerts.append(f"Expired document: {doc.name} for {resident.name}")
                    
            elif doc.expiration_date == seven_days_out:
                # Document expires in 7 days
                if not has_alert_been_sent(db, alert_key, '7day'):
                    send_document_alert(mail, resident.name, doc.name, doc.expiration_date, '7-day warning')
                    mark_alert_as_sent(db, alert_key, '7day')
                    alerts.append(f"7-DAY WARNING: Document {doc.name} for {resident.name} expires on {doc.expiration_date}")
                else:
                    alerts.append(f"Document expiring soon: {doc.name} for {resident.name} (expires {doc.expiration_date})")
                    
            elif doc.expiration_date < today:
                # Already expired
                if not has_alert_been_sent(db, alert_key, 'expired_notification'):
                    send_document_alert(mail, resident.name, doc.name, doc.expiration_date, 'overdue')
                    mark_alert_as_sent(db, alert_key, 'expired_notification')
                    alerts.append(f"OVERDUE: Document {doc.name} for {resident.name} expired on {doc.expiration_date}")
                else:
                    alerts.append(f"Expired document: {doc.name} for {resident.name}")
                    
            elif doc.expiration_date <= seven_days_out:
                # Expiring within 7 days
                alerts.append(f"Document expiring soon: {doc.name} for {resident.name} (expires {doc.expiration_date})")
                
    except Exception as e:
        logging.error(f"Error checking medication alerts: {e}")
        
    return alerts
    except Exception as e:
        print(f"Error checking medication alerts: {e}")
        return []

def has_alert_been_sent(db, alert_key, alert_type):
    """Check if an alert has already been sent"""
    from app import NotificationLog  # Import here to avoid circular imports
    
    try:
        log = NotificationLog.query.filter_by(
            alert_key=alert_key,
            alert_type=alert_type
        ).first()
        return log is not None
    except:
        # If table doesn't exist yet, assume not sent
        return False

def mark_alert_as_sent(db, alert_key, alert_type):
    """Mark an alert as sent"""
    from app import NotificationLog  # Import here to avoid circular imports
    
    try:
        log = NotificationLog(
            alert_key=alert_key,
            alert_type=alert_type,
            sent_date=date.today()
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error marking alert as sent: {e}")
        db.session.rollback()

def send_medication_alert(mail, resident_name, med_name, expiration_date, alert_type):
    """Send medication expiration alert email"""
    try:
        if alert_type == 'expired':
            subject = f"MEDICATION EXPIRED - {resident_name}"
            body = f"URGENT: Medication '{med_name}' for {resident_name} EXPIRED TODAY ({expiration_date}).\n\nPlease take immediate action to replace this medication."
        elif alert_type == '7-day warning':
            subject = f"Medication Expiring Soon - {resident_name}"
            body = f"REMINDER: Medication '{med_name}' for {resident_name} will expire in 7 days ({expiration_date}).\n\nPlease arrange for a replacement soon."
        elif alert_type == 'overdue':
            subject = f"OVERDUE MEDICATION - {resident_name}"
            body = f"WARNING: Medication '{med_name}' for {resident_name} expired on {expiration_date}.\n\nThis medication is overdue for replacement."
        
        msg = Message(subject, recipients=[current_app.config['MAIL_DEFAULT_SENDER']])
        msg.body = body
        mail.send(msg)
        logging.info(f"Sent {alert_type} alert for medication {med_name}")
    except Exception as e:
        logging.error(f"Failed to send medication alert: {e}")

def send_document_alert(mail, resident_name, doc_name, expiration_date, alert_type):
    """Send document expiration alert email"""
    try:
        if alert_type == 'expired':
            subject = f"DOCUMENT EXPIRED - {resident_name}"
            body = f"URGENT: Document '{doc_name}' for {resident_name} EXPIRED TODAY ({expiration_date}).\n\nPlease renew this document immediately."
        elif alert_type == '7-day warning':
            subject = f"Document Expiring Soon - {resident_name}"
            body = f"REMINDER: Document '{doc_name}' for {resident_name} will expire in 7 days ({expiration_date}).\n\nPlease arrange for renewal soon."
        elif alert_type == 'overdue':
            subject = f"OVERDUE DOCUMENT - {resident_name}"
            body = f"WARNING: Document '{doc_name}' for {resident_name} expired on {expiration_date}.\n\nThis document is overdue for renewal."
        
        msg = Message(subject, recipients=[current_app.config['MAIL_DEFAULT_SENDER']])
        msg.body = body
        mail.send(msg)
        logging.info(f"Sent {alert_type} alert for document {doc_name}")
    except Exception as e:
        logging.error(f"Failed to send document alert: {e}")
