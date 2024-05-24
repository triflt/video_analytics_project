import psycopg2
from sqlalchemy import create_engine
from sqlalchemy import text
import config

def get_db_engine():
    return create_engine(f'postgresql://{config.DB_USER}:{config.DB_PASSWORD}@localhost:5432/{config.DB_NAME}')

try:
    db_engine = get_db_engine().connect()
except Exception as e:
    print(e)

def insert(state):
    command = f"INSERT INTO video_analytics.states (state) VALUES ('{state}') RETURNING id"
    try:
        result = db_engine.execute(text(command)).fetchall()
        db_engine.commit()
        print(result)
        return {"id": str(result[0])}
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        return {"error": error}

def select(video_id):
    command = f"SELECT state FROM video_analytics.states WHERE id={video_id}"
    try:
        result = db_engine.execute((text(command))).fetchall()
        db_engine.commit()
        for row in result:
            print(row)
        return {"id": str(result[0])}
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
        return {"error": error}
    

if __name__ == '__main__':
    insert('heh')
    select(34)