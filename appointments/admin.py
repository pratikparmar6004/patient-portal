from django.contrib import admin
from .models import (
    Patient,
    Provider,
    Appointment,
    AppointmentHistory,
)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "email",
    )

    search_fields = (
        "name",
        "email",
    )


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "specialty",
    )

    search_fields = (
        "name",
        "specialty",
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "patient",
        "provider",
        "appointment_date",
        "appointment_time",
        "appointment_type",
        "status",
        "version",
    )

    list_filter = (
        "status",
        "appointment_date",
        "provider",
    )

    search_fields = (
        "patient__name",
        "provider__name",
        "appointment_type",
    )

    ordering = (
        "appointment_date",
        "appointment_time",
    )


@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "appointment",
        "previous_status",
        "new_status",
        "changed_by",
        "changed_at",
    )

    ordering = (
        "-changed_at",
    )