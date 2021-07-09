def new_row():
    row = "INSERT INTO twitter (twitter_handle, tweet_id, tweet_text, keywords, uppercase, tweet_url, profile_photo_url, profile_banner_url, timestamp) VALUES('" + twitter_handle + "', '" + format(new_tweet_id) + "', '" + new_tweet_text + "', '" + format(regex) + "', '" + regex_uppercase + "', '" + make_url() + "', '" + new_profile_photo + "', '" + new_profile_banner +"', '" + timestamp + "');"
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