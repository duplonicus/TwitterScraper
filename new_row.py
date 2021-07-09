import psycopg2
from config import config
import sys

def new_row(row):
    conn = None
    try:
        # Read the connection parameters
        params = config()
        # Connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # Create new row
        cur.execute(row)
        # Close communication with the PostgreSQL database server
        cur.close()
        # Commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        with open("twitter.log", "a") as log:
            sys.stdout = log 
            print("Database error:", error, "\n")
            # Reset the standard output
            sys.stdout = original_stdout
    finally:
        if conn is not None:
            conn.close()
if __name__ == '__main__':
    new_row()