import os
import smtplib
import logging
from email.message import EmailMessage
from email.utils import make_msgid

SUBJECT = "Motion Detected"
BODY = "Motion detected screenshot"
SENDER = os.getenv("MOTIONCAM_SENDER")
PW = os.getenv("MOTIONCAM_PW")
RECIPIENT = os.getenv("MOTIONCAM_RECIPIENT")

logger = logging.getLogger(__name__)


def send_mail(file_attach: str) -> None:
    msg = EmailMessage()
    msg["subject"] = SUBJECT
    msg["From"] = SENDER
    msg["To"] = RECIPIENT
    attachment_cid = make_msgid()
    msg.set_content(
        f'<b>{BODY}</b><br/><img src="cid:{attachment_cid[1:-1]}"/><br/>', "html"
    )
    try:
        attachment = open(file_attach, "rb")
        msg.add_related(attachment.read(), "image", "jpeg", cid=attachment_cid)
    except IOError as e:
        logging.info(type(e))
        logging.info(e)
    try:
        smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtp_server.login(SENDER, PW)
        smtp_server.sendmail(SENDER, RECIPIENT, msg.as_string())
    except Exception as e:
        logging.info(type(e))
        logging.info(e)
