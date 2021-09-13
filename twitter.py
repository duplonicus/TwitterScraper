# TODO get full_text isntead of truncated text from tweets - possibly an issue with get_tweets() in pytwitterscraper module
# TODO escape single quotes in input statement instead of removing them
# TODO better expceptions and error logging
# TODO add required argument types to arguments

## Modules ##
from pytwitterscraper import TwitterScraper                 # Twitter scraper - no API key required
import webbrowser                                           # Web browser
import time                                                 # Wait
import re                                                   # Regex
import winsound                                             # Play Windows sounds
import sys                                                  # Read/write to files
import argparse                                             # Argument parser
import datetime                                             # Timestamp
from nltk.sentiment import SentimentIntensityAnalyzer       # Sentiment analyzer
from db_functions import *                                  # Database functions
from discord_webhook import DiscordWebhook, DiscordEmbed    # Discord webhook
from secrets import DISCORD_WEBHOOK_URL                     # Webhook URL for Discord channel

## Variables ##

# Save original standard output (for logging to twitter.log)
original_stdout = sys.stdout

# Argument parser
parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
parser.add_argument("username", nargs="?", default="unusual_whales") # Change default twitter account here
parser.add_argument("--wordlist", nargs="?", action="store", default="keywords.txt") # Change default keyword list here
parser.add_argument("--tablename", nargs="?", action="store", default="twitter") # Change default PostgreSQL table here
parser.add_argument("--frequency", nargs="?", action="store", default=5) # Change default loop wait time in seconds here
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
loop_wait = int(args.frequency)

# Get Twitter account from argument
twitter_handle = args.username

# Get table name from argument
table_name = args.tablename

# Create twitter scraper object
tw = TwitterScraper()

# Create sentiment analayzer object
sia = SentimentIntensityAnalyzer()

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

# Remove special characters (used after converting regex result list to string)
def remove_special_chars(regex_result):
    return regex_result.replace("\'", "").replace(" ", "").replace("[", "").replace("]", "").replace(",", " ")

# Remove quotation marks that might break insert statements
def remove_quotes(tweet_text):
    return tweet_text.replace('"','').replace("'", "")

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
        return remove_special_chars(list_to_string_spaces(result))

# Find upercase characters and create a string (they can be sneaky like that)
def find_uppercase(tweet_text):
    for p in regex_uppercase_pattern:
        result = remove_special_chars(list_to_string(re.findall(p, tweet_text)))
    return result

# Make tweet URL - this can also be retrieved from new_tweet_contents with ["url"]
def make_url(tweet_id):
    url = f"https://twitter.com/{twitter_handle}/status/{format(tweet_id)}"
    return url

# Find sentiment
def find_sentiment(tweet: str):
    score = sia.polarity_scores(tweet)["compound"]
    if score == 0:
        return f"Neutral ({score})"
    elif score > 0:
        return f"Positive ({score})"
    else:
        return f"Negative ({score})"

## Run once before looping ##

# Create PostgreSQL table if it doesn't exist
if database:  
    table_query = f"CREATE TABLE {table_name} ({table_name}_pkey SERIAL PRIMARY KEY, twitter_handle TEXT, tweet_id NUMERIC, hashtags TEXT, tweet_sentiment TEXT, tweet_text TEXT, tweet_image TEXT, keywords TEXT, uppercase TEXT, tweet_url TEXT, profile_photo_url TEXT, profile_banner_url TEXT, timestamp TEXT);" 
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

# Get last 2 tweets and compare IDs to filter up to 1 pinned tweet (a pinned tweet may not be the newest tweet)
try:
    last_tweet_contents = tw.get_tweets(twitter_id, count=2).contents
    # Check if the profile has more than 1 tweet
    if len(last_tweet_contents) > 1:
        # Compare last 2 tweets and use the newer one
        last_tweet_id = last_tweet_contents[1]["id"]
        last_tweet_id_2 = last_tweet_contents[0]["id"]
        if last_tweet_id_2 > last_tweet_id:
            last_tweet_id = last_tweet_id_2
            newer_tweet = 0
        else:
            newer_tweet = 1
    else:
        last_tweet_id = last_tweet_contents[0]["id"]
        newer_tweet = 0
    # Get tweet text
    last_tweet_text = remove_quotes(last_tweet_contents[newer_tweet]["text"])
    # Get tweet hashtags
    last_tweet_hashtags = list_to_string_spaces(last_tweet_contents[newer_tweet]["hashtags"])
    # Get tweet image
    if last_tweet_contents[newer_tweet]["media"] != [] :
        last_tweet_image = last_tweet_contents[newer_tweet]["media"][0]["image_url"]
    else:
        last_tweet_image = ''
    # Find keywords in tweet text
    last_tweet_keywords = find_keywords(last_tweet_text)
    # Find uppercase characters in tweet text
    last_regex_uppercase = find_uppercase(last_tweet_text)
    # Find sentiment
    last_sentiment = find_sentiment(last_tweet_text)
    # Check database for last_tweet_id and add a new row if not present
    try:
        if check_table(last_tweet_id, "tweet_id", table_name) == False:
            last_tweet_query = f"INSERT INTO {table_name} (twitter_handle, tweet_id, hashtags, tweet_sentiment, tweet_text, tweet_image, keywords, uppercase, tweet_url, profile_photo_url, profile_banner_url, timestamp) VALUES('{twitter_handle}', '{format(last_tweet_id)}', '{last_tweet_hashtags}', '{last_sentiment}','{last_tweet_text}', '{last_tweet_image}', '{format(last_tweet_keywords)}', '{last_regex_uppercase}', '{make_url(last_tweet_id)}', '{profile_photo}', '{profile_banner}', '{timestamp}');"
            new_row(last_tweet_query)
    except:
        print("Database error")
