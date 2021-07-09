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

def create_tables():
    """ create tables in the PostgreSQL database"""
    create_table = "CREATE TABLE twitter (twitter_pkey SERIAL PRIMARY KEY, twitter_handle TEXT, tweet_id NUMERIC, tweet_text TEXT, keywords TEXT, uppercase TEXT, tweet_url TEXT, profile_photo_url TEXT, profile_banner_url TEXT, timestamp TEXT);"
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create twitter table if it doesn't already exist
        cur.execute("select exists(select * from information_schema.tables where table_name='twitter')")
        table_exists = cur.fetchone()[0]
        if table_exists != True:
            cur.execute(create_table)      
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()        

if __name__ == '__main__':
    create_tables()