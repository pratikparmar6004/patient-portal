import threading
from .notifications import send_confirmation_notification
from django.contrib import messages

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    AppointmentRequestForm,
    ProviderAppointmentUpdateForm,
)
from .models import (
    Appointment,
    AppointmentHistory,
    Patient,
    Provider,
)


def home(request):
    """
    Landing page.
    User selects whether they are
    Patient or Provider.
    """

    return render(
        request,
        "home.html",
    )


def request_appointment(request):
    """
    Patient requests a new appointment.
    """

    # Temporary patient until authentication is added
    patient = Patient.objects.first()

    if request.method == "POST":

        form = AppointmentRequestForm(request.POST)

        if form.is_valid():

            appointment = form.save(commit=False)

            appointment.patient = patient

            appointment.status = "pending"

            appointment.save()

            messages.success(
                request,
                "Appointment request submitted successfully."
            )

            return redirect("patient_dashboard")

    else:

        form = AppointmentRequestForm()

    return render(
        request,
        "appointment_form.html",
        {
            "form": form,
        },
    )


def patient_dashboard(request):
    """
    Displays all appointments for a patient.
    """

    # Temporary patient until authentication is added
    patient = Patient.objects.first()

    appointments = (
        Appointment.objects
        .filter(patient=patient)
        .order_by("appointment_date", "appointment_time")
    )

    context = {
        "patient": patient,
        "appointments": appointments,
    }

    return render(
        request,
        "patient_dashboard.html",
        context,
    )

def provider_dashboard(request):
    """
    Displays all appointments for a provider.
    """

    provider = Provider.objects.first()

    appointments = (
        Appointment.objects
        .filter(provider=provider)
        .order_by("appointment_date", "appointment_time")
    )

    context = {
        "provider": provider,
        "appointments": appointments,
    }

    return render(
        request,
        "provider_dashboard.html",
        context,
    )




@transaction.atomic
def cancel_appointment(request, appointment_id):
    """
    Patient can cancel only CONFIRMED appointments.
    Implements Optimistic Locking (Problem 1).
    """

    patient = Patient.objects.first()

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=patient,
    )

    # Check if appointment is confirmed
    if appointment.status != "confirmed":

        messages.error(
            request,
            "Only confirmed appointments can be cancelled."
        )

        return redirect("patient_dashboard")

    # ---------- Problem 1 : Optimistic Locking ----------
    submitted_version = int(
        request.POST.get(
            "version",
            appointment.version,
        )
    )

    if submitted_version != appointment.version: # checking if the submitted version is same is of appointment version

        messages.error(
            request,
            "This appointment has already been modified by the provider. Please refresh the page."
        )

        return redirect("patient_dashboard")
    # ----------------------------------------------------

    # Save appointment history (Problem 2)
    AppointmentHistory.objects.create(
        appointment=appointment,
        previous_status=appointment.status,
        new_status="cancelled",
        previous_date=appointment.appointment_date,
        previous_time=appointment.appointment_time,
        new_date=appointment.appointment_date,
        new_time=appointment.appointment_time,
        changed_by="Patient",
    )

    # Update appointment
    appointment.status = "cancelled"

    # Increment version after successful update
    appointment.version += 1

    appointment.save()

    messages.success(
        request,
        "Appointment cancelled successfully."
    )

    return redirect("patient_dashboard")


# provider confirm appoinment 


@transaction.atomic
def confirm_appointment(request, appointment_id):
    """
    Provider confirms an appointment.
    """

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
    )

    # -------- Problem 1 --------
    submitted_version = int(     # getting the submitted version as well broswer version   
        request.POST.get(
            "version",
            appointment.version,
        )
    )
    if submitted_version != appointment.version: # if the version of both dosent match provide errr message

        messages.error(
            request,
            "This appointment was modified by another user. Please refresh the page."
        )

        return redirect("provider_dashboard")

    if appointment.status != "pending":

        messages.error( 
            request,
            "Appointment is already processed."
        )

        return redirect("provider_dashboard")

    AppointmentHistory.objects.create( # since version are not same then the request is rejected these solve the problem 2 of This solves Problem 2 by recording the previous state before making changes and save in  the history  table for audit logs
        appointment=appointment,
        previous_status=appointment.status,
        new_status="confirmed",
        previous_date=appointment.appointment_date,
        previous_time=appointment.appointment_time,
        new_date=appointment.appointment_date,
        new_time=appointment.appointment_time,
        changed_by="Provider",
    )

    appointment.status = "confirmed"

    appointment.version += 1 #To properly implement optimistic locking, we need to:
                            # Add a hidden version field to the form.
                            # Compare the submitted version with the current database version.
                            # Reject stale updates if the versions don't match. once provider confirmed appoinment version column increment with the change of appoinmwnt in databse with new appoinment detials with new version

    appointment.save()

    # Start background notification. since appointment is saved with confirmed status sned notifiaction in backgroung
    # solving the problem 3

    threading.Thread(
        target=send_confirmation_notification,
        args=(appointment,),
        daemon=True,
    ).start()



    messages.success(
        request,
        "Appointment confirmed successfully."
    )

    return redirect("provider_dashboard")


#provider reschedule the appoinment 

@transaction.atomic

def reschedule_appointment(request, appointment_id):
    """
    Provider can reschedule an appointment.
    Implements Optimistic Locking (Problem 1).
    """

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
    )

    if request.method == "POST":

        form = ProviderAppointmentUpdateForm(
            request.POST,
            instance=appointment,
        )

        if form.is_valid():

            # Version submitted by the browser
            submitted_version = form.cleaned_data["version"]

            # -------- Problem 1 --------
            if submitted_version != appointment.version:

                messages.error(
                    request,
                    "This appointment has already been updated by another user. Please refresh the page."
                )

                return redirect("provider_dashboard")

            # --------------------------

            updated = form.save(commit=False)

            # Save history before updating
            AppointmentHistory.objects.create(
                appointment=appointment,
                previous_status=appointment.status,
                new_status=updated.status,
                previous_date=appointment.appointment_date,
                previous_time=appointment.appointment_time,
                new_date=updated.appointment_date,
                new_time=updated.appointment_time,
                changed_by="Provider",
            )

            # Increment version
            updated.version += 1

            updated.save()

            messages.success(
                request,
                "Appointment updated successfully."
            )

            return redirect("provider_dashboard")

    else:

        form = ProviderAppointmentUpdateForm(
            instance=appointment
        )

    return render(
        request,
        "appointment_form.html",
        {
            "form": form,
        },
    )
#However, the code above only increments the version. It does not yet check whether the version submitted by the user matches the current version in the database.

# To fully implement optimistic locking, we need to:

# Include a hidden version field in the form.
# Compare the submitted version with the database version.
# Reject the update if they differ.