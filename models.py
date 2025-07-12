
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TypeDecorator, Text
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from cryptography.fernet import Fernet
import os

# Initialize encryption
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key().decode()
cipher = Fernet(ENCRYPTION_KEY.encode())

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Custom SQLAlchemy type for encrypted fields
class EncryptedText(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return cipher.encrypt(value.encode()).decode()

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return cipher.decrypt(value.encode()).decode()

class Resident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(EncryptedText, nullable=False)
    _dob = db.Column(EncryptedText, nullable=False)
    _medical_info = db.Column(EncryptedText)
    _emergency_contact = db.Column(EncryptedText)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def dob(self):
        if self._dob:
            try:
                return datetime.strptime(self._dob, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return None
        return None

    @dob.setter
    def dob(self, value):
        if value:
            if isinstance(value, str):
                self._dob = value
            else:
                self._dob = value.strftime('%Y-%m-%d')
        else:
            self._dob = None

    @property
    def medical_info(self):
        return self._medical_info

    @medical_info.setter
    def medical_info(self, value):
        self._medical_info = value

    @property
    def emergency_contact(self):
        return self._emergency_contact

    @emergency_contact.setter
    def emergency_contact(self, value):
        self._emergency_contact = value

    @property
    def formatted_dob(self):
        """Return DOB in 'Month Day, Year' format"""
        if self.dob:
            return self.dob.strftime('%B %d, %Y')
        return None

class Vitals(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # 'breakfast'
    systolic = db.Column(db.Integer, nullable=False)
    diastolic = db.Column(db.Integer, nullable=False)
    pulse = db.Column(db.Integer, nullable=False)

class FoodIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # 'breakfast', 'lunch', 'dinner'
    intake_level = db.Column(db.String(20), nullable=False)  # '25%', '50%', '75%', '100%', 'Ensure', 'Other'
    _notes = db.Column(EncryptedText)  # Encrypted notes for 'Other'

    @hybrid_property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, value):
        self._notes = value

class LiquidIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # 'breakfast', 'lunch', 'dinner'
    intake = db.Column(db.String(20), nullable=False)  # 'Yes', 'No', 'Partial'

class BowelMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # 'breakfast', 'lunch', 'dinner'
    size = db.Column(db.String(20), nullable=False)  # 'Small', 'Medium', 'Large'
    consistency = db.Column(db.String(20), nullable=False)  # 'Soft', 'Medium', 'Hard'

class UrineOutput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)  # 'breakfast', 'lunch', 'dinner'
    output = db.Column(db.String(20), nullable=False)  # 'Yes', 'No'

class IncidentReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer, db.ForeignKey('resident.id'), nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    _description = db.Column(EncryptedText, nullable=False)
    _immediate_action = db.Column(EncryptedText)
    injury_occurred = db.Column(db.String(3), nullable=False)
    medical_attention = db.Column(db.String(3), nullable=False)
    _witnesses = db.Column(EncryptedText)
    follow_up_required = db.Column(db.String(3), nullable=False)
    _follow_up_notes = db.Column(EncryptedText)
    date_reported = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reported_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='open')  # 'open', 'in_progress', 'closed'

    @hybrid_property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @hybrid_property
    def immediate_action(self):
        return self._immediate_action

    @immediate_action.setter
    def immediate_action(self, value):
        self._immediate_action = value

    @hybrid_property
    def witnesses(self):
        return self._witnesses

    @witnesses.setter
    def witnesses(self, value):
        self._witnesses = value

    @hybrid_property
    def follow_up_notes(self):
        return self._follow_up_notes

    @follow_up_notes.setter
    def follow_up_notes(self, value):
        self._follow_up_notes = value

class MedicationNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medication.id'), nullable=False)
    notification_type = db.Column(db.String(20), nullable=False)  # '7_day_warning', 'expiration_day', 'expired'
    sent_date = db.Column(db.Date, nullable=False)
    
    # Ensure we don't send duplicate notifications
    __table_args__ = (db.UniqueConstraint('medication_id', 'notification_type', name='unique_med_notification'),)
