-- Create a users table.
CREATE TABLE users (
    id varchar PRIMARY KEY,
    email varchar NOT NULL,
    email_verified boolean NOT NULL,
    created_at timestamp NOT NULL
);

-- Create a user_resorts table that links users to their pinned resorts.
CREATE TABLE user_resorts (
    user_id varchar NOT NULL REFERENCES users,
    resort_id varchar NOT NULL REFERENCES resorts
);