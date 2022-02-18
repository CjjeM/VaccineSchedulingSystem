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

        cursor.execute("""CREATE TABLE IF NOT EXISTS User_Information (
            user_id int NOT NULL AUTO_INCREMENT,
            first_name varchar(50) NOT NULL,
            middle_name varchar(50) NOT NULL,
            last_name varchar(50) NOT NULL,
            region varchar(255) NOT NULL,
            province varchar(255) NOT NULL,
            city varchar(255) NOT NULL,
            home_address varchar(255) NOT NULL,
            birthdate date NOT NULL,
            contact_number numeric(11) NOT NULL,
            email_address varchar(50) NOT NULL,
            pwd varchar(255) NOT NULL,
            PRIMARY KEY (user_id)
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS Vaccine (
            vaccine_id int NOT NULL AUTO_INCREMENT,
            vaccine_name varchar(50) NOT NULL,
            PRIMARY KEY (vaccine_id)
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS Hospital (
            hosp_id int NOT NULL AUTO_INCREMENT,
            hosp_name varchar(100) NOT NULL,
            hosp_address varchar(255) NOT NULL,
            PRIMARY KEY (hosp_id)
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS Availability_Details (
            id int NOT NULL AUTO_INCREMENT,
            hosp_id int,
            vaccine_id int,
            availability_date date NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (hosp_id) REFERENCES Hospital(hosp_id),
            FOREIGN KEY (vaccine_id) REFERENCES Vaccine(vaccine_id)
        )""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS Appointment (
            id int NOT NULL AUTO_INCREMENT,
            user_id int,
            availability_id int,
            PRIMARY KEY (id),
            FOREIGN KEY (user_id) REFERENCES User_Information(user_id),
            FOREIGN KEY (availability_id) REFERENCES Availability_Details(id)
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
    
    def add_user(self, email, password):
        self.open_connection()

        self.session.execute("INSERT INTO users (email, password) VALUES (%s, %s)",
                            (email, password))

        self.connection.commit()

        self.close_connection()

    def isEmailExists(self, email):
        pass
