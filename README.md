# patirnt-portal-


# Patient Portal Web Application

## Overview

This project is a minimal Patient Portal web application built using **Python**, **Django**, and **SQLite**.

The application allows patients to request and manage appointments while providers can confirm or reschedule those appointments. It also demonstrates solutions to common backend engineering problems such as concurrency handling, audit history, optimistic locking, and asynchronous notifications.

This project was developed as a take-home assignment.

---

# Technology Stack

* Python 3.13
* Django 6.x
* SQLite
* Bootstrap 5
* HTML
* CSS

---

# Features

## Patient

* View upcoming appointments
* Request a new appointment
* Cancel confirmed appointments
* View appointment status

## Provider

* View all assigned appointments
* Confirm appointments
* Reschedule appointments
* View appointment history

---

# Appointment Status Flow

```
Pending
    │
    ▼
Confirmed
    │
    ▼
Cancelled
```

---

# Project Structure

```
patient-portal/
│
├── manage.py
├── README.md
├── db.sqlite3
│
├── patient_portal/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── appointments/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── notifications.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   └── templates/
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── patient_dashboard.html
│   ├── provider_dashboard.html
│   └── appointment_form.html
│
├── static/
│
└── venv/
```

---

# Database Models

## Patient

Stores patient information.

Fields

* Name
* Email

---

## Provider

Stores provider information.

Fields

* Name
* Email

---

## Appointment

Stores appointment details.

Fields

* Patient
* Provider
* Appointment Date
* Appointment Time
* Appointment Type
* Reason
* Status
* Version

---

## AppointmentHistory

Stores every modification made to an appointment.

Fields

* Previous Status
* New Status
* Previous Date
* New Date
* Previous Time
* New Time
* Changed By
* Changed At

---

# Role Switcher

The assignment specifies that authentication is not required.

Instead of implementing login, a simple role switcher is provided.

Users can choose:

* Patient
* Provider

The selected user is stored in the Django session.

---

# Problems Solved

## Problem 1 — Optimistic Locking

### Problem

The provider changes an appointment while the patient still sees the old data.

### Solution

A `version` field is stored with every appointment.

Each form submits the current version as a hidden field.

Before updating:

* Submitted version is compared with the current database version.
* If the versions differ, the update is rejected.
* The user is asked to refresh the page.

This prevents stale updates from overwriting newer changes.

---

## Problem 2 — Audit Trail

### Problem

Users want to know:

* Who changed an appointment?
* When was it changed?
* What was changed?

### Solution

A separate `AppointmentHistory` model stores every modification.

Every confirm, cancel, or reschedule creates a history record before updating the appointment.

Previous values are never overwritten.

This provides a complete audit trail.

---

## Problem 3 — Background Notification

### Problem

Confirming an appointment should not wait for email delivery.

### Solution

Notification sending is executed in a background thread.

```
threading.Thread(
    target=send_confirmation_notification,
    args=(appointment,),
    daemon=True,
).start()
```

The notification currently logs a message to the terminal instead of sending a real email.

Example output:

```
Would send appointment confirmation email to john@example.com
```

The appointment confirmation succeeds even if the notification fails.

---

## Problem 4 — Prevent Double Booking

### Problem

A provider cannot have two confirmed appointments at the same date and time.

### Solution

The confirmation process is wrapped inside a database transaction.

```
transaction.atomic()
```

The appointment row is locked using

```
select_for_update()
```

Before confirming, the application checks whether another confirmed appointment already exists for the same provider, date, and time.

If a conflict exists, confirmation is rejected.

Example message:

```
Provider already has another confirmed appointment at this time.
```

This guarantees that overlapping confirmed appointments cannot be created through the confirmation flow.

---

# Running the Project

## Clone Repository

```
git clone <repository-url>
```

---

## Create Virtual Environment

macOS/Linux

```
python3 -m venv venv
```

Windows

```
python -m venv venv
```

---

## Activate Environment

macOS/Linux

```
source venv/bin/activate
```

Windows

```
venv\Scripts\activate
```

---

## Install Dependencies

```
pip install django
```

---

## Apply Migrations

```
python manage.py migrate
```

---

## Create Superuser

```
python manage.py createsuperuser
```

---

## Run Development Server

```
python manage.py runserver
```

Application

```
http://127.0.0.1:8000/
```

Admin

```
http://127.0.0.1:8000/admin/
```

---

# Testing

## Patient

* Select Patient from the role switcher.
* Request an appointment.
* View appointment list.
* Cancel confirmed appointments.

---

## Provider

* Select Provider from the role switcher.
* Confirm appointments.
* Reschedule appointments.
* View appointment history.

---

## Testing Problem 4

1. Confirm one appointment for Dr. Smith at 10:00 AM.
2. Create another pending appointment for Dr. Smith at 10:00 AM.
3. Attempt to confirm the second appointment.

Expected Result

```
Provider already has another confirmed appointment at this time.
```

The second appointment remains **Pending**.

---

# Future Improvements

For a production-ready application, the following enhancements could be added:

* Django Authentication
* Email/SMS integration
* Celery with Redis for background tasks
* PostgreSQL database
* REST APIs using Django REST Framework
* Unit and integration tests
* Docker support
* CI/CD pipeline
* JWT authentication
* Calendar integration
* Time zone support
* Availability scheduling

---

# Author

Pratik Vijay Parmar
