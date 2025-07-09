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

class MedicationCatalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # Generic name
    brand_name = db.Column(db.String(100))  # Brand name
    default_dosage = db.Column(db.String(50))
    default_frequency = db.Column(db.String(50))
    _default_notes = db.Column(EncryptedText)
    form = db.Column(db.String(50))
    _common_uses = db.Column(EncryptedText)

    @hybrid_property
    def default_notes(self):
        return self._default_notes

    @default_notes.setter
    def default_notes(self, value):
        self._default_notes = value

    @hybrid_property
    def common_uses(self):
        return self._common_uses

    @common_uses.setter
    def common_uses(self, value):
        self._common_uses = value