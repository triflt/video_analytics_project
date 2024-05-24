CREATE SCHEMA video_analytics;

CREATE TABLE video_analytics.states (
            id INTEGER PRIMARY KEY,
            state VARCHAR,
            datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

CREATE TABLE video_analytics.predictions (
            id INTEGER PRIMARY KEY,
            id_frame INTEGER,
            prediction VARCHAR,
            datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );