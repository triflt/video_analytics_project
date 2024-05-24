import psycopg2
from sqlalchemy import create_engine
import config

#connection = psycopg2.connect(database="video_analytics", user="user", password="user", host="localhost", port=5432)

def get_db_engine():
    return create_engine(f'postgresql://{config.DB_USER}:{config.DB_PASSWORD}@postgres:5432/{config.DB_NAME}')

try:
    db_engine = get_db_engine().connect()
except Exception as e:
    print(e)

#cursor = connection.cursor()

def insert():
    """ Create tables in the PostgreSQL database"""
    commands = (
        """
        INSERT INTO video_analytics.states (id, state) VALUES (1, 'state1');
        """,
        """
        INSERT INTO video_analytics.predictions (id, id_frame, prediction) VALUES (1, 1, 'prediction1');
        """
        )
    try:
        #with connection.cursor() as cur:
            # execute the CREATE TABLE statement
        for command in commands:
            db_engine.execute(command)
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def select():
    """ Create tables in the PostgreSQL database"""
    commands = (
        """
        SELECT * FROM video_analytics.states;
        """,
        """
        SELECT * FROM video_analytics.predictions;
        """
        )
    try:
        #with connection.cursor() as cur:
            # execute the CREATE TABLE statement
        for command in commands:
            db_engine.execute(command)
            print(db_engine.fetchone())
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

if __name__ == '__main__':
    insert()
    #select()