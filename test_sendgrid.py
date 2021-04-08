from middlewares.sendgrid_email import SendGridService


if __name__ == '__main__':
    sendgrid_service = SendGridService(from_email='')
    sendgrid_service.send_email(
        to_email='example@wecella.com',
        subject='Confirm email',
        template='d-example',
        data={
          "id": "#1002",
        }
    )
