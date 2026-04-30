import mysql.connector

def get_db():

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Kishlay@0610",
        database="heart_app"
    )

    return conn