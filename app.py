import os
from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DateField, TimeField, SubmitField, FileField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from flask_mail import Mail, Message
import re
import json

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///afh.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'documents'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB file size limit
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME',
                                             'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD',
                                             'your-app-password')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME',
                                                   'your-email@gmail.com')
db = SQLAlchemy(app)
mail = Mail(app)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# CSRF Protection
csrf = CSRFProtect(app)


# Database Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'caregiver'


class Resident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    medical_info = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))


class FoodIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer,
                            db.ForeignKey('resident.id'),
                            nullable=False)
    date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)


class LiquidIntake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer,
                            db.ForeignKey('resident.id'),
                            nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    liquid_type = db.Column(db.String(50))
    amount = db.Column(db.String(50))


class BowelMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer,
                            db.ForeignKey('resident.id'),
                            nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    size = db.Column(db.String(20))
    consistency = db.Column(db.String(20))


class UrineOutput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer,
                            db.ForeignKey('resident.id'),
                            nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    output = db.Column(db.String(20))


class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer,
                            db.ForeignKey('resident.id'),
                            nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    notes = db.Column(db.Text)  # Added for medication notes
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)


class MedicationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer,
                              db.ForeignKey('medication.id'),
                              nullable=False)
    resident_id = db.Column(db.Integer,
                            db.ForeignKey('resident.id'),
                            nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    administered = db.Column(db.Boolean, default=False)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    resident_id = db.Column(db.Integer,
                            db.ForeignKey('resident.id'),
                            nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.Date, nullable=False)
    expiration_date = db.Column(db.Date)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class MedicationCatalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    default_dosage = db.Column(db.String(50))
    default_frequency = db.Column(db.String(50))
    default_notes = db.Column(db.Text)


# WTForms for CSRF-protected forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class AddUserForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(max=50)])
    password = PasswordField('Password',
                             validators=[DataRequired(),
                                         Length(min=8)])
    role = SelectField('Role',
                       choices=[('admin', 'Admin'),
                                ('caregiver', 'Caregiver')],
                       validators=[DataRequired()])
    submit = SubmitField('Save User')


class EditUserForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Length(max=50)])
    password = PasswordField(
        'Password',
        validators=[
            Length(min=8,
                   message="Password must be at least 8 characters long")
        ])
    role = SelectField('Role',
                       choices=[('admin', 'Admin'),
                                ('caregiver', 'Caregiver')],
                       validators=[DataRequired()])
    submit = SubmitField('Save User')


class AddResidentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    dob = DateField('Date of Birth', validators=[DataRequired()])
    medical_info = TextAreaField('Medical Info')
    emergency_contact = StringField('Emergency Contact',
                                    validators=[Length(max=100)])
    submit = SubmitField('Save Resident')


class FoodIntakeForm(FlaskForm):
    meal_type = SelectField('Meal Type',
                            choices=[('breakfast', 'Breakfast'),
                                     ('lunch', 'Lunch'), ('dinner', 'Dinner')],
                            validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Add Food Intake')


class LiquidIntakeForm(FlaskForm):
    time = StringField('Time', validators=[DataRequired()])
    liquid_type = StringField('Liquid Type', validators=[Length(max=50)])
    amount = StringField('Amount', validators=[Length(max=50)])
    submit = SubmitField('Add Liquid Intake')


class BowelMovementForm(FlaskForm):
    time = StringField('Time', validators=[DataRequired()])
    size = SelectField('Size',
                       choices=[('small', 'Small'), ('medium', 'Medium'),
                                ('large', 'Large')],
                       validators=[DataRequired()])
    consistency = SelectField('Consistency',
                              choices=[('soft', 'Soft'), ('medium', 'Medium'),
                                       ('hard', 'Hard')],
                              validators=[DataRequired()])
    submit = SubmitField('Add Bowel Movement')


class UrineOutputForm(FlaskForm):
    time = StringField('Time', validators=[DataRequired()])
    output = SelectField('Output',
                         choices=[('yes', 'Yes'), ('no', 'No'),
                                  ('no output', 'No Output')],
                         validators=[DataRequired()])
    submit = SubmitField('Add Urine Output')


class MedicationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    dosage = StringField('Dosage', validators=[Length(max=50)])
    frequency = StringField('Frequency', validators=[Length(max=50)])
    notes = TextAreaField('Notes')
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date')
    submit = SubmitField('Save Medication')


class MedicationLogForm(FlaskForm):
    medication_id = SelectField('Medication',
                                coerce=int,
                                validators=[DataRequired()])
    time = StringField('Time', validators=[DataRequired()])
    submit = SubmitField('Log Dose')


class DocumentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=100)])
    file = FileField('File (PDF or Image)', validators=[DataRequired()])
    expiration_date = DateField('Expiration Date')
    submit = SubmitField('Upload Document')


