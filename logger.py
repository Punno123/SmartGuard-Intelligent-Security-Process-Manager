# logger.py
from datetime import datetime

def log_event(message):
    # Add encoding="utf-8" to handle special characters
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} - {message}\n")