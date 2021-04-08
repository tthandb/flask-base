import os
from sendgrid import SendGridAPIClient


class SendGridService(object):
    def __init__(self, from_email=None):
        self.client = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        if from_email:
            self.from_email = from_email
        else:
            self.from_email = os.getenv('DEFAULT_EMAIL')

    def send_email(
        self, to_email, subject, template, data=None,
        attachments=None, from_name=None, categories=None, bcc_email=None
    ):
        try:
            message = {
                'from': {
                    'email': self.from_email
                },
                'personalizations': [
                    {
                        'to': [
                            {'email': to_email}
                        ],
                        'subject': subject,
                        'dynamic_template_data': data or {},
                    }
                ],
                'template_id': template,
            }
            if from_name:
                message['from']['name'] = from_name

            if attachments:
                new_attachments = [{
                    'type': attachment.get('type'),
                    'filename': attachment.get('filename'),
                    'content': attachment.get('content')
                } for attachment in attachments]
                message['attachments'] = new_attachments

            if categories:
                message['categories'] = categories

            if bcc_email:
                message['personalizations'][0]['bcc'] = [{
                    'email': bcc_email
                }]

            response = self.client.send(message)
            return response.status_code // 100 == 2

        except Exception:
            return False

    def send_email_with_cc(self, to_email, subject="", content="",
                   attachments=None, cc_email="", cc_name=""):
        try:
            message = {
                'from': {
                    'email': self.from_email
                },
                'personalizations': [
                    {
                        'to': [
                            {'email': to_email}
                        ],
                        'subject': subject,
                    }
                ],
                "content": [
                    {
                      "type": "text/html",
                      "value": content
                    }
                ]
            }

            if attachments:
                new_attachments = [{
                    'type': attachment.get('type'),
                    'filename': attachment.get('filename'),
                    'content': attachment.get('content')
                } for attachment in attachments]
                message['attachments'] = new_attachments

            response = self.client.send(message)
            return response.status_code // 100 == 2, None

        except Exception as e:
            return False, str(e)
