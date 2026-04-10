from celery_app import celery
from db import run_query


@celery.task(name="insert_user")
def insert_user(first_name, last_name):
    run_query("INSERT INTO users (first_name, last_name) VALUES (%s, %s)", (first_name, last_name))
    return f"{first_name} {last_name} successfully inserted"
