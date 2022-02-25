import os
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

account_sid = os.environ["ACCOUNT_SID"]
auth_token = os.environ["AUTH_TOKEN"]
sendgrid_api = os.environ["SENDGRID_API"]

#twilio_client = Client(account_sid, auth_token)

"""
twilio_client.messages.create(
    to = os.environ["TEST_NUMBER"],
    from_= "+19035609492",
    body = "test message :D"
)
"""

"""
message = Mail(from_email="EpicLegitPlayer@tutanota.com",
               to_emails="EpicLegitPlayer@gmail.com",
               subject="This is a test message2",
               plain_text_content="This is a test content2")

try:
    sg = SendGridAPIClient(sendgrid_api)
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)

except Exception as e:
    print(e)
"""

