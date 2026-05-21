# 🏥 MediBook — Hospital Appointment System

A full-featured web application built with **Flask** and **MySQL**, allowing patients to book appointments, doctors to manage their schedules, and admins to oversee the entire system.

---

## 👥 Team Members

| # | Name |
|---|------|
| 1 | Israa Mahmoud Mohamed Saleh |
| 2 | Shahd Mohamed Mahmoud |
| 3 | Mayar Yasser Abbas |
| 4 | Fatma Mahrous Mohamed Amin |


---

## 🎯 Objective
Design and implement a simple web application demonstrating the Flask framework and database principles, featuring user authentication, role-based access control, and a complete appointment management workflow.

---

## ⚙️ Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Language   | Python 3.11+                      |
| Framework  | Flask 3.0                         |
| Database   | MySQL (via SQLAlchemy + PyMySQL)  |
| Frontend   | Jinja2 + CSS + FontAwesome 6      |
| Auth       | Werkzeug password hashing         |

---

## 🗄️ Database Tables (4 Tables)

### 1. `department`
| Column      | Type         | Description             |
|-------------|--------------|-------------------------|
| id          | INT (PK)     | Primary Key             |
| name        | VARCHAR(100) | Department name (unique)|
| description | TEXT         | Department description  |

### 2. `user`
| Column        | Type         | Description                    |
|---------------|--------------|--------------------------------|
| id            | INT (PK)     | Primary Key                    |
| name          | VARCHAR(100) | Full name                      |
| email         | VARCHAR(120) | Unique email (login identifier)|
| password_hash | VARCHAR(256) | Hashed password (Werkzeug)     |
| role          | VARCHAR(20)  | patient / doctor / admin       |
| phone         | VARCHAR(20)  | Phone number                   |
| specialty     | VARCHAR(100) | Doctor specialty (nullable)    |
| department_id | INT (FK)     | FK → department.id             |
| bio           | TEXT         | Doctor biography (nullable)    |
| is_active     | BOOLEAN      | Account active/disabled        |
| created_at    | DATETIME     | Registration timestamp         |

### 3. `appointment`
| Column        | Type         | Description                     |
|---------------|--------------|---------------------------------|
| id            | INT (PK)     | Primary Key                     |
| patient_id    | INT (FK)     | FK → user.id                    |
| doctor_id     | INT (FK)     | FK → user.id                    |
| department_id | INT (FK)     | FK → department.id              |
| date          | VARCHAR(20)  | Appointment date (YYYY-MM-DD)   |
| time          | VARCHAR(10)  | Appointment time (HH:MM)        |
| reason        | TEXT         | Reason for visit                |
| status        | VARCHAR(20)  | pending / confirmed / cancelled |
| notes         | TEXT         | Doctor notes                    |
| created_at    | DATETIME     | Booking timestamp               |

### 4. `message`
| Column      | Type         | Description              |
|-------------|--------------|--------------------------|
| id          | INT (PK)     | Primary Key              |
| sender_id   | INT (FK)     | FK → user.id             |
| receiver_id | INT (FK)     | FK → user.id             |
| content     | TEXT         | Message content          |
| is_read     | BOOLEAN      | Read/unread status       |
| created_at  | DATETIME     | Message timestamp        |

---

## 🔗 Endpoints (18 Endpoints)

| #  | Method   | Route                            | Description                     | Access         |
|----|----------|----------------------------------|---------------------------------|----------------|
| 1  | GET      | `/`                              | Home page                       | Public         |
| 2  | GET/POST | `/register`                      | User registration                | Public         |
| 3  | GET/POST | `/login`                         | User login                       | Public         |
| 4  | GET      | `/logout`                        | User logout                      | Logged in      |
| 5  | GET      | `/dashboard`                     | Role-based dashboard             | Logged in      |
| 6  | GET/POST | `/book`                          | Book a new appointment           | Patient        |
| 7  | POST     | `/appointment/<id>/update`       | Confirm appointment              | Doctor / Admin |
| 8  | POST     | `/appointment/<id>/cancel`       | Cancel an appointment            | Patient / Admin|
| 9  | GET      | `/departments`                   | List all departments             | Public         |
| 10 | GET      | `/doctors`                       | List all doctors                 | Public         |
| 11 | GET      | `/messages`                      | View messages / chat             | Logged in      |
| 12 | POST     | `/messages/send`                 | Send a message                   | Logged in      |
| 13 | GET      | `/my-patients`                   | Doctor views their patients      | Doctor         |
| 14 | GET/POST | `/profile`                       | View & edit profile              | Logged in      |
| 15 | GET      | `/admin/users`                   | Manage all users                 | Admin          |
| 16 | GET/POST | `/admin/add-doctor`              | Add a new doctor                 | Admin          |
| 17 | POST     | `/admin/user/<id>/toggle`        | Enable / disable a user          | Admin          |
| 18 | GET      | `/admin/appointments`            | View all appointments            | Admin          |

---

## 👤 User Roles

| Feature                    | Patient | Doctor | Admin |
|----------------------------|---------|--------|-------|
| Register                   | ✅      | ❌     | ❌    |
| Login                      | ✅      | ✅     | ✅    |
| View departments & doctors | ✅      | ✅     | ✅    |
| Book appointment           | ✅      | ❌     | ❌    |
| View own appointments      | ✅      | ✅     | ✅    |
| Confirm appointments       | ❌      | ✅     | ✅    |
| Cancel appointments        | ✅      | ❌     | ✅    |
| Send / receive messages    | ✅      | ✅     | ❌    |
| View all users             | ❌      | ❌     | ✅    |
| Add doctors                | ❌      | ❌     | ✅    |
| Manage all appointments    | ❌      | ❌     | ✅    |

---

## 🚀 Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/medibook.git
cd medibook

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create MySQL database
mysql -u root -p12345 -e "CREATE DATABASE IF NOT EXISTS hospital_db;"

# 5. Run the application
flask run

# 6. Open in browser
# http://localhost:5000
```

---

## 🔐 Default Admin Account

| Role  | Email                  | Password  |
|-------|------------------------|-----------|
| Admin | admin@hospital.com     | admin123  |

> Doctor accounts are created by the Admin only. Patients can self-register.

---

## 📁 Project Structure

```
medibook/
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── secret.env               # DB connection string (not pushed to GitHub)
├── .flaskenv                # Flask environment config
├── README.md                # This file
├── Dockerfile               # Docker support (Bonus)
├── static/
│   ├── css/
│   │   └── style.css        # Main unified stylesheet
│   └── js/
│       └── main.js
└── templates/
    ├── base.html            # Base layout (nav + sidebar)
    ├── index.html           # Home page
    ├── login.html           # Login
    ├── register.html        # Registration
    ├── dashboard.html       # Role-based dashboard
    ├── book.html            # Book appointment
    ├── departments.html     # Departments list
    ├── doctors.html         # Doctors list
    ├── messages.html        # Messaging system
    ├── my_patients.html     # Doctor's patients
    ├── profile.html         # User profile
    ├── admin_users.html     # Admin — manage users
    ├── admin_appointments.html  # Admin — all appointments
    └── admin_add_doctor.html    # Admin — add doctor
```

---

## 🐳 Bonus — Docker

```bash
# Build the image
docker build -t medibook .

# Run the container
docker run -p 5000:5000 medibook

# Access at http://localhost:5000
```

---

## 📄 License
MIT License — Free to use for educational purposes.