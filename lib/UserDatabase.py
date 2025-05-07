import sqlite3
import os

class UserDatabase:
    def __init__(self, db_name="users.db"):
        # Initialize the database connection and create necessary tables
        db_path = os.path.join("data", "db")  # Path to the database directory
        os.makedirs(db_path, exist_ok=True)  # Ensure the directory exists

        self.db_file = os.path.join(db_path, db_name)  # Full path to the database file

        self.connection = sqlite3.connect(self.db_file)  # Connect to the SQLite database
        self.cursor = self.connection.cursor()  # Create a cursor for executing SQL commands
        self._create_table()  # Create tables if they don't exist

    def _create_table(self):
        # Create the "users" table to store user information
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL UNIQUE
            )
        """)

        # Create the "scores" table to store user scores
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                time REAL NOT NULL,
                FOREIGN KEY (user_name) REFERENCES users (user_name) ON DELETE CASCADE
            )
        """)
        self.connection.commit()  # Commit the changes to the database

    def get_last_user(self):
        # Retrieve the most recently added user
        self.cursor.execute("""
            SELECT user_name FROM users
            ORDER BY id DESC
            LIMIT 1
        """)
        result = self.cursor.fetchone()
        return result[0] if result else None  # Return the username or None if no users exist

    def user_exists(self, user_name):
        # Check if a user with the given username exists in the database
        self.cursor.execute("""
            SELECT 1 FROM users WHERE user_name = ?
        """, (user_name,))
        return self.cursor.fetchone() is not None  # Return True if the user exists, otherwise False

    def add_user(self, user_name):
        # Add a new user to the database
        self.cursor.execute("""
            INSERT INTO users (user_name) VALUES (?)
        """, (user_name,))
        self.connection.commit()  # Commit the changes to the database

    def close(self):
        # Close the database connection
        self.connection.close()