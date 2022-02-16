import mysql.connector

class mysqldb:
    def __init__(self):
        connection = None
        session = None
    
    def open_connection(self):
        db = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='testdb'
        )

        self.connection = db
        self.session = db.cursor()
    
    def close_connection(self):
        self.session.close()
        self.connection.close()
    
    def test(self):
        print("test")
