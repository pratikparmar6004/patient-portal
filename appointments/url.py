from django.urls import path

from . import views

urlpatterns = [

    # Home Page
    path(
        "",
        views.home,
        name="home",
    ),

    # Patient Dashboard
    path(
        "patient/",
        views.patient_dashboard,
        name="patient_dashboard",
    ),

    # Provider Dashboard
    path(
        "provider/",
        views.provider_dashboard,
        name="provider_dashboard",
    ),

    # Request Appointment
    path(
        "request/",
        views.request_appointment,
        name="request_appointment",
    ),

    # Cancel Appointment
    path(
        "cancel/<int:appointment_id>/",
        views.cancel_appointment,
        name="cancel_appointment",
    ),

    # Confirm Appointment
    path(
        "confirm/<int:appointment_id>/",
        views.confirm_appointment,
        name="confirm_appointment",
    ),

    # Reschedule Appointment
    path(
        "reschedule/<int:appointment_id>/",
        views.reschedule_appointment,
        name="reschedule_appointment",
    ),
]