class ReportForm(FlaskForm):
    export_pdf = SubmitField('Export as PDF')


# Input validation and sanitization
def sanitize_input(text):
    if text:
        text = re.sub(r'<[^>]+>', '', text).strip()
    return text


def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, ""


# Send email notification
def send_alert_email(subject, body):
    try:
        msg = Message(subject, recipients=[app.config['MAIL_DEFAULT_SENDER']])
        msg.body = body
        mail.send(msg)
    except Exception as e:
        flash(f'Failed to send email: {str(e)}')


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = sanitize_input(form.username.data)
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            audit_log = AuditLog(user_id=user.id,
                                 action=f"User {username} logged in")
            db.session.add(audit_log)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    audit_log = AuditLog(user_id=current_user.id,
                         action=f"User {current_user.username} logged out")
    db.session.add(audit_log)
    db.session.commit()
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def home():
    residents = Resident.query.all()
    total_residents = len(residents)
    alerts = []
    today = date.today()
    for resident in residents:
        food_intakes = FoodIntake.query.filter_by(resident_id=resident.id,
                                                  date=today).all()
        meal_types = ['breakfast', 'lunch', 'dinner']
        logged_meals = [food.meal_type for food in food_intakes]
        for meal in meal_types:
            if meal not in logged_meals:
                alerts.append(f"Missing {meal} log for {resident.name}")
        documents = Document.query.filter_by(resident_id=resident.id).all()
        for doc in documents:
            if doc.expiration_date and doc.expiration_date < today:
                alerts.append(
                    f"Expired document: {doc.name} for {resident.name}")
                send_alert_email(
                    "Expired Document Alert",
                    f"Document {doc.name} for {resident.name} expired on {doc.expiration_date}"
                )
        medications = Medication.query.filter_by(resident_id=resident.id).all()
        for med in medications:
            if med.frequency == 'Daily' and (not med.end_date
                                             or med.end_date >= today):
                logs = MedicationLog.query.filter_by(medication_id=med.id,
                                                     date=today).count()
                if logs == 0:
                    alerts.append(
                        f"Missing dose for {med.name} for {resident.name}")
                    send_alert_email(
                        "Missing Medication Alert",
                        f"Missing dose for {med.name} for {resident.name} on {today}"
                    )
    return render_template('home.html',
                           residents=residents,
                           total_residents=total_residents,
                           alerts=alerts)


@app.route('/api/medication-suggestions', methods=['GET'])
def medication_suggestions():
    query = request.args.get('term', '')
    if not query:
        return jsonify([])
    suggestions = MedicationCatalog.query.filter(
        MedicationCatalog.name.ilike(f'%{query}%')).limit(10).all()
    return jsonify([{
        'label': med.name,
        'value': med.name,
        'dosage': med.default_dosage or '',
        'frequency': med.default_frequency or '',
        'notes': med.default_notes or ''
    } for med in suggestions])


@app.route('/audit_logs')
@login_required
def audit_logs():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('audit_logs.html', logs=logs)


@app.route('/users', methods=['GET'])
@login_required
def users():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/user/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    form = AddUserForm()
    if form.validate_on_submit():
        username = sanitize_input(form.username.data)
        password = form.password.data
        role = form.role.data
        is_valid, message = validate_password(password)
        if not is_valid:
            flash(message)
            return render_template('add_user.html',
                                   title='Add User',
                                   form=form)
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('add_user.html',
                                   title='Add User',
                                   form=form)
        if role not in ['admin', 'caregiver']:
            flash('Invalid role')
            return render_template('add_user.html',
                                   title='Add User',
                                   form=form)
        new_user = User(username=username,
                        password_hash=generate_password_hash(password),
                        role=role)
        db.session.add(new_user)
        db.session.commit()
        audit_log = AuditLog(user_id=current_user.id,
                             action=f"Added user {username}")
        db.session.add(audit_log)
        db.session.commit()
        flash('User added successfully.')
        return redirect(url_for('users'))
    return render_template('add_user.html', title='Add User', form=form)


