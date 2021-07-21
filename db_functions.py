import psycopg2
from config import config

__all__ = ["new_row", "create_table", "check_table"]

def new_row(query):
    conn = None
    try:
        # Read the connection parameters
        params = config()
        # Connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # Create new row
        cur.execute(query)
        # Close communication with the PostgreSQL database server
        cur.close()
        # Commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def create_table(name, query):
    """create a table in the PostgreSQL database"""
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table if it doesn't already exist
        cur.execute("select exists(select * from information_schema.tables where table_name='" + name + "')")
        table_exists = cur.fetchone()[0]
        if table_exists != True:
            cur.execute(query)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def check_table(value, column, table):
    """check if value exists in column in table - returns True or False"""    
    conn = None
    try:
        # read the connection parameters
        params = config()
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create twitter table if it doesn't already exist
        cur.execute("select exists(select " + column + " from " + table + " where " + column + "=" + value + ")")
        value_exists = cur.fetchone()[0]
        # close communication with the PostgreSQL database server
        cur.close()
        return value_exists
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()