#Libraries
from pytwitterscraper import TwitterScraper #Twitter scraper
import webbrowser                           #Web browser
import time                                 #Wait
import re                                   #Regex
import winsound                             #Play Windows sounds
import sys                                  #Write to files
import psycopg2                             #Library for postgreSQL functionality
from config import config                   #Used to connect to DB with db.ini
import argparse                             #Used to change elon to someone else if desired

#Variables

#Parser
parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
parser.add_argument("username", nargs="?")
args = parser.parse_args()
#Save original standard output for logging
original_stdout = sys.stdout
#Create twitter scraper
tw = TwitterScraper()
#Twitter Handle from args or default
try:
    twitter_handle = args.username
except:
    twitter_handle = "elonmusk"
#Get Elon's Twitter profile data
profile = tw.get_profile(name=twitter_handle)
profile_dict = profile.__dict__
profile_url = profile_dict["profileurl"]
profile_banner = profile_dict["bannerurl"]
#Elon's twitter ID and URL
elon_id = profile_dict["id"]
elon_twitter_url = "https://twitter.com/" + twitter_handle
#Get Elon's last tweet data
last_tweet = tw.get_tweets(elon_id, count=1)
last_tweet_contents = last_tweet.contents
last_tweet_id = last_tweet_contents[0]["id"]
#Store empty new tweet ID and text strings to avoid errors
new_tweet_id = None
new_tweet_text = None
#Keywords Elon has used
keywords = "Crypto|crypto|BTC|btc|Bitcoin|bitcoin|DOGE|Doge|doge|💦|🚀|🌙|🌕|🌜|🌛|CUM|Cum|cum|Rocket|rocket|Moon|moon|Money|money|Economy|economy|Market|market"
#Iterator
i = 1

#Scrape Elon's Twitter and open in browser if new tweet, profile photo changed, or banner changed
while True:
    try:
        #Get new profile data
        new_profile = tw.get_profile(name=twitter_handle)
        new_profile_dict = new_profile.__dict__
        new_profile_url = new_profile_dict["profileurl"]
        new_profile_banner = new_profile_dict["bannerurl"]
    except:
        print("Bad profile \n")
    try:
        #Get new tweet data
        new_tweet = tw.get_tweets(elon_id, count=1)
        new_tweet_contents = new_tweet.contents
        new_tweet_id = new_tweet_contents[0]["id"]
        new_tweet_text = new_tweet_contents[0]["text"]
        #Compare tweet
        if new_tweet_id != last_tweet_id and type(new_tweet_id) == int and new_tweet_id > last_tweet_id:
            webbrowser.open(elon_twitter_url, new=1)
        #Compare profile URL
        if new_profile_url != profile_url:
            webbrowser.open(new_profile_url, new=1) 
        #Compare banner URL
        if new_profile_banner != profile_banner:
            webbrowser.open(new_profile_banner, new=1)
    except:
        print("Bad tweet \n")

    #Print results to console
    print("Iteration: ", i)
    try:
        #Tweets
        print("Tweet ID: ", new_tweet_id)
        print("Tweet Text: ", new_tweet_text)        
    except:
        print("Nothing to print \n")
    try:
        #Regular expression for keywords
        regex = re.search(keywords, new_tweet_text)
        print("Regex Result: ", regex)
        #Regular expression for uppercase characters
        regex_uppercase_pattern = ['[A-Z]+']
        for p in regex_uppercase_pattern:
            regex_uppercase = re.findall(p, new_tweet_text)
            print("Upper Case: ", regex_uppercase)
    except:
        print("Regex error")
    #Photo
    print("Profile URL: ", new_profile_url, "\n")

    #Print results to log if new tweet, profile URL changed, or banner changed
    try:
        #Tweets
        if new_tweet_id > last_tweet_id:
            with open("twitter.log", "a") as log:
                sys.stdout = log 
                print("Iteration: ", i)
                print("Tweet ID: ", new_tweet_id)
                print("Tweet Text: ", new_tweet_text)
                print("Regex Result: ", regex)
                print("Upper Case: ", regex_uppercase, "\n")
                # Reset the standard output
                sys.stdout = original_stdout 
        #Photo
        if new_profile_url != profile_url:
            with open("twitter.log", "a") as log:
                sys.stdout = log 
                print("Profile URL: ", new_profile_url, "\n")
                #Reset the standard output
                sys.stdout = original_stdout
        #Banner
        if new_profile_banner != profile_banner:
            with open("twitter.log", "a") as log:
                sys.stdout = log 
                print("Banner URL: ", new_profile_banner, "\n")
                #Reset the standard output
                sys.stdout = original_stdout
    except:
        print("Log error \n")

    #Update elon table in elonscraper database
    if new_tweet_id > last_tweet_id or new_profile_url != profile_url or new_profile_banner != profile_banner:
        def new_row():
            row = "INSERT INTO elon (tweet_id, tweet_text, regex_result, regex_uppercase, profile_photo_url, profile_banner_url) VALUES(" + str(new_tweet_id) + ", '" + new_tweet_text + "', '" + regex + "', '" + regex_uppercase + "', '" + new_profile_url + "', '" + new_profile_banner + "');"

            conn = None
            try:
                # read the connection parameters
                params = config()
                # connect to the PostgreSQL server
                conn = psycopg2.connect(**params)
                cur = conn.cursor()
                # create new row
                cur.execute(row)
                # close communication with the PostgreSQL database server
                cur.close()
                # commit the changes
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
                with open("twitter.log", "a") as log:
                    sys.stdout = log 
                    print("Database error: ", error, "\n")
                    #Reset the standard output
                    sys.stdout = original_stdout
            finally:
                if conn is not None:
                    conn.close()

        if __name__ == '__main__':
            new_row()
        
    
    #Play sound if keyword found
    if re.search(keywords, new_tweet_text) and new_tweet_id > last_tweet_id:
        winsound.PlaySound("sound2.wav", winsound.SND_ASYNC)
    #Play sound if profile URL changes, or banner changes
    if new_profile_url != profile_url or new_profile_banner != profile_banner:
        winsound.PlaySound("sound2.wav", winsound.SND_ASYNC)
        
    #Feeling brave? Add exchange API code here
    #if re.search("DOGE|Doge|doge",new_tweet_text) and new_tweet_id > last_tweet_id:
    #if re.search("BTC|DOGE|btc|Bitcoin|bitcoin",new_tweet_text) and new_tweet_id > last_tweet_id:

    #Update tweet ID, profile URL, and banner URL
    if new_tweet_id > last_tweet_id:
        last_tweet_id = new_tweet_id
    if new_profile_url != profile_url:
        profile_url = new_profile_url
    if new_profile_banner != profile_banner:
        profile_banner = new_profile_banner

    #Update iteration
    i += 1
        
    #Wait 5 seconds
    time.sleep(5)