@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    user = User.query.get_or_404(user_id)
    form = EditUserForm()
    if form.validate_on_submit():
        username = sanitize_input(form.username.data)
        password = form.password.data
        role = form.role.data
        if User.query.filter_by(
                username=username).first() and username != user.username:
            flash('Username already exists')
            return render_template('add_user.html',
                                   title='Edit User',
                                   form=form,
                                   user=user)
        if role not in ['admin', 'caregiver']:
            flash('Invalid role')
            return render_template('add_user.html',
                                   title='Edit User',
                                   form=form,
                                   user=user)
        user.username = username
        if password:
            is_valid, message = validate_password(password)
            if not is_valid:
                flash(message)
                return render_template('add_user.html',
                                       title='Edit User',
                                       form=form,
                                       user=user)
            user.password_hash = generate_password_hash(password)
        user.role = role
        db.session.commit()
        audit_log = AuditLog(user_id=current_user.id,
                             action=f"Edited user {username}")
        db.session.add(audit_log)
        db.session.commit()
        flash('User updated successfully.')
        return redirect(url_for('users'))
    form.username.data = user.username
    form.role.data = user.role
    return render_template('add_user.html',
                           title='Edit User',
                           form=form,
                           user=user)


@app.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Cannot delete your own account')
        return redirect(url_for('users'))
    username = user.username
    db.session.delete(user)
    db.session.commit()
    audit_log = AuditLog(user_id=current_user.id,
                         action=f"Deleted user {username}")
    db.session.add(audit_log)
    db.session.commit()
    flash('User deleted successfully.')
    return redirect(url_for('users'))


@app.route('/resident/add', methods=['GET', 'POST'])
@login_required
def add_resident():
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    form = AddResidentForm()
    if form.validate_on_submit():
        name = sanitize_input(form.name.data)
        dob = form.dob.data
        medical_info = sanitize_input(form.medical_info.data)
        emergency_contact = sanitize_input(form.emergency_contact.data)
        if not name:
            flash('Name is required')
            return render_template('add_resident.html',
                                   title='Add Resident',
                                   form=form)
        new_resident = Resident(name=name,
                                dob=dob,
                                medical_info=medical_info,
                                emergency_contact=emergency_contact)
        db.session.add(new_resident)
        db.session.commit()
        audit_log = AuditLog(user_id=current_user.id,
                             action=f"Added resident {name}")
        db.session.add(audit_log)
        db.session.commit()
        flash('Resident added successfully.')
        return redirect(url_for('home'))
    return render_template('add_resident.html',
                           title='Add Resident',
                           form=form)


