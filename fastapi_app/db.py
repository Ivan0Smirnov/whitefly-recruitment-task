import psycopg2


def get_connection():
    return psycopg2.connect(
        dbname="recruitment_tasks_whitefly",
        user="ivansmirnov",
        password="whitefly",
        host="db",
        port="5432"
    )


def run_query(query, params=None, fetch=False):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            return result
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
