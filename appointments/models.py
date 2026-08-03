from django.db import models


# -----------------------------
# Patient Model
# -----------------------------
class Patient(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    def __str__(self):
        return self.name


# -----------------------------
# Provider Model
# -----------------------------
class Provider(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# -----------------------------
# Appointment Model
# -----------------------------
class Appointment(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="appointments",
    )

    appointment_date = models.DateField()

    appointment_time = models.TimeField()

    appointment_type = models.CharField(
        max_length=100
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # Used for Problem 1 (Optimistic Locking)
    version = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.patient.name} - "
            f"{self.provider.name} - "
            f"{self.appointment_date}"
        )


# -----------------------------
# Appointment History
# Problem 2
# -----------------------------
class AppointmentHistory(models.Model):

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="history",
    )

    previous_status = models.CharField(
        max_length=20
    )

    new_status = models.CharField(
        max_length=20
    )

    previous_date = models.DateField()

    previous_time = models.TimeField()

    new_date = models.DateField()

    new_time = models.TimeField()

    changed_by = models.CharField(
        max_length=20
    )

    changed_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.appointment.id} "
            f"{self.previous_status} -> {self.new_status}"
        )