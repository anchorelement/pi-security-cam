import os
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid

SUBJECT = "Motion Detected"
BODY = "Motion detected screenshot"
SENDER = os.getenv("MOTIONCAM_SENDER")
PW = os.getenv("MOTIONCAM_PW")
RECIPIENT = os.getenv("MOTIONCAM_RECIPIENT")


def send_mail(file_attach):
    msg = EmailMessage()
    msg["subject"] = SUBJECT
    msg["From"] = SENDER
    msg["To"] = RECIPIENT
    attachment_cid = make_msgid()
    msg.set_content(
        f'<b>{BODY}</b><br/><img src="cid:{attachment_cid[1:-1]}"/><br/>', "html"
    )

    with open(file_attach, "rb") as attachment:
        msg.add_related(attachment.read(), "image", "jpeg", cid=attachment_cid)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        smtp_server.login(SENDER, PW)
        smtp_server.sendmail(SENDER, RECIPIENT, msg.as_string())
