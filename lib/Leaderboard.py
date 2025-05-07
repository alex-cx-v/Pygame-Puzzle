import pygame

class Leaderboard:
    def __init__(self, db):
        # Initialize the leaderboard with a database connection
        self.db = db
        self.entries = self._get_top_10()  # Fetch the top 10 scores

    def _get_top_10(self):
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

        # Retrieve the top 10 scores ordered by score (descending) and time (ascending)
        self.db.cursor.execute("""
            SELECT user_name, score, time
            FROM scores
            ORDER BY score DESC, time ASC
            LIMIT 10
        """)
        return self.db.cursor.fetchall()

    def refresh(self):
        # Refresh the leaderboard entries by fetching the latest top 10 scores
        self.entries = self._get_top_10()

    def draw(self, screen, font, x, y):
        # Draw the leaderboard on the screen
        rect_width = 300  # Width of the leaderboard background
        rect_height = 60 + len(self.entries) * 40  # Height based on the number of entries
        background_rect = pygame.Rect(x, y, rect_width, rect_height)

        # Draw the background rectangle
        pygame.draw.rect(screen, (0, 0, 0), background_rect)

        # Draw the leaderboard title
        black_font = pygame.font.Font("data/fnt/FixelDisplay-Black.otf", 30)
        title = black_font.render("Leaderboard", True, (255, 255, 255))
        screen.blit(title, (x + 10, y + 10))
        y += 60

        # Draw each leaderboard entry
        for idx, (user_name, score, time) in enumerate(self.entries, start=1):
            # Format the time as minutes and seconds
            minutes = int(time // 60)
            seconds = int(time % 60)
            # Create the entry text
            entry_text = f"{idx}. {user_name} - {score} pts - {minutes:02}:{seconds:02}"
            entry_surface = font.render(entry_text, True, (255, 255, 255))
            # Draw the entry on the screen
            screen.blit(entry_surface, (x + 10, y))
            y += 40