@app.route('/resident/<int:resident_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_resident(resident_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    resident = Resident.query.get_or_404(resident_id)
    form = AddResidentForm()
    if form.validate_on_submit():
        name = sanitize_input(form.name.data)
        dob = form.dob.data
        medical_info = sanitize_input(form.medical_info.data)
        emergency_contact = sanitize_input(form.emergency_contact.data)
        if not name:
            flash('Name is required')
            return render_template('add_resident.html',
                                   title='Edit Resident',
                                   form=form,
                                   resident=resident)
        resident.name = name
        resident.dob = dob
        resident.medical_info = medical_info
        resident.emergency_contact = emergency_contact
        db.session.commit()
        audit_log = AuditLog(user_id=current_user.id,
                             action=f"Edited resident {name}")
        db.session.add(audit_log)
        db.session.commit()
        flash('Resident updated successfully.')
        return redirect(url_for('resident_profile', resident_id=resident_id))
    form.name.data = resident.name
    form.dob.data = resident.dob
    form.medical_info.data = resident.medical_info
    form.emergency_contact.data = resident.emergency_contact
    return render_template('add_resident.html',
                           title='Edit Resident',
                           form=form,
                           resident=resident)


@app.route('/resident/<int:resident_id>/delete', methods=['POST'])
@login_required
def delete_resident(resident_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    resident = Resident.query.get_or_404(resident_id)
    name = resident.name
    db.session.delete(resident)
    db.session.commit()
    audit_log = AuditLog(user_id=current_user.id,
                         action=f"Deleted resident {name}")
    db.session.add(audit_log)
    db.session.commit()
    flash('Resident deleted successfully.')
    return redirect(url_for('home'))


@app.route('/resident/<int:resident_id>')
@login_required
def resident_profile(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    return render_template('resident_profile.html', resident=resident)


@app.route('/resident/<int:resident_id>/logs', methods=['GET', 'POST'])
@login_required
def daily_logs(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    date_str = request.args.get('date', date.today().isoformat())
    log_date = datetime.strptime(date_str, '%Y-%m-%d').date()

    food_intakes = FoodIntake.query.filter_by(resident_id=resident_id,
                                              date=log_date).all()
    liquid_intakes = LiquidIntake.query.filter_by(resident_id=resident_id,
                                                  date=log_date).all()
    bowel_movements = BowelMovement.query.filter_by(resident_id=resident_id,
                                                    date=log_date).all()
    urine_outputs = UrineOutput.query.filter_by(resident_id=resident_id,
                                                date=log_date).all()

    missing_logs = []
    meal_types = ['breakfast', 'lunch', 'dinner']
    logged_meals = [food.meal_type for food in food_intakes]
    for meal in meal_types:
        if meal not in logged_meals:
            missing_logs.append(f"Missing {meal} log")

    prev_date = (log_date - timedelta(days=1)).isoformat()
    next_date = (log_date + timedelta(days=1)).isoformat()

    food_form = FoodIntakeForm()
    liquid_form = LiquidIntakeForm()
    bowel_form = BowelMovementForm()
    urine_form = UrineOutputForm()

    if request.method == 'POST':
        if food_form.validate_on_submit(
        ) and 'add_food' in request.form and current_user.role in [
                'admin', 'caregiver'
        ]:
            meal_type = food_form.meal_type.data
            description = sanitize_input(food_form.description.data)
            if meal_type not in meal_types:
                flash('Invalid meal type')
                return redirect(
                    url_for('daily_logs',
                            resident_id=resident_id,
                            date=log_date.isoformat()))
            new_food = FoodIntake(resident_id=resident_id,
                                  date=log_date,
                                  meal_type=meal_type,
                                  description=description)
            db.session.add(new_food)
            db.session.commit()
            audit_log = AuditLog(
                user_id=current_user.id,
                action=f"Added food intake for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Food intake added successfully.')
        elif liquid_form.validate_on_submit(
        ) and 'add_liquid' in request.form and current_user.role in [
                'admin', 'caregiver'
        ]:
            liquid_type = sanitize_input(liquid_form.liquid_type.data)
            amount = sanitize_input(liquid_form.amount.data)
            time = datetime.strptime(liquid_form.time.data, '%H:%M').time()
            new_liquid = LiquidIntake(resident_id=resident_id,
                                      date=log_date,
                                      time=time,
                                      liquid_type=liquid_type,
                                      amount=amount)
            db.session.add(new_liquid)
            db.session.commit()
            audit_log = AuditLog(
                user_id=current_user.id,
                action=f"Added liquid intake for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Liquid intake added successfully.')
        elif bowel_form.validate_on_submit(
        ) and 'add_bowel' in request.form and current_user.role in [
                'admin', 'caregiver'
        ]:
            time = datetime.strptime(bowel_form.time.data, '%H:%M').time()
            size = bowel_form.size.data
            consistency = bowel_form.consistency.data
            if size not in ['small', 'medium', 'large'
                            ] or consistency not in ['soft', 'medium', 'hard']:
                flash('Invalid bowel movement data')
                return redirect(
                    url_for('daily_logs',
                            resident_id=resident_id,
                            date=log_date.isoformat()))
            new_bowel = BowelMovement(resident_id=resident_id,
                                      date=log_date,
                                      time=time,
                                      size=size,
                                      consistency=consistency)
            db.session.add(new_bowel)
            db.session.commit()
            audit_log = AuditLog(
                user_id=current_user.id,
                action=f"Added bowel movement for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Bowel movement added successfully.')
        elif urine_form.validate_on_submit(
        ) and 'add_urine' in request.form and current_user.role in [
                'admin', 'caregiver'
        ]:
            time = datetime.strptime(urine_form.time.data, '%H:%M').time()
            output = urine_form.output.data
            if output not in ['yes', 'no', 'no output']:
                flash('Invalid urine output data')
                return redirect(
                    url_for('daily_logs',
                            resident_id=resident_id,
                            date=log_date.isoformat()))
            new_urine = UrineOutput(resident_id=resident_id,
                                    date=log_date,
                                    time=time,
                                    output=output)
            db.session.add(new_urine)
            db.session.commit()
            audit_log = AuditLog(
                user_id=current_user.id,
                action=f"Added urine output for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Urine output added successfully.')
        return redirect(
            url_for('daily_logs',
                    resident_id=resident_id,
                    date=log_date.isoformat()))

    return render_template('daily_logs.html',
                           resident=resident,
                           log_date=log_date,
                           food_intakes=food_intakes,
                           liquid_intakes=liquid_intakes,
                           bowel_movements=bowel_movements,
                           urine_outputs=urine_outputs,
                           missing_logs=missing_logs,
                           prev_date=prev_date,
                           next_date=next_date,
                           food_form=food_form,
                           liquid_form=liquid_form,
                           bowel_form=bowel_form,
                           urine_form=urine_form)


@app.route('/resident/<int:resident_id>/medications', methods=['GET', 'POST'])
@login_required
def medications(resident_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))

    resident = Resident.query.get_or_404(resident_id)
    medications = Medication.query.filter_by(resident_id=resident_id).all()
    medication_form = MedicationForm()
    log_form = MedicationLogForm()
    log_form.medication_id.choices = [(med.id, med.name)
                                      for med in medications]

    if request.method == 'POST':
        if medication_form.validate_on_submit(
        ) and 'add_medication' in request.form:
            name = sanitize_input(medication_form.name.data)
            dosage = sanitize_input(medication_form.dosage.data)
            frequency = sanitize_input(medication_form.frequency.data)
            notes = sanitize_input(medication_form.notes.data)
            start_date = medication_form.start_date.data
            end_date = medication_form.end_date.data
            if not name:
                flash('Medication name is required')
                return redirect(url_for('medications',
                                        resident_id=resident_id))
            new_med = Medication(resident_id=resident_id,
                                 name=name,
                                 dosage=dosage,
                                 frequency=frequency,
                                 notes=notes,
                                 start_date=start_date,
                                 end_date=end_date)
            db.session.add(new_med)
            # Add to MedicationCatalog if not already present
            if not MedicationCatalog.query.filter_by(name=name).first():
                catalog_entry = MedicationCatalog(name=name,
                                                  default_dosage=dosage,
                                                  default_frequency=frequency,
                                                  default_notes=notes)
                db.session.add(catalog_entry)
            db.session.commit()
            audit_log = AuditLog(
                user_id=current_user.id,
                action=f"Added medication {name} for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Medication added successfully.')
        elif log_form.validate_on_submit() and 'log_dose' in request.form:
            medication_id = log_form.medication_id.data
            time = datetime.strptime(log_form.time.data, '%H:%M').time()
            med_name = Medication.query.get(medication_id).name
            new_log = MedicationLog(medication_id=medication_id,
                                    resident_id=resident_id,
                                    date=date.today(),
                                    time=time,
                                    administered=True)
            db.session.add(new_log)
            db.session.commit()
            audit_log = AuditLog(
                user_id=current_user.id,
                action=f"Logged dose for {med_name} for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Dose logged successfully.')
        elif 'delete_medication' in request.form:
            medication_id = request.form['medication_id']
            medication = Medication.query.get_or_404(medication_id)
            med_name = medication.name
            db.session.delete(medication)
            db.session.commit()
            audit_log = AuditLog(
                user_id=current_user.id,
                action=f"Deleted medication {med_name} for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Medication deleted successfully.')
        return redirect(url_for('medications', resident_id=resident_id))

    medication_logs = MedicationLog.query.filter_by(
        resident_id=resident_id).all()
    return render_template('medications.html',
                           resident=resident,
                           medications=medications,
                           medication_logs=medication_logs,
                           medication_form=medication_form,
                           log_form=log_form)


@app.route('/resident/<int:resident_id>/documents', methods=['GET', 'POST'])
@login_required
def documents(resident_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))

    resident = Resident.query.get_or_404(resident_id)
    documents = Document.query.filter_by(resident_id=resident_id).all()
    form = DocumentForm()

    expired_documents = [
        doc for doc in documents
        if doc.expiration_date and doc.expiration_date < date.today()
    ]

    if request.method == 'POST':
        if form.validate_on_submit() and 'add_document' in request.form:
            file = form.file.data
            name = sanitize_input(form.name.data)
            expiration_date = form.expiration_date.data
            if not file or not name:
                flash('File and name are required')
                return redirect(url_for('documents', resident_id=resident_id))
            if not (file.filename.endswith('.pdf')
                    or file.filename.lower().endswith(
                        ('.jpg', '.jpeg', '.png'))):
                flash('Invalid file type. Only PDFs and images allowed.')
                return redirect(url_for('documents', resident_id=resident_id))
            try:
                filename = f"{resident_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_doc = Document(resident_id=resident_id,
                                   filename=filename,
                                   name=name,
                                   upload_date=date.today(),
                                   expiration_date=expiration_date)
                db.session.add(new_doc)
                db.session.commit()
                audit_log = AuditLog(
                    user_id=current_user.id,
                    action=f"Uploaded document {name} for {resident.name}")
                db.session.add(audit_log)
                db.session.commit()
                flash('Document uploaded successfully.')
            except Exception as e:
                flash(f'Failed to upload document: {str(e)}')
        elif 'delete_document' in request.form:
            document_id = request.form['document_id']
            document = Document.query.get_or_404(document_id)
            doc_name = document.name
            try:
                os.remove(
                    os.path.join(app.config['UPLOAD_FOLDER'],
                                 document.filename))
            except OSError:
                pass
            db.session.delete(document)
            db.session.commit()
            audit_log = AuditLog(
                user_id=current_user.id,
                action=f"Deleted document {doc_name} for {resident.name}")
            db.session.add(audit_log)
            db.session.commit()
            flash('Document deleted successfully.')
        return redirect(url_for('documents', resident_id=resident_id))

    return render_template('documents.html',
                           resident=resident,
                           documents=documents,
                           expired_documents=expired_documents,
                           form=form)


@app.route('/documents/<path:filename>')
@login_required
def serve_document(filename):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/resident/<int:resident_id>/report', methods=['GET', 'POST'])
@login_required
def report(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    form = ReportForm()
    start_date = request.args.get(
        'start_date', (date.today() - timedelta(days=7)).isoformat())
    end_date = request.args.get('end_date', date.today().isoformat())

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format')
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()

    food_intakes = FoodIntake.query.filter_by(resident_id=resident_id).filter(
        FoodIntake.date.between(start_date, end_date)).all()
    liquid_intakes = LiquidIntake.query.filter_by(
        resident_id=resident_id).filter(
            LiquidIntake.date.between(start_date, end_date)).all()
    bowel_movements = BowelMovement.query.filter_by(
        resident_id=resident_id).filter(
            BowelMovement.date.between(start_date, end_date)).all()
    urine_outputs = UrineOutput.query.filter_by(
        resident_id=resident_id).filter(
            UrineOutput.date.between(start_date, end_date)).all()
    medication_logs = MedicationLog.query.filter_by(
        resident_id=resident_id).filter(
            MedicationLog.date.between(start_date, end_date)).all()

    date_range = [
        start_date + timedelta(days=x)
        for x in range((end_date - start_date).days + 1)
    ]
    meal_counts = {
        d.isoformat(): {
            'breakfast': 0,
            'lunch': 0,
            'dinner': 0
        }
        for d in date_range
    }
    for food in food_intakes:
        date_str = food.date.isoformat()
        if date_str in meal_counts:
            meal_counts[date_str][food.meal_type] += 1
    chart_labels = [d.isoformat() for d in date_range]
    chart_data = {
        'breakfast': [meal_counts[d]['breakfast'] for d in chart_labels],
        'lunch': [meal_counts[d]['lunch'] for d in chart_labels],
        'dinner': [meal_counts[d]['dinner'] for d in chart_labels]
    }

    if form.validate_on_submit() and form.export_pdf.data:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)
        pdf.setFont("Helvetica", 12)
        y = 750
        pdf.drawString(
            100, y, f"Report for {resident.name}: {start_date} to {end_date}")
        y -= 20
        pdf.drawString(100, y, "Food Intakes")
        y -= 20
        for food in food_intakes:
            pdf.drawString(
                120, y,
                f"{food.date} - {food.meal_type.capitalize()}: {food.description}"
            )
            y -= 15
            if y < 50:
                pdf.showPage()
                y = 750
                pdf.setFont("Helvetica", 12)
        y -= 20
        pdf.drawString(100, y, "Liquid Intakes")
        y -= 20
        for liquid in liquid_intakes:
            pdf.drawString(
                120, y,
                f"{liquid.date} {liquid.time}: {liquid.liquid_type} - {liquid.amount}"
            )
            y -= 15
            if y < 50:
                pdf.showPage()
                y = 750
                pdf.setFont("Helvetica", 12)
        y -= 20
        pdf.drawString(100, y, "Bowel Movements")
        y -= 20
        for bowel in bowel_movements:
            pdf.drawString(
                120, y,
                f"{bowel.date} {bowel.time}: Size - {bowel.size}, Consistency - {bowel.consistency}"
            )
            y -= 15
            if y < 50:
                pdf.showPage()
                y = 750
                pdf.setFont("Helvetica", 12)
        y -= 20
        pdf.drawString(100, y, "Urine Outputs")
        y -= 20
        for urine in urine_outputs:
            pdf.drawString(120, y,
                           f"{urine.date} {urine.time}: {urine.output}")
            y -= 15
            if y < 50:
                pdf.showPage()
                y = 750
                pdf.setFont("Helvetica", 12)
        y -= 20
        pdf.drawString(100, y, "Medication Logs")
        y -= 20
        for log in medication_logs:
            med_name = Medication.query.get(log.medication_id).name
            pdf.drawString(
                120, y, f"{log.date} {log.time}: {med_name} - Administered")
            y -= 15
            if y < 50:
                pdf.showPage()
                y = 750
                pdf.setFont("Helvetica", 12)
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        safe_name = re.sub(r'[^\w\-]', '_', resident.name)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"report_{safe_name}_{start_date}_to_{end_date}.pdf",
            mimetype='application/pdf')

    return render_template('report.html',
                           resident=resident,
                           start_date=start_date,
                           end_date=end_date,
                           food_intakes=food_intakes,
                           liquid_intakes=liquid_intakes,
                           bowel_movements=bowel_movements,
                           urine_outputs=urine_outputs,
                           medication_logs=medication_logs,
                           chart_labels=json.dumps(chart_labels),
                           chart_data=json.dumps(chart_data),
                           form=form)


# Run the app and initialize database with sample data
if __name__ == '__main__':
    with app.app_context():
        print("Creating database at afh.db...")
        db.create_all()
        print("Database created!")
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin',
                         password_hash=generate_password_hash('admin123'),
                         role='admin')
            db.session.add(admin)
            db.session.commit()
        if not User.query.filter_by(username='caregiver').first():
            caregiver = User(
                username='caregiver',
                password_hash=generate_password_hash('caregiver123'),
                role='caregiver')
            db.session.add(caregiver)
            db.session.commit()
        if not Resident.query.filter_by(name='John Doe').first():
            resident = Resident(name='John Doe',
                                dob=date(1950, 1, 1),
                                medical_info='Diabetic',
                                emergency_contact='Jane Doe - 555-1234')
            db.session.add(resident)
            db.session.commit()
        sample_medications = [{
            'name': 'Lisinopril',
            'default_dosage': '10 mg',
            'default_frequency': 'Daily',
            'default_notes': 'Take with water'
        }, {
            'name': 'Metformin',
            'default_dosage': '500 mg',
            'default_frequency': 'Twice daily',
            'default_notes': 'Take with meals'
        }, {
            'name': 'Ibuprofen',
            'default_dosage': '200 mg',
            'default_frequency': 'As needed',
            'default_notes': 'Do not exceed 3200 mg daily'
        }, {
            'name': 'Amlodipine',
            'default_dosage': '5 mg',
            'default_frequency': 'Daily',
            'default_notes': 'Monitor blood pressure'
        }, {
            'name': 'Atorvastatin',
            'default_dosage': '20 mg',
            'default_frequency': 'Daily',
            'default_notes': 'Take at night'
        }]
        for med in sample_medications:
            if not MedicationCatalog.query.filter_by(name=med['name']).first():
                db.session.add(MedicationCatalog(**med))
        db.session.commit()
    app.run(host='0.0.0.0', port=8080, debug=True)
