CREATE SCHEMA video_analytics;

CREATE TABLE video_analytics.states (
            id SERIAL PRIMARY KEY,
            state VARCHAR,
            datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

CREATE TABLE video_analytics.predictions (
            id SERIAL PRIMARY KEY,
            id_frame INTEGER,
            prediction JSONB,
            datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );