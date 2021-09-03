# TODO consolidate more code into functions - regex, print_console, print_log, 
# TODO sentiment analysis

## Modules ##
from pytwitterscraper import TwitterScraper                 # Twitter scraper - no API key required
import webbrowser                                           # Web browser
import time                                                 # Wait
import re                                                   # Regex
import winsound                                             # Play Windows sounds
import sys                                                  # Read/write to files
import argparse                                             # Argument parser
import datetime                                             # Timestamp
from db_functions import *                                  # Database functions
from discord_webhook import DiscordWebhook, DiscordEmbed    # Discord webhook
from secrets import DISCORD_WEBHOOK_URL                     # Contains webhook URL for Discord channel

## Variables ##

# Save original standard output (for logging to twitter.log)
original_stdout = sys.stdout

# Argument parser
parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
parser.add_argument("username", nargs="?", default="unusual_whales") # Change default twitter account here
parser.add_argument("--wordlist", nargs="?", action="store", default="keywords.txt") # Change default keyword list here
parser.add_argument("--tablename", nargs="?", action="store", default="twitter") # Change default PostgreSQL table here
parser.add_argument('--noconsole', action="store_false", default=True)
parser.add_argument('--nolog', action="store_false", default=True)
parser.add_argument('--nobrowser', action="store_false", default=True)
parser.add_argument('--nosounds', action="store_false", default=True)
parser.add_argument('--nodb', action="store_false", default=True)
parser.add_argument('--nodiscord', action="store_false", default=True)
args = parser.parse_args()

## Options ## - Now controlled via argument parser ^
console = args.noconsole
log = args.nolog
open_browser = args.nobrowser
play_sounds = args.nosounds
database = args.nodb
discord = args.nodiscord
wordlist = args.wordlist

# Get Twitter account from argument
twitter_handle = args.username

# Get table name from argument
table_name = args.tablename

# Create twitter scraper object
tw = TwitterScraper()

# Variables for loop
new_tweet_id = ""
new_tweet_text = ""
new_tweet_hashtags = ""

# Regular expression pattern for uppercase characters
regex_uppercase_pattern = ['[A-Z]+']

# Timestamp
timestamp = format(datetime.datetime.now())

# Iterator
i = 1


## Functions ##

# Convert a list to a string 
def list_to_string(s):     
    str1 = ""      
    for ele in s: 
        str1 += ele     
    return str1

# Convert a list to a string adding spaces between elements
def list_to_string_spaces(s):     
    str1 = ""      
    for ele in s: 
        str1 += ele + " "     
    return str1

# Remove special characters from regex result string
def format_regex(r):
    r.replace("\'", "").replace(" ", "").replace("[", "").replace("]", "").replace(",", " ")
    return r

# Search keyword list and format
def find_keywords(tweet_text):
    # Open wordlist
    keywords = open(wordlist, "r", encoding="utf-8")
    # Format wordlist for regex
    keywords_regex_string = keywords.read().replace("\n", "|")
    # Find all keywords in new tweet with regex
    result = re.findall(keywords_regex_string, tweet_text, re.IGNORECASE)
    # Convert r to string, remove special characters, and return r
    if result != None:
        return format_regex(list_to_string_spaces(result))

# Find upercase characters and create a string (they can be sneaky like that)
def find_upercase(tweet_text):
    for p in regex_uppercase_pattern:
        result = format_regex(list_to_string(re.findall(p, tweet_text)))
    return result

# Remove characters that break INSERT
def format_tweet(tweet_text):
    tweet_text.replace("'", "").replace("\"", "")
    return tweet_text

# Make tweet URL - this can also be retrieved from new_tweet_contents with ["url"]
def make_url(tweet_id):
    url = f"https://twitter.com/{twitter_handle}/status/{format(tweet_id)}"
    return url


## Run once before looping ##

# Create PostgreSQL table if it doesn't exist
if database:  
    table_query = f"CREATE TABLE {table_name} ({table_name}_pkey SERIAL PRIMARY KEY, twitter_handle TEXT, tweet_id NUMERIC, hashtags TEXT, tweet_text TEXT, keywords TEXT, uppercase TEXT, tweet_url TEXT, profile_photo_url TEXT, profile_banner_url TEXT, timestamp TEXT);" 
    try:
        create_table(table_name, table_query)
    except:
        print("Table error")

