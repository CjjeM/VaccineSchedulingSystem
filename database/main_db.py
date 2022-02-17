import mysql.connector

class mysqldb:
    def __init__(self):
        self.connection = None
        self.session = None
    
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
