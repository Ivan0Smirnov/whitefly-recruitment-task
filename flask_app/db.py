import psycopg2
def get_connection():
    return psycopg2.connect(
        dbname="recruitment_tasks_whitefly",
        user="ivansmirnov",
        password="whitefly",
        host="db",
        port="5432"
    )