# Get Twitter profile data
try:
    profile = tw.get_profile(name=twitter_handle).__dict__
    profile_photo = profile["profileurl"]
    profile_banner = profile["bannerurl"]
    twitter_id = profile["id"]
except:
    print("Bad initial profile request")
    print("Try again")
    exit()

# Get last 2 tweets and compare IDs to filter up to 1 pinned tweet
try:
    last_tweet_contents = tw.get_tweets(twitter_id, count=2).contents
    last_tweet_id = last_tweet_contents[0]["id"]
    last_tweet_id_2 = last_tweet_contents[1]["id"]
    if last_tweet_id_2 > last_tweet_id:
        last_tweet_id = last_tweet_id_2
        newer_tweet = 0
    else:
        newer_tweet = 1
    last_tweet_text = list_to_string(last_tweet_contents[newer_tweet]["text"])
    last_tweet_hashtags = list_to_string(last_tweet_contents[newer_tweet]["hashtags"])
    # Find keywords
    last_tweet_keywords = find_keywords(last_tweet_text)
    # Find uppercase characters    
    last_regex_uppercase = find_upercase(last_tweet_text)
    # Check database for last_tweet_id and add a new row if not present
    if check_table(last_tweet_id, "tweet_id", table_name) == False:
        last_tweet_query = f"INSERT INTO {table_name} (twitter_handle, tweet_id, hashtags, tweet_text, keywords, uppercase, tweet_url, profile_photo_url, profile_banner_url, timestamp) VALUES('{twitter_handle}', '{format(last_tweet_id)}', '{last_tweet_hashtags}', '{format_tweet(last_tweet_text)}', '{format(last_tweet_keywords)}', '{last_regex_uppercase}', '{make_url(last_tweet_id)}', '{profile_photo}', '{profile_banner}', '{timestamp}');"
        new_row(last_tweet_query)
except:
    print("No tweets detected")
    print("Try again")
    exit()


