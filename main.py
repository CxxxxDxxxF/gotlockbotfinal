import datetime
from bot import run_bot

def current_timestamp():
    """Return current UTC timestamp as a formatted string."""
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

def ready_message(user):
    """Return a ready message including the user's identifier and timestamp."""
    return f"\u2714 GotLockz bot logged in as {user} at {current_timestamp()}"

if __name__ == "__main__":
    run_bot()
