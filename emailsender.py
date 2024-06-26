import smtplib
from email.mime.text import MIMEText

def send_email(sender_email, receiver_email, password, subject, body):
    """
    Sends an email using Gmail's SMTP server.

    Args:
        sender_email (str): The email address of the sender.
        receiver_email (str): The email address of the recipient.
        password (str): The password for the sender's email account.
        subject (str): The subject line of the email.
        body (str): The body of the email.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email

        server = smtplib.SMTP("smtp.office365.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        print("Email sent successfully")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False