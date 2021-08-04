from timetracker.models import create_database
from timetracker.ctes import SQLITE_DB_FILE


if __name__ == "__main__":
    create_database(SQLITE_DB_FILE)