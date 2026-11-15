import os
import sqlite3
from datetime import datetime, date
from flask import Flask, render_template, redirect, url_for, session, request, flash
from config import Config

# Register ISO adapters for sqlite3 in Python 3.12+
sqlite3.register_adapter(date, lambda d: d.isoformat())
sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())

from models import db, User, Department, Student, Room, Bench, Examination, ExaminationDepartmentSubject, AllocationRule, SeatAssignment, Invigilator, InvigilatorAssignment, Attendance, ActivityLog, Setting, AllocationHistory, Notification, ExaminationTimetable, ArrearRecord, ArrearCandidateSelection, ExaminationStatusHistory, StoredFile, run_migrations, log_activity

def create_app(config_override=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)

    # Adapt engine options if URI was overridden (e.g. SQLite in unit tests)
    target_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'sqlite:' in target_uri:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.init_app(app)

    with app.app_context():
        db.create_all()
        run_migrations(app)

        # All authentication credentials reside strictly in the database.
        # Find any existing superadmin or legacy administrator in the database
        superadmin = User.query.filter_by(role='SUPERADMIN').order_by(User.id.asc()).first()
        if not superadmin:
            superadmin = User.query.filter(User.role.in_(['Administrator', 'admin'])).order_by(User.id.asc()).first()
            if superadmin:
                superadmin.role = 'SUPERADMIN'
                superadmin.is_active = True
                superadmin.status = 'Active'
                db.session.commit()
            elif User.query.count() == 0:
                # First-time bootstrap only when database contains zero users.
                # Credentials are read from environment variables rather than hardcoded in code.
                import secrets
                bootstrap_user = os.environ.get('INITIAL_SUPERADMIN_USERNAME') or os.environ.get('SUPERADMIN_USERNAME') or 'superadmin'
                bootstrap_pass = os.environ.get('INITIAL_SUPERADMIN_PASSWORD') or os.environ.get('SUPERADMIN_PASSWORD')
                if not bootstrap_pass:
                    # Generate a secure one-time bootstrap password if none configured in environment
                    bootstrap_pass = secrets.token_urlsafe(12)
                    print(f"[*] Bootstrap: Created initial Superadmin account in DB: username='{bootstrap_user}', password='{bootstrap_pass}'")

                new_sa = User(
                    username=bootstrap_user,
                    full_name=os.environ.get('SUPERADMIN_FULL_NAME', 'Super Administrator'),
                    role='SUPERADMIN',
                    is_active=True,
                    status='Active'
                )
                new_sa.set_password(bootstrap_pass)
                db.session.add(new_sa)
                db.session.commit()

        # Seed default departments if empty
        if Department.query.count() == 0:
            departments = [
                Department(code='DS', name='B.Sc. Data Science', color='#2563eb', description='Department of Data Science'),
                Department(code='BCA', name='Bachelor of Computer Applications', color='#0d9488', description='Department of Computer Applications'),
                Department(code='CS', name='B.Sc. Computer Science', color='#9333ea', description='Department of Computer Science'),
                Department(code='COM', name='B.Com.', color='#ea580c', description='Department of Commerce'),
                Department(code='BBA', name='Bachelor of Business Administration', color='#e11d48', description='Department of Business Administration'),
                Department(code='BCCA', name='B.Com. Computer Applications', color='#0284c7', description='Department of Commerce with Computer Applications'),
                Department(code='ENG', name='B.A. English', color='#16a34a', description='Department of English'),
                Department(code='TAM', name='B.A. Tamil', color='#d97706', description='Department of Tamil'),
                Department(code='MATH', name='B.Sc. Mathematics', color='#4f46e5', description='Department of Mathematics'),
                Department(code='PHY', name='B.Sc. Physics', color='#0891b2', description='Department of Physics'),
                Department(code='CHEM', name='B.Sc. Chemistry', color='#dc2626', description='Department of Chemistry'),
                Department(code='ZOO', name='B.Sc. Zoology', color='#059669', description='Department of Zoology'),
                Department(code='BOT', name='B.Sc. Botany', color='#65a30d', description='Department of Botany'),
                Department(code='MICRO', name='B.Sc. Microbiology', color='#7c3aed', description='Department of Microbiology'),
                Department(code='BIOTECH', name='B.Sc. Biotechnology', color='#c026d3', description='Department of Biotechnology'),
                Department(code='PSY', name='B.Sc. Psychology', color='#db2777', description='Department of Psychology'),
                Department(code='IT', name='B.Sc. Information Technology', color='#2563eb', description='Department of Information Technology'),
                Department(code='AF', name='B.Com. Accounting and Finance', color='#d97706', description='Department of Accounting and Finance'),
                Department(code='HIS', name='B.A. History', color='#b45309', description='Department of History'),
                Department(code='VISCOM', name='B.Sc. Visual Communication', color='#0284c7', description='Department of Visual Communication')
            ]
            db.session.bulk_save_objects(departments)

        # Seed initial rooms (LH 1, LH 2, LH 3) if none exist
        if Room.query.count() == 0:
            for idx in range(1, 4):
                room = Room(
                    name=f"LH {idx}",
                    building="Academic Block A",
                    floor=f"Floor {idx}",
                    rows=5,
                    cols=3,
                    total_benches=15,
                    seats_per_bench=2,
                    capacity=30,
                    display_order=idx
                )
                db.session.add(room)
                db.session.flush()

                # Generate 15 benches
                for b_num in range(1, 16):
                    # Group: 1..5 Left, 6..10 Middle, 11..15 Right
                    col_g = 1 if b_num <= 5 else (2 if b_num <= 10 else 3)
                    bench = Bench(
                        room_id=room.id,
                        bench_number=b_num,
                        global_bench_number=(idx - 1) * 15 + b_num,
                        col_group=col_g,
                        is_usable=True
                    )
                    db.session.add(bench)

        # Seed default examination if empty
        if Examination.query.count() == 0:
            exam1 = Examination(
                name='Semester Exam - Nov 2025',
                subject_name='Database Management Systems',
                subject_code='CS302',
                academic_year='2025-2026',
                exam_date='2025-11-22',
                session='FN (9:00 AM - 12:00 PM)',
                start_time='09:00 AM',
                end_time='12:00 PM',
                eligible_departments='ALL',
                status='Scheduled'
            )
            exam2 = Examination(
                name='Semester Exam - Nov 2025',
                subject_name='Data Structures & Algorithms',
                subject_code='CS201',
                academic_year='2025-2026',
                exam_date='2025-11-23',
                session='AN (1:30 PM - 04:30 PM)',
                start_time='01:30 PM',
                end_time='04:30 PM',
                eligible_departments='ALL',
                status='Scheduled'
            )
            db.session.add(exam1)
            db.session.add(exam2)

        # Do not seed sample students. System remains empty until dataset import.


        # Seed Invigilators if empty
        if Invigilator.query.count() == 0:
            staffs = [
                Invigilator(staff_id='STF-101', name='Dr. Ramesh Sharma', department='Computer Science', phone='9876543210'),
                Invigilator(staff_id='STF-102', name='Prof. Sunita Patil', department='Data Science', phone='9876543211'),
                Invigilator(staff_id='STF-103', name='Dr. Vijay Kumar', department='Commerce', phone='9876543212'),
                Invigilator(staff_id='STF-104', name='Prof. Lakshmi Devi', department='Mathematics', phone='9876543213')
            ]
            db.session.bulk_save_objects(staffs)

        # Seed initial system notifications if empty
        if Notification.query.count() == 0:
            notifs = [
                Notification(
                    title="Student Dataset Synchronized",
                    message="1,359 active student records are verified across 23 departments.",
                    category="success",
                    icon="user-check",
                    is_read=False,
                    action_url="/students"
                ),
                Notification(
                    title="Examination Scheduled",
                    message="CS302 - Database Management Systems scheduled for Nov 22, FN.",
                    category="info",
                    icon="calendar",
                    is_read=False,
                    action_url="/examinations"
                ),
                Notification(
                    title="Exam Room Allocation Ready",
                    message="Hall capacity stands at 654 seats across 22 configured rooms.",
                    category="warning",
                    icon="door-open",
                    is_read=False,
                    action_url="/rooms"
                )
            ]
            db.session.bulk_save_objects(notifs)

        db.session.commit()


    # --- SECURITY & ERROR HANDLING ENHANCEMENTS ---
    @app.after_request
    def set_security_headers(response):
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # Prevent MIME-type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # Control referrer information
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        # XSS Protection for older browsers
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    @app.errorhandler(400)
    def handle_bad_request(e):
        if request.path.startswith('/api/') or request.accept_mimetypes.best == 'application/json':
            return {'success': False, 'error': 'Bad request.'}, 400
        return render_template('base.html', bad_request_error=True), 400

    @app.errorhandler(404)
    def handle_not_found(e):
        if request.path.startswith('/api/') or request.accept_mimetypes.best == 'application/json':
            return {'success': False, 'error': 'Endpoint not found.'}, 404
        return render_template('base.html', not_found_error=True), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        db.session.rollback()
        if request.path.startswith('/api/') or request.accept_mimetypes.best == 'application/json':
            return {'success': False, 'error': 'An internal server error occurred.'}, 500
        return render_template('base.html', server_error=True), 500

    # Register Blueprints
    from routes.main_routes import main_bp
    from routes.api_routes import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5050))
    debug_mode = os.environ.get('FLASK_DEBUG', 'true').lower() in ('true', '1')
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
