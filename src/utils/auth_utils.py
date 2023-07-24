import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
from src.constants import SENDGRID_API_KEY, SENDGRID_EMAIL


async def send_email(recipient: str):
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(SENDGRID_EMAIL)  # Change to your verified sender
    to_email = To(recipient)  # Change to your recipient
    subject = "Test Email from FastAPI"
    # send html content
    content = Content(
        "text/html",
        "<html><body><h1>Test Email from FastAPI</h1><p>This is a test email from FastAPI</p></body></html>",
    )
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)
    return {"res": response}
