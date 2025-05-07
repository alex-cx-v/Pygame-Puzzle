import time
from lib.UserDatabase import UserDatabase

class ScoreTable:
    def __init__(self, user_name):
        # Initialize the score table with the player's username
        self.user_name = user_name
        self.start_time = time.time()  # Record the start time of the game
        self.end_time = None  # End time will be set when the game is completed
        self.score = 0  # Initial score
        self.db = UserDatabase()  # Database connection for saving scores
        self.bonus_applied = False  # Flag to ensure the time bonus is applied only once

    def add_piece_score(self, count=1):
        # Add score for placing puzzle pieces
        self.score += 10 * count  # Each piece adds 10 points (multiplied by count)

    def get_elapsed_time(self):
        # Calculate the elapsed time since the game started
        if self.end_time:
            return self.end_time - self.start_time  # Use end time if the game is completed
        return time.time() - self.start_time  # Otherwise, calculate from the current time

    def mark_completed(self):
        # Mark the game as completed by setting the end time
        if not self.end_time:
            self.end_time = time.time()

    def calculate_time_bonus(self):
        # Calculate a time-based bonus based on the elapsed time
        elapsed_time = self.get_elapsed_time()
        if elapsed_time < 300:  # Under 5 minutes
            return 200, "Bonus: +200 points (under 5 minutes)"
        elif elapsed_time < 600:  # Under 10 minutes
            return 100, "Bonus: +100 points (under 10 minutes)"
        else:  # Over 10 minutes
            return 0, "No bonus (over 10 minutes)"

    def apply_time_bonus(self):
        # Apply the time bonus to the score
        if not self.bonus_applied:
            bonus, _ = self.calculate_time_bonus()
            self.score += bonus
            self.bonus_applied = True  # Ensure the bonus is applied only once

    def save_best_score(self):
        # Save the player's best score to the database
        if self.end_time is None:
            return  # Do nothing if the game is not completed

        self.apply_time_bonus()  # Ensure the time bonus is applied
        elapsed_time = self.get_elapsed_time()

        # Create the scores table if it doesn't exist
        self.db.cursor.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                time REAL NOT NULL,
                FOREIGN KEY (user_name) REFERENCES users (user_name) ON DELETE CASCADE
            )
        """)
        self.db.connection.commit()

        # Check the player's best score
        self.db.cursor.execute("""
            SELECT MAX(score) FROM scores WHERE user_name = ?
        """, (self.user_name,))
        best_score = self.db.cursor.fetchone()[0]

        # Save the new score if it's better than the previous best
        if best_score is None or self.score > best_score:
            self.db.cursor.execute("""
                INSERT INTO scores (user_name, score, time) VALUES (?, ?, ?)
            """, (self.user_name, self.score, elapsed_time))
            self.db.connection.commit()

    def close(self):
        # Close the database connection
        self.db.close()