import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings


def send_email(to_email: str, subject: str, body: str):
    """Send an email notification"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_USER
        msg["To"] = to_email

        html_part = MIMEText(body, "html")
        msg.attach(html_part)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())

        print(f"Email sent to {to_email}")
        return True

    except Exception as e:
        # Don't crash the app if email fails
        print(f"Email sending failed: {e}")
        return False


def send_booking_confirmation_email(
    guest_email: str,
    guest_name: str,
    property_title: str,
    check_in: str,
    check_out: str,
    total_amount: float
):
    """Send booking confirmation to guest"""
    subject = f"Booking Confirmed - {property_title}"
    body = f"""
    <html>
    <body>
        <h2>Booking Confirmed!</h2>
        <p>Dear {guest_name},</p>
        <p>Your booking has been confirmed.</p>
        <table border="1" cellpadding="10">
            <tr><td><b>Property</b></td><td>{property_title}</td></tr>
            <tr><td><b>Check-in</b></td><td>{check_in}</td></tr>
            <tr><td><b>Check-out</b></td><td>{check_out}</td></tr>
            <tr><td><b>Total Amount</b></td><td>₹{total_amount}</td></tr>
        </table>
        <p>Thank you for choosing our platform!</p>
    </body>
    </html>
    """
    send_email(guest_email, subject, body)


def send_booking_cancellation_email(
    guest_email: str,
    guest_name: str,
    property_title: str,
    check_in: str,
    check_out: str
):
    """Send cancellation email to guest"""
    subject = f"Booking Cancelled - {property_title}"
    body = f"""
    <html>
    <body>
        <h2>Booking Cancelled</h2>
        <p>Dear {guest_name},</p>
        <p>Your booking has been cancelled.</p>
        <table border="1" cellpadding="10">
            <tr><td><b>Property</b></td><td>{property_title}</td></tr>
            <tr><td><b>Check-in</b></td><td>{check_in}</td></tr>
            <tr><td><b>Check-out</b></td><td>{check_out}</td></tr>
        </table>
        <p>We hope to see you again soon!</p>
    </body>
    </html>
    """
    send_email(guest_email, subject, body)


def send_payment_confirmation_email(
    guest_email: str,
    guest_name: str,
    amount: float,
    property_title: str
):
    """Send payment confirmation to guest"""
    subject = "Payment Confirmed - Vacation Rental"
    body = f"""
    <html>
    <body>
        <h2>Payment Confirmed!</h2>
        <p>Dear {guest_name},</p>
        <p>Your payment has been received.</p>
        <table border="1" cellpadding="10">
            <tr><td><b>Property</b></td><td>{property_title}</td></tr>
            <tr><td><b>Amount Paid</b></td><td>₹{amount}</td></tr>
        </table>
        <p>Enjoy your stay!</p>
    </body>
    </html>
    """
    send_email(guest_email, subject, body)


def send_host_booking_notification(
    host_email: str,
    host_name: str,
    guest_name: str,
    property_title: str,
    check_in: str,
    check_out: str,
    total_amount: float
):
    """Notify host about new booking"""
    subject = f"New Booking - {property_title}"
    body = f"""
    <html>
    <body>
        <h2>New Booking Received!</h2>
        <p>Dear {host_name},</p>
        <p>You have a new booking for your property.</p>
        <table border="1" cellpadding="10">
            <tr><td><b>Property</b></td><td>{property_title}</td></tr>
            <tr><td><b>Guest</b></td><td>{guest_name}</td></tr>
            <tr><td><b>Check-in</b></td><td>{check_in}</td></tr>
            <tr><td><b>Check-out</b></td><td>{check_out}</td></tr>
            <tr><td><b>Total Amount</b></td><td>₹{total_amount}</td></tr>
        </table>
    </body>
    </html>
    """
    send_email(host_email, subject, body)