## Scrape Twitter and open in browser if new tweet, profile photo changed, or banner changed ##
while True:
    # Get new profile data
    try:
        new_profile = tw.get_profile(name=twitter_handle).__dict__
        new_profile_photo = new_profile["profileurl"]
        new_profile_banner = new_profile["bannerurl"]
    except:
        print("Bad profile \n")
    # Get 2 latest tweets and compare IDs to filter up to 1 pinned tweet
    try:
        new_tweet_contents = tw.get_tweets(twitter_id, count=2).contents
        new_tweet_id = new_tweet_contents[1]["id"]
        new_tweet_id_2 = new_tweet_contents[0]["id"]
        if new_tweet_id_2 > new_tweet_id:
            newest_tweet = 0
            new_tweet_id = new_tweet_id_2
        else:
            newest_tweet = 1
        new_tweet_text = new_tweet_contents[newest_tweet]["text"]
        new_tweet_hashtags = list_to_string(new_tweet_contents[newest_tweet]["hashtags"])
        tweet_keywords  = find_keywords(new_tweet_text)
        for p in regex_uppercase_pattern:
            regex_uppercase = format_regex(list_to_string(re.findall(p, new_tweet_text)))
        # Compare new tweet to last tweet
        if open_browser:
            if new_tweet_id != last_tweet_id and new_tweet_id > last_tweet_id:
                webbrowser.open(make_url(new_tweet_id), new=1)
            # Compare profile URL
            if new_profile_photo != profile_photo:
                webbrowser.open(new_profile_photo, new=1) 
            # Compare banner URL
            if new_profile_banner != profile_banner:
                webbrowser.open(new_profile_banner, new=1)
    except:
        print("Bad tweet \n")
    
    ## Print results to console ##
    if console:
        print(f"Iteration: {i}")
        print(f"Timestamp: {timestamp}")
        print(f"Twitter Handle: @{twitter_handle}")
        print(f"Tweet ID: {new_tweet_id}")
        print(f"Tweet Text: {new_tweet_text}")   
        print(f"Tweet Hashtags: {list_to_string(new_tweet_hashtags)}")    
        print(f"Keywords: {tweet_keywords}")
        print(f"Upper Case: {regex_uppercase}")
        print(f"Tweet URL: {make_url(new_tweet_id)} \n")

    ## Send tweet to discord
    try:
        # Discord web hook URL defined in secrets.py
        if discord and new_tweet_id > last_tweet_id:
            webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
            embed = DiscordEmbed(title=f'@{twitter_handle}', description=format_tweet(new_tweet_text), color='03b2f8')
            # add fields to embed
            if tweet_keywords:
                embed.add_embed_field(name='Keywords', value=tweet_keywords)
            embed.add_embed_field(name='URL', value=make_url(new_tweet_id))      
            # add embed object to webhook
            webhook.add_embed(embed)
            response = webhook.execute()
    except:
        print("Discord error \n")

    ## Print results to log if new tweet, profile URL changed, or banner changed ##
    try:
        # Tweets
        if log and new_tweet_id > last_tweet_id:
            with open("twitter.log", "a", encoding="utf-8") as log:
                sys.stdout = log
                print(f"Timestamp: {timestamp}")
                print(f"Twitter Handle: @{twitter_handle}")
                print(f"Tweet ID: {new_tweet_id}")
                print(f"Tweet Text: {new_tweet_text}")   
                print(f"Tweet Hashtags: {list_to_string(new_tweet_hashtags)}")    
                print(f"Keywords: {tweet_keywords}")
                print(f"Upper Case: {regex_uppercase}")
                print(f"Tweet URL: {make_url(new_tweet_id)} \n")
                # Reset the standard output
                sys.stdout = original_stdout
        # Photo
        if new_profile_photo != profile_photo:
            with open("twitter.log", "a") as log:
                sys.stdout = log 
                print(f"Timestamp: {timestamp}")
                print(f"Twitter Handle: @{twitter_handle}")
                print(f"Profile URL: {new_profile_photo} \n")
                # Reset the standard output
                sys.stdout = original_stdout
        # Banner
        if new_profile_banner != profile_banner:
            with open("twitter.log", "a") as log:
                sys.stdout = log 
                print(f"Timestamp: {timestamp}")
                print(f"Twitter Handle: @{twitter_handle}")
                print(f"Banner URL: {new_profile_banner} \n")
                # Reset the standard output
                sys.stdout = original_stdout
    except:
        print("Log error \n")

    ## Update table in database ##
    if database and (new_tweet_id > last_tweet_id or new_profile_photo != profile_photo or new_profile_banner != profile_banner):
        row_query = f"INSERT INTO {table_name} (twitter_handle, tweet_id, hashtags, tweet_text, keywords, uppercase, tweet_url, profile_photo_url, profile_banner_url, timestamp) VALUES('{twitter_handle}', '{format(new_tweet_id)}', '{new_tweet_hashtags}', '{format_tweet(new_tweet_text)}', '{format(tweet_keywords)}', '{regex_uppercase}', '{make_url()}', '{new_profile_photo}', '{new_profile_banner}', '{timestamp}');"
        try:
            new_row(row_query) 
        except:
            print("Database not detected")     
    
    ## Play sound if keyword found or image changed ##
    try:
        if play_sounds and ((tweet_keywords != "") and (new_tweet_id > last_tweet_id) or (new_profile_photo != profile_photo) or (new_profile_banner != profile_banner)):
            winsound.PlaySound("sound2.wav", winsound.SND_ASYNC)
    except:
        print("Error playing sound \n")
        
    # Feeling brave? Add exchange API code here
    # if re.search("DOGE|Doge|doge",new_tweet_text) and new_tweet_id > last_tweet_id:
    # if re.search("BTC|DOGE|btc|Bitcoin|bitcoin",new_tweet_text) and new_tweet_id > last_tweet_id:

    ## Update tweet ID, profile URL, and banner URL ##
    if new_tweet_id > last_tweet_id:
        last_tweet_id = new_tweet_id
    if new_profile_photo != profile_photo:
        profile_photo = new_profile_photo
    if new_profile_banner != profile_banner:
        profile_banner = new_profile_banner

    ##  Update iterator ##
    i += 1
        
    ## Wait 5 seconds ##
    time.sleep(5)