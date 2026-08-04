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




def cancel_appointment(request, appointment_id):
    """
    Patient can cancel only CONFIRMED appointments.
    Pending appointments cannot be cancelled.
    """

    patient = Patient.objects.first()

    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient=patient,
    )

    # Only confirmed appointments can be cancelled
    if appointment.status != "confirmed":

        messages.error(
            request,
            "Only confirmed appointments can be cancelled."
        )

        return redirect("patient_dashboard")

    # Save history before updating
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

    appointment.status = "cancelled"
    appointment.version += 1 # solving 1 problem using optimistic locking by increment the version at each update 
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

    if appointment.status != "pending":

        messages.error( 
            request,
            "Appointment is already processed."
        )

        return redirect("provider_dashboard")

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

    appointment.status = "confirmed"

    appointment.version += 1 # once provider confirmed appoinment version column increment with the change of appoinmwnt in databse with new appoinment detials with new version

    appointment.save()

    messages.success(
        request,
        "Appointment confirmed successfully."
    )

    return redirect("provider_dashboard")


#provider reschedule the appoinment 

@transaction.atomic
def reschedule_appointment(request, appointment_id):

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

            updated = form.save(commit=False)

            AppointmentHistory.objects.create(   #appointment history table stored the changes made by patient daoctor or provider to track the aduit trial log 
                appointment=appointment,
                previous_status=appointment.status,
                new_status=updated.status,
                previous_date=appointment.appointment_date,
                previous_time=appointment.appointment_time,
                new_date=updated.appointment_date,
                new_time=updated.appointment_time,
                changed_by="Provider",
            )

            updated.version += 1 # 

            updated.save() # every update create the history row nothing is overwritten 

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
            "form": form
        },
    )

#However, the code above only increments the version. It does not yet check whether the version submitted by the user matches the current version in the database.

# To fully implement optimistic locking, we need to:

# Include a hidden version field in the form.
# Compare the submitted version with the database version.
# Reject the update if they differ.