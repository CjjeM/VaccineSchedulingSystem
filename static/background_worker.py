from models.models import user_information, hospital, vaccine, availability_details, appointment
from datetime import datetime
import os
from twilio.rest import Client

class Worker:

    def __init__(self, db_obj):
        self.db = db_obj
    
    def notify(self):
        # combines all data then filters
        # retrieve data if the schedule is not null and not notified
        data = self.db.session.query(user_information, appointment, availability_details, hospital, vaccine)\
            .join(appointment, appointment.user_id == user_information.user_id)\
            .join(availability_details, appointment.avail_id == availability_details.avail_id)\
            .join(hospital, hospital.hosp_id == availability_details.hosp_id)\
            .join(vaccine, vaccine.vaccine_id == availability_details.vaccine_id)\
            .filter(user_information.schedule.isnot(None))\
            .filter(user_information.notified == 0)\
            .all()

        current_date = datetime.now().date()

        for user in data:
            # check date difference
            scheduled_date = user.availability_details.availability_date
            delta = scheduled_date - current_date
            print(delta.days)
            if delta.days != 1: 
                continue

            # send sms a day before the scheduled date
            self.send_sms(user)
            user.user_information.notified = 1
            self.db.session.commit()
            
            

    def send_sms(self, user):
        account_sid = os.environ["ACCOUNT_SID"]
        auth_token = os.environ["AUTH_TOKEN"]

        message = f"""REMINDER!!! Here are the details of your appointment tomorrow:
        Hospital Name: {user.hospital.hosp_name}
        Hospital Address: {user.hospital.hosp_address}
        Vaccine to Administer: {user.vaccine.vaccine_name}
        Expected Date of Vaccination: {user.availability_details.availability_date}
        Site opens at: {user.availability_details.availability_time1}
        Site closes at: {user.availability_details.availability_time2}
        
        Registration Code: {user.user_information.schedule}"""

        twilio_client = Client(account_sid, auth_token)
        twilio_client.messages.create(
            to = user.user_information.contact_number,
            from_= "+19035609492",
            body = message
        )
