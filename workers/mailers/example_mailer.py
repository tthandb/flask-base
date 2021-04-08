import os
import datetime
import pytz
import urllib.parse
import json
from workers.base_worker import BaseWorker, connect_database
from middlewares.sendgrid_email import SendGridService
from database.session import session_scope


class ExampleMailer(BaseWorker):
    def send_example(self, message):
        print(message)
        sendgrid_service = SendGridService(from_email="mail@example.com")
        categories = 'example'
        template_id = 'd-example'
        bcc_email = "bbc@example.com"
        sendgrid_service.send_email(
            to_email="customer_mail@example.com",
            subject='Example Email',
            template=template_id,
            data=confirm_order_mail_data,
            from_name="Example",
            categories=categories,
            bcc_email=bcc_email
        )
        print('FINISHED')

   