except:
    print("No tweets detected")
    print("Try again")
    #print(last_tweet_contents) # Debugging
    exit()


## Main loop - Scrape Twitter and open in browser if new tweet, profile photo changed, or banner changed ##
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
        # Check if the profile has more than 1 tweet
        if len(new_tweet_contents) > 1:
            # Compare last 2 tweets and use the newer one
            new_tweet_id = new_tweet_contents[1]["id"]
            new_tweet_id_2 = new_tweet_contents[0]["id"]
            if new_tweet_id_2 > new_tweet_id:
                newest_tweet = 0
                new_tweet_id = new_tweet_id_2
            else:
                newest_tweet = 1
        else: 
            new_tweet_id = new_tweet_contents[0]["id"]
            newest_tweet = 0
        # Get text from newest tweet
        new_tweet_text = remove_quotes(new_tweet_contents[newest_tweet]["text"])
        # Get hashtags from newest tweet
        new_tweet_hashtags = list_to_string(new_tweet_contents[newest_tweet]["hashtags"])
        # Get tweet image
        if new_tweet_contents[newest_tweet]["media"] != [] :
            new_tweet_image = new_tweet_contents[newest_tweet]["media"][0]["image_url"]
        else:
            new_tweet_image = ''
        # Find keywords in newest tweet text
        tweet_keywords = find_keywords(new_tweet_text)
        # Find uppercase chars in newest tweet text
        regex_uppercase = find_uppercase(new_tweet_text)
        # Find sentiment
        new_sentiment = find_sentiment(new_tweet_text)
        # Compare new tweet to last tweet and open changes in browser
        if open_browser:
            # Compare tweets
            if new_tweet_id != last_tweet_id and new_tweet_id > last_tweet_id:
                webbrowser.open(make_url(new_tweet_id), new=1)
            # Compare profile image URL
            if new_profile_photo != profile_photo:
                webbrowser.open(new_profile_photo, new=1) 
            # Compare banner image URL
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
        print(f"Sentiment: {new_sentiment}")
        print(f"Tweet Text: {new_tweet_text}")   
        print(f"Tweet Hashtags: {list_to_string_spaces(new_tweet_hashtags)}")    
        print(f"Keywords: {tweet_keywords}")
        print(f"Upper Case: {regex_uppercase}")
        print(f"Tweet URL: {make_url(new_tweet_id)}")
        print(f"Tweet Image: {new_tweet_image}  \n")

    ## Send changes to discord ##
    # Discord web hook URL defined in secrets.py
    try:
        # Tweets
        if discord and new_tweet_id > last_tweet_id:
            webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
            embed = DiscordEmbed(title=f'@{twitter_handle}', description=new_tweet_text, color='03b2f8')
            # Add fields to embed
            if tweet_keywords:
                embed.add_embed_field(name='Keywords', value=tweet_keywords)
            embed.add_embed_field(name='Sentiment', value=new_sentiment) 
            embed.add_embed_field(name='URL', value=make_url(new_tweet_id))  
            if new_tweet_image != '':
                  embed.set_image(url=new_tweet_image) 
            # Add embed object to webhook
            webhook.add_embed(embed)
            response = webhook.execute()
        # Profile photo
        if discord and new_profile_photo != profile_photo:
            webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
            embed = DiscordEmbed(title=f'@{twitter_handle}', description="New Profile Photo", color='03b2f8')
            # Add fields to embed
            embed.add_embed_field(name='Photo URL', value=profile_photo) 
            # Add embed object to webhook
            webhook.add_embed(embed)
            response = webhook.execute()
        # Profile banner
        if discord and new_profile_banner != profile_banner:
            webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
            embed = DiscordEmbed(title=f'@{twitter_handle}', description="New Profile Banner", color='03b2f8')
            # Add fields to embed
            embed.add_embed_field(name='Photo Banner URL', value=profile_banner) 
            # Add embed object to webhook
            webhook.add_embed(embed)
            response = webhook.execute()
    except:
        print("Discord error \n")

    ## Print results to log if new tweet, profile image URL changed, or banner image URL changed ##
    try:
        # Tweets
        if log and new_tweet_id > last_tweet_id:
            with open("twitter.log", "a", encoding="utf-8") as log:
                sys.stdout = log
                print(f"Timestamp: {timestamp}")
                print(f"Twitter Handle: @{twitter_handle}")
                print(f"Tweet ID: {new_tweet_id}")
                print(f"Sentiment: {new_sentiment}")
                print(f"Tweet Text: {new_tweet_text}")   
                print(f"Tweet Hashtags: {list_to_string(new_tweet_hashtags)}")    
                print(f"Keywords: {tweet_keywords}")
                print(f"Upper Case: {regex_uppercase}")
                print(f"Tweet URL: {make_url(new_tweet_id)}")
                print(f"Tweet Image: {new_tweet_image}  \n")
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

    ## Update table in database if anything changed ##
    if database and (new_tweet_id > last_tweet_id or new_profile_photo != profile_photo or new_profile_banner != profile_banner):
        row_query = f"INSERT INTO {table_name} (twitter_handle, tweet_id, hashtags, tweet_sentiment, tweet_text, tweet_image, keywords, uppercase, tweet_url, profile_photo_url, profile_banner_url, timestamp) VALUES('{twitter_handle}', '{format(new_tweet_id)}', '{new_tweet_hashtags}', '{new_sentiment}', '{new_tweet_text}', '{new_tweet_image}', '{format(tweet_keywords)}', '{regex_uppercase}', '{make_url(last_tweet_id)}', '{new_profile_photo}', '{new_profile_banner}', '{timestamp}');"
        try:
            new_row(row_query) 
        except:
            print("Database error")
    
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
    time.sleep(loop_wait)