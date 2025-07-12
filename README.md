
# AFH Management System

A comprehensive Adult Family Home (AFH) management application built with Flask for managing residents, medications, documents, daily logs, and incident reports.

## Features

- **Resident Management** - Add, edit, and track resident information
- **Medication Tracking** - Monitor medications with expiration alerts
- **Document Management** - Store and organize resident documents
- **Daily Logs** - Track meals, vitals, and daily activities
- **Incident Reports** - Document and manage incidents
- **User Management** - Role-based access control (Admin/Staff)
- **Audit Logs** - Track all system activities
- **Email Notifications** - Automated alerts for medication/document expiration

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, HTML5, JavaScript
- **Charts**: Chart.js
- **Security**: Encrypted data storage, CSRF protection
- **Email**: Flask-Mail for notifications

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd afh-management
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export FLASK_SECRET_KEY="your-secret-key"
export MAIL_SERVER="your-mail-server"
export MAIL_USERNAME="your-email@example.com"
export MAIL_PASSWORD="your-email-password"
```

4. Initialize the database:
```bash
python app.py
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:8080
```

3. Default admin login:
   - Username: `admin`
   - Password: `admin123`

## Project Structure

```
afh-management/
├── app.py                 # Main Flask application
├── models.py             # Database models
├── forms.py              # WTForms for form handling
├── medication_notifications.py  # Email notification system
├── medications_data.py   # Medication catalog data
├── templates/            # HTML templates
│   ├── base.html
│   ├── home.html
│   ├── resident_profile.html
│   └── ...
├── static/              # CSS, JS, and static assets
│   ├── css/
│   └── js/
└── documents/           # Uploaded documents storage
```

## Key Features

### Resident Management
- Add new residents with medical information
- Track emergency contacts and important details
- Edit and update resident information
- Secure deletion with confirmation

### Medication System
- Add medications with dosage and frequency
- Track expiration dates with automated alerts
- Medication catalog with common medications
- Email notifications for expiring medications

### Daily Logging
- Track food intake, liquid consumption
- Monitor bowel movements and urine output
- Record vital signs
- Multi-step wizard interface

### Document Management
- Upload and store resident documents
- Track document expiration dates
- Secure file storage and retrieval

### Security Features
- Encrypted sensitive data storage
- Role-based access control
- CSRF protection on all forms
- Audit logging for all actions

## Configuration

### Email Settings
Configure email notifications in your environment:

```python
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'your-email@gmail.com'
MAIL_PASSWORD = 'your-app-password'
```

### Database
The application uses SQLite by default. The database file (`afh.db`) is created automatically on first run.

## API Endpoints

- `GET /` - Home dashboard
- `GET /resident/<id>` - Resident profile
- `GET /resident/<id>/medications` - Medication management
- `GET /resident/<id>/documents` - Document management
- `GET /resident/<id>/logs` - Daily logs
- `GET /resident/<id>/incidents` - Incident reports
- `POST /add_resident` - Add new resident
- `POST /resident/<id>/edit` - Edit resident

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
python app.py
```

### Database Migrations
The application automatically handles database schema updates on startup.

## Deployment

This application is designed to run on Replit. Simply:

1. Import your code to a new Repl
2. Set your environment variables in Replit Secrets
3. Click the Run button

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please create an issue in the repository.

## Changelog

### Version 0.1.0
- Initial release
- Basic resident management
- Medication tracking
- Document management
- Daily logging system
- Incident reporting
- Email notifications

---

**Note**: This is a healthcare management application. Ensure compliance with HIPAA and other relevant regulations when deploying in production environments.
