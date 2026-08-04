import logging
import time

# Create logger
logger = logging.getLogger(__name__)


def send_confirmation_notification(appointment):
    """
    Stub notification function.

    Runs in the background after the appointment
    has already been confirmed.
    """

    try:

        # Simulate slow email server
        time.sleep(3)

        logger.info(
            f"""
            ======================================
            WOULD SEND EMAIL

            To      : {appointment.patient.email}
            Patient : {appointment.patient.name}

            Subject : Appointment Confirmed

            Message :
            Dear {appointment.patient.name},

            Your appointment with
            {appointment.provider.name}
            on {appointment.appointment_date}
            at {appointment.appointment_time}
            has been confirmed.

            ======================================
            """
        )

    except Exception as e:

        logger.error(
            f"Notification failed: {e}"
        )