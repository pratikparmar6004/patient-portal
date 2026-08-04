from django import forms
from .models import Appointment


class AppointmentRequestForm(forms.ModelForm):
    """
    Form used by the Patient to request a new appointment.
    """

    class Meta:
        model = Appointment

        fields = [
            "provider",
            "appointment_date",
            "appointment_time",
            "appointment_type",
            "reason",
        ]

        widgets = {
            "appointment_date": forms.DateInput(
                attrs={"type": "date"}
            ),

            "appointment_time": forms.TimeInput(
                attrs={"type": "time"}
            ),

            "reason": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Reason for visit"
                }
            ),
        }


class ProviderAppointmentUpdateForm(forms.ModelForm):
    """
    Used by the Provider to
    1. Confirm
    2. Reschedule
    """

    class Meta:
        model = Appointment

        fields = [
            "appointment_date",
            "appointment_time",
            "status",
        ]

        widgets = {

            "appointment_date": forms.DateInput(
                attrs={"type": "date"}
            ),

            "appointment_time": forms.TimeInput(
                attrs={"type": "time"}
            ),
        }

    def clean(self):
        """
        Custom Validation
        """

        cleaned_data = super().clean()

        status = cleaned_data.get("status")

        if status not in [
            "pending",
            "confirmed",
            "cancelled",
        ]:
            raise forms.ValidationError(
                "Invalid appointment status."
            )

        return cleaned_data