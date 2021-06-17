import psycopg2
from config import config

def create_tables():
    """ create tables in the PostgreSQL database"""
    create_table = "CREATE TABLE elon (elon_pkey SERIAL PRIMARY KEY, tweet_id NUMERIC, tweet_text TEXT, regex_result TEXT, regex_uppercase TEXT, profile_photo_url TEXT, profile_banner_url TEXT);"

    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create database
        #cur.execute(create_database)
        # create table
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