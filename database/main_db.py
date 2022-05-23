import mysql.connector

class mysqldb:
    def __init__(self):
        self.connection = None
        self.session = None
    
    # use this function to initialize the database and its tables
    def _init_db(self):
        db = mysql.connector.connect(
            host='localhost',
            user='vaccinedb',
            password='vaccine'
        )

        cursor = db.cursor()

        cursor.execute("CREATE DATABASE IF NOT EXISTS vaccinedb")

        cursor.execute("USE vaccinedb")

        cursor.execute("""CREATE TABLE IF NOT EXISTS Hospital (
            hosp_id int NOT NULL AUTO_INCREMENT,
            hosp_name varchar(100) NOT NULL,
            hosp_address varchar(255) NOT NULL,
            PRIMARY KEY (hosp_id)
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS Vaccine (
            vaccine_id int NOT NULL AUTO_INCREMENT,
            vaccine_name varchar(50) NOT NULL,
            hosp_id int,
            vaccine_expiration varchar(50) NOT NULL,
            vaccine_manufacturer varchar(50) NOT NULL,
            vaccine_supplier varchar(50) NOT NULL,
            vaccine_information varchar(1000),
            vaccine_type varchar(50) NOT NULL,
            PRIMARY KEY (vaccine_id),
            FOREIGN KEY (hosp_id) REFERENCES Hospital(hosp_id)
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS Availability_Details (
            avail_id int NOT NULL AUTO_INCREMENT,
            vaccine_id int,
            hosp_id int,
            availability_date date NOT NULL,
            availability_time1 time NOT NULL,
            availability_time2 time NOT NULL,
            PRIMARY KEY (avail_id),
            FOREIGN KEY (hosp_id) REFERENCES Hospital(hosp_id),
            FOREIGN KEY (vaccine_id) REFERENCES Vaccine(vaccine_id)
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS User_Information (
            user_id int NOT NULL AUTO_INCREMENT,
            first_name varchar(50) NOT NULL,
            middle_name varchar(50) NOT NULL,
            last_name varchar(50) NOT NULL,
            city varchar(255) NOT NULL,
            home_address varchar(255) NOT NULL,
            birthdate date NOT NULL,
            contact_number varchar(50) NOT NULL,
            email_address varchar(50) NOT NULL,
            pwd varchar(255) NOT NULL,
            schedule int,
            dose_count int,
            booster_count int,
            next_shot date,
            PRIMARY KEY (user_id)
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS Appointment (
            appoint_id int NOT NULL AUTO_INCREMENT,
            user_id int,
            avail_id int,
            PRIMARY KEY (appoint_id),
            FOREIGN KEY (user_id) REFERENCES User_Information(user_id),
            FOREIGN KEY (avail_id) REFERENCES Availability_Details(avail_id)
        )""")

        db.commit()

        cursor.close()
        db.close()
        
    def open_connection(self):
        db = mysql.connector.connect(
            host='localhost',
            user='vaccinedb',
            password='vaccine',
            database='vaccinedb'
        )

        self.connection = db
        self.session = db.cursor()
    
    def close_connection(self):
        self.session.close()
        self.connection.close()


db = mysqldb()
db._init_db()