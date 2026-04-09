from celery_app import celery
from db import get_connection


@celery.task(name="insert_user")
def insert_user(first_name, last_name):
    connection = get_connection()
    cursor = connection.cursor()
    insert_query = "INSERT INTO users (first_name, last_name) VALUES (%s, %s)"
    cursor.execute(insert_query, (first_name, last_name))
    connection.commit()
    cursor.close()
    connection.close()
    return f"{first_name} {last_name} successfully inserted"
