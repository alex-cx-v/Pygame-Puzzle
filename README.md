# Pygame Puzzle

## Overview

Pygame Puzzle is an engaging puzzle game where players can assemble pieces to recreate a complete image. The game offers intuitive controls, a leaderboard to track top scores, and storage of player profiles and game progress in a database.

## Features

- Start the game by running `python run_game.py`.
- Scroll through the available puzzle pieces using the mouse wheel, arrow keys (up/down), or Page Up/Page Down keys.
- Drag and drop pieces using the mouse to assemble the puzzle.
- Pieces will snap into place when dropped close to their original position.
- Pieces will also snap to neighboring pieces if dropped close enough.
- Right-click on a group of connected pieces to split them into individual pieces.
- Create and save player profiles with unique usernames.
- View the leaderboard to see the top 10 scores, sorted by score and completion time.
- Earn bonus points for completing the puzzle quickly (e.g., under 5 or 10 minutes).
- The game automatically saves your best score for each profile.
- Select from a variety of puzzle motives and preview them before starting.
- Enjoy smooth animations and a user-friendly interface powered by `pygame` and `pygame_gui`.

## Instructions

1. Start the game by running `python run_game.py`.
2. Enter your username or select an existing profile to track your progress.
3. Navigate through the menu to select a puzzle motive.
4. Assemble the puzzle by dragging and snapping pieces into place.
5. Complete the puzzle as quickly as possible to earn time-based bonuses.
6. Check your score on the leaderboard and aim to improve!

## Requirements

- Python 3.x
- Required libraries: `pygame-ce==2.5.3`, `pygame_gui==0.6.13`

## To install dependencies, run:
`pip install -r requirements.txt`

## Enjoy solving puzzles and competing for the top score!
