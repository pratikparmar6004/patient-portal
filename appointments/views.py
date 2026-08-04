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
    provider = Provider.objects.first()

    if request.method == "POST":

        form = AppointmentRequestForm(request.POST)

        if form.is_valid():

            appointment = form.save(commit=False)

            appointment.patient = patient
            appointment.provider = provider
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

    # Lock the appointment row (Problem 4)
    appointment = (
        Appointment.objects
        .select_for_update()
        .get(id=appointment_id)
    )

    # -------- Problem 1 --------
    # Get the version submitted by the browser.
    submitted_version = int(
        request.POST.get(
            "version",
            appointment.version,
        )
    )

    # Compare submitted version with database version.
    if submitted_version != appointment.version:

        messages.error(
            request,
            "This appointment was modified by another user. Please refresh the page."
        )

        return redirect("provider_dashboard")

    # Appointment must still be pending.
    if appointment.status != "pending":

        messages.error(
            request,
            "Appointment is already processed."
        )

        return redirect("provider_dashboard")

    # -------- Problem 4 --------
    # Check whether the provider already has another appointment at same time 
    # conflict detection this checks whether the provider already has another confirmed appointment at the same date and time.
    conflict = Appointment.objects.filter(
        provider=appointment.provider,
        appointment_date=appointment.appointment_date,
        appointment_time=appointment.appointment_time,
        status="confirmed",
    ).exclude(
        id=appointment.id,
    ).exists()
    
    #This stops the confirmation, making overlapping confirmed appointments impossible through this confirmation flow.
    if conflict:

        messages.error(
            request,
            "Provider already has another confirmed appointment at this time."
        )

        return redirect("provider_dashboard")

    # -------- Problem 2 --------
    # Save appointment history before updating.
    AppointmentHistory.objects.create(
        appointment=appointment,
        previous_status=appointment.status,
        new_status="confirmed",
        previous_date=appointment.appointment_date,
        previous_time=appointment.appointment_time,
        new_date=appointment.appointment_date,
        new_time=appointment.appointment_time,
        changed_by="Provider",
    )

    # Update appointment.
    appointment.status = "confirmed"

    # Increment version for optimistic locking.
    appointment.version += 1

    appointment.save()

    # -------- Problem 3 --------
    # Start notification in the background.
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