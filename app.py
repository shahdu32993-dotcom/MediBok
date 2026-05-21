from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from functools import wraps
from datetime import datetime, date
import os

load_dotenv(dotenv_path='secret.env')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('CONNECTION_STRING')
app.config['SECRET_KEY']              = os.getenv('SECRET_KEY', 'fallback-secret')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ─────────────────────────────────────────
#  MODELS
# ─────────────────────────────────────────

class Department(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    def __repr__(self):
        return f"<Department {self.name}>"


class User(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20), default='patient')
    phone         = db.Column(db.String(20))
    specialty     = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    bio           = db.Column(db.Text)
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    department          = db.relationship('Department', backref='staff')
    appointments        = db.relationship('Appointment', foreign_keys='Appointment.patient_id', backref='patient', lazy=True)
    doctor_appointments = db.relationship('Appointment', foreign_keys='Appointment.doctor_id',  backref='doctor',  lazy=True)
    sent_messages       = db.relationship('Message', foreign_keys='Message.sender_id',   backref='sender',   lazy=True)
    received_messages   = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)

    def set_password(self, p):
        self.password_hash = generate_password_hash(p)

    def check_password(self, p):
        return check_password_hash(self.password_hash, p)

    def __repr__(self):
        return f"<User {self.email}>"


class Appointment(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    patient_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    date          = db.Column(db.String(20), nullable=False)
    time          = db.Column(db.String(10), nullable=False)
    reason        = db.Column(db.Text)
    status        = db.Column(db.String(20), default='pending')
    notes         = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    department = db.relationship('Department', backref='appointments')

    def __repr__(self):
        return f"<Appointment {self.id} - {self.status}>"


class Message(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    sender_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content     = db.Column(db.Text, nullable=False)
    is_read     = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.sender_id} → {self.receiver_id}>"


# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def get_current_user():
    if 'user_id' in session:
        return db.session.get(User, session['user_id'])
    return None


def seed_initial_data():
    """تهيئة الأقسام وحساب Admin عند أول تشغيل فقط."""
    if Department.query.first():
        return

    depts = [
        Department(name='Cardiology',  description='Heart and cardiovascular system care'),
        Department(name='Neurology',   description='Brain, spine, and nervous system'),
        Department(name='Orthopedics', description='Bones, joints, and muscles'),
        Department(name='Pediatrics',  description='Medical care for children'),
        Department(name='Dermatology', description='Skin, hair, and nail conditions'),
    ]
    for d in depts:
        db.session.add(d)

    if not User.query.filter_by(role='admin').first():
        admin = User(name='Admin', email='admin@gmail.com', role='admin', phone='0000000000')
        admin.set_password('admin123')
        db.session.add(admin)

    if not User.query.filter_by(role='doctor').first():
        for name, email, phone, specialty, dept_id in [
            ('Dr. Sarah Ahmed', 'sarah@gmail.com', '01011111111', 'Cardiologist', 1),
            ('Dr. Omar Hassan', 'omar@gmail.com',  '01022222222', 'Neurologist',  2),
            ('Dr. Nour El-Din', 'nour@gmail.com',  '01033333333', 'Orthopedist',  3),
        ]:
            doc = User(name=name, email=email, role='doctor', phone=phone,
                       specialty=specialty, department_id=dept_id)
            doc.set_password('doctor123')
            db.session.add(doc)

    if not User.query.filter_by(role='patient').first():
        patient = User(name='Ahmed Mohamed', email='patient@gmail.com',
                       role='patient', phone='01044444444')
        patient.set_password('patient123')
        db.session.add(patient)

    db.session.commit()


# ─────────────────────────────────────────
#  ROUTES
# ─────────────────────────────────────────

@app.route('/')
def index():
    db.session.execute(text('CREATE DATABASE IF NOT EXISTS hospital_db'))
    db.create_all()
    db.session.commit()
    seed_initial_data()

    user        = get_current_user()
    departments = Department.query.all()
    doctors     = User.query.filter_by(role='doctor').all()
    return render_template('index.html', user=user, departments=departments, doctors=doctors)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name  = request.form['first_name'].strip() + ' ' + request.form['last_name'].strip()
        email = request.form['email'].strip().lower()
        pwd   = request.form['password']
        phone = request.form.get('phone', '').strip()

        if User.query.filter_by(email=email).first():
            msg = 'Email already registered.'
            return render_template('register.html', msg=msg)

        user = User(name=name, email=email, phone=phone, role='patient')
        user.set_password(pwd)
        db.session.add(user)
        db.session.commit()

        session['user_id']  = user.id
        session['role']     = user.role
        session['username'] = user.name
        flash(f"Welcome, {user.name}!", 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        pwd   = request.form['password']
        user  = User.query.filter_by(email=email).first()

        if user and user.is_active and user.check_password(pwd):
            session.clear()                      # امسح أي session قديم أولاً
            session['user_id']  = user.id
            session['role']     = user.role
            session['username'] = user.name
            flash(f"Welcome back, {user.name}!", 'success')
            return redirect(url_for('dashboard'))  # redirect صح بدل render

        msg = 'Invalid email or password.'
        return render_template('login.html', msg=msg)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    user  = get_current_user()
    today = date.today().isoformat()

    if user.role == 'patient':
        appointments = Appointment.query.filter_by(patient_id=user.id)\
                                        .order_by(Appointment.created_at.desc()).all()
        return render_template('dashboard.html', user=user, appointments=appointments)

    elif user.role == 'doctor':
        appointments   = Appointment.query.filter_by(doctor_id=user.id)\
                                          .order_by(Appointment.date).all()
        today_count    = Appointment.query.filter_by(doctor_id=user.id, date=today).count()
        total_patients = len({a.patient_id for a in appointments})
        return render_template('dashboard.html', user=user, appointments=appointments,
                               today_count=today_count, total_patients=total_patients)

    else:
        appointments       = Appointment.query.order_by(Appointment.created_at.desc()).all()
        total_patients     = User.query.filter_by(role='patient').count()
        total_doctors      = User.query.filter_by(role='doctor').count()
        total_appointments = Appointment.query.count()
        today_count        = Appointment.query.filter_by(date=today).count()
        recent_users       = User.query.order_by(User.created_at.desc()).limit(8).all()
        return render_template('dashboard.html', user=user, appointments=appointments,
                               total_patients=total_patients, total_doctors=total_doctors,
                               total_appointments=total_appointments, today_count=today_count,
                               recent_users=recent_users)


@app.route('/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    user        = get_current_user()
    departments = Department.query.all()
    doctors     = User.query.filter_by(role='doctor').all()
    today       = date.today().isoformat()

    if request.method == 'POST':
        appt = Appointment(
            patient_id    = user.id,
            doctor_id     = int(request.form['doctor_id']),
            department_id = int(request.form['department_id']),
            date          = request.form['date'],
            time          = request.form['time'],
            reason        = request.form.get('reason', ''),
        )
        db.session.add(appt)
        db.session.commit()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('book.html', user=user, departments=departments,
                           doctors=doctors, today=today)


@app.route('/appointment/<int:appt_id>/update', methods=['POST'])
@login_required
def update_appointment(appt_id):
    user = get_current_user()
    appt = db.session.get(Appointment, appt_id)
    if user.role in ('doctor', 'admin'):
        appt.status = request.form.get('status')
        appt.notes  = request.form.get('notes', '')
        db.session.commit()
        flash('Appointment updated.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/appointment/<int:appt_id>/cancel', methods=['POST'])
@login_required
def cancel_appointment(appt_id):
    user = get_current_user()
    appt = db.session.get(Appointment, appt_id)
    if appt.patient_id == user.id or user.role == 'admin':
        appt.status = 'cancelled'
        db.session.commit()
        flash('Appointment cancelled.', 'info')
    return redirect(url_for('dashboard'))


@app.route('/departments')
def departments():
    user  = get_current_user()
    depts = Department.query.all()
    return render_template('departments.html', user=user, departments=depts)


@app.route('/doctors')
def doctors():
    user    = get_current_user()
    doctors = User.query.filter_by(role='doctor').all()
    return render_template('doctors.html', user=user, doctors=doctors)


@app.route('/messages')
@login_required
def messages():
    user = get_current_user()
    sent_ids     = {m.receiver_id for m in user.sent_messages}
    received_ids = {m.sender_id   for m in user.received_messages}
    contact_ids  = sent_ids | received_ids

    if user.role == 'patient':
        contact_ids |= {a.doctor_id  for a in user.appointments}
    elif user.role == 'doctor':
        contact_ids |= {a.patient_id for a in user.doctor_appointments}

    contacts = []
    for cid in contact_ids:
        c = db.session.get(User, cid)
        if c:
            c.has_unread = Message.query.filter_by(
                sender_id=cid, receiver_id=user.id, is_read=False).count() > 0
            contacts.append(c)

    with_id  = request.args.get('with', type=int)
    active_contact = None
    thread         = []
    if with_id:
        active_contact = db.session.get(User, with_id)
        if active_contact:
            thread = Message.query.filter(
                ((Message.sender_id == user.id)   & (Message.receiver_id == with_id)) |
                ((Message.sender_id == with_id)   & (Message.receiver_id == user.id))
            ).order_by(Message.created_at).all()
            Message.query.filter_by(
                sender_id=with_id, receiver_id=user.id, is_read=False
            ).update({'is_read': True})
            db.session.commit()

    return render_template('messages.html', user=user, contacts=contacts,
                           active_contact=active_contact, thread=thread)


@app.route('/messages/send', methods=['POST'])
@login_required
def send_message():
    user        = get_current_user()
    receiver_id = int(request.form['receiver_id'])
    content     = request.form['content'].strip()
    if content:
        db.session.add(Message(sender_id=user.id, receiver_id=receiver_id, content=content))
        db.session.commit()
    return redirect(url_for('messages', **{'with': receiver_id}))


@app.route('/my-patients')
@login_required
def my_patients():
    user = get_current_user()
    if user.role != 'doctor':
        return redirect(url_for('dashboard'))
    appts       = Appointment.query.filter_by(doctor_id=user.id).all()
    patient_ids = {a.patient_id for a in appts}
    patients    = [db.session.get(User, pid) for pid in patient_ids if db.session.get(User, pid)]
    return render_template('my_patients.html', user=user, patients=patients, appointments=appts)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_current_user()
    if request.method == 'POST':
        user.name  = request.form['name'].strip()
        user.phone = request.form.get('phone', '').strip()
        if user.role == 'doctor':
            user.specialty = request.form.get('specialty', '').strip()
            user.bio       = request.form.get('bio', '').strip()
        new_pwd = request.form.get('new_password', '').strip()
        if new_pwd:
            user.set_password(new_pwd)
        session['username'] = user.name
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)


@app.route('/admin/users')
@login_required
def admin_users():
    user = get_current_user()
    if user.role != 'admin':
        return redirect(url_for('dashboard'))
    role  = request.args.get('role', '')
    query = User.query
    if role:
        query = query.filter_by(role=role)
    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', user=user, users=users, selected_role=role)


@app.route('/admin/add-doctor', methods=['GET', 'POST'])
@login_required
def admin_add_doctor():
    user = get_current_user()
    if user.role != 'admin':
        return redirect(url_for('dashboard'))
    departments = Department.query.all()
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('admin_add_doctor'))
        doc = User(
            name          = request.form['name'].strip(),
            email         = email,
            phone         = request.form.get('phone', '').strip(),
            role          = 'doctor',
            specialty     = request.form.get('specialty', '').strip(),
            department_id = request.form.get('department_id', type=int),
            bio           = request.form.get('bio', '').strip(),
        )
        doc.set_password(request.form['password'])
        db.session.add(doc)
        db.session.commit()
        flash(f'Doctor {doc.name} added successfully.', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin_add_doctor.html', user=user, departments=departments)


@app.route('/admin/user/<int:uid>/toggle', methods=['POST'])
@login_required
def admin_toggle_user(uid):
    user   = get_current_user()
    if user.role != 'admin':
        return redirect(url_for('dashboard'))
    target = db.session.get(User, uid)
    if target and target.role != 'admin':
        target.is_active = not target.is_active
        db.session.commit()
        flash(f'User {"enabled" if target.is_active else "disabled"}.', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/appointments')
@login_required
def admin_appointments():
    user = get_current_user()
    if user.role != 'admin':
        return redirect(url_for('dashboard'))
    status = request.args.get('status', '')
    query  = Appointment.query
    if status:
        query = query.filter_by(status=status)
    appointments = query.order_by(Appointment.date.desc()).all()
    return render_template('admin_appointments.html', user=user,
                           appointments=appointments, selected_status=status)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_initial_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
