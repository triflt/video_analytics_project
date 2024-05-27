from sqlalchemy import create_engine, text
import json
import config

def get_db_engine():
    return create_engine(f'postgresql://{config.DB_USER}:{config.DB_PASSWORD}@localhost:5432/{config.DB_NAME}')

try:
    db_engine = get_db_engine().connect()
except Exception as e:
    print(e)

def init_state(state):
    command = f"INSERT INTO video_analytics.states (state) VALUES ('{state}') RETURNING id"
    try:
        result = db_engine.execute(text(command)).fetchall()
        db_engine.commit()
        return result[0]
    except ValueError as error:
        print(error)
        return {"error": error}

def update_state(state, video_id):
    command = f"UPDATE video_analytics.states SET state='{state}' WHERE id={video_id}"
    try:
        db_engine.execute(text(command))
        db_engine.commit()
    except ValueError as error:
        print(error)
        return {"error": error}

def get_state(video_id):
    command = f"SELECT state FROM video_analytics.states WHERE id={video_id}"
    try:
        result = db_engine.execute((text(command))).fetchall()
        db_engine.commit()
        return result[0]
    except ValueError as error:
        print(error)
        return {"error": error}
    
def select_inference_result(video_id):
    command = f"SELECT prediction from video_analytics.predictions WHERE id={video_id}"
    try:
        result = db_engine.execute((text(command))).fetchall()
        db_engine.commit()
        return result
    except ValueError as error:
        print(error)
        return {"error": error}

def save_prediction(json_data, video_id):
    command = f"INSERT INTO video_analytics.predictions (prediction, id) VALUES ('{json.dumps(json_data)}', {video_id})"
    try:
        db_engine.execute((text(command)))
        db_engine.commit()
    except ValueError as error:
        print(error)
        return {"error": error}
    

if __name__ == '__main__':
    test_text = 'test'
    id = init_state(test_text)
    assert get_state(id[0])[0] == test_text 