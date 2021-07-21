# TODO consolidate more code into functions - regex, print_console, print_log, 
# TODO check latest tweet ID entry in DB and add last_tweet info to log and DB if not present
# TODO sentiment analysis

## Modules ##
from pytwitterscraper import TwitterScraper                 # Twitter scraper no API required
import webbrowser                                           # Web browser
import time                                                 # Wait
import re                                                   # Regex
import winsound                                             # Play Windows sounds
import sys                                                  # Write to files
import argparse                                             # Argument parser - change default to someone else if desired
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
parser.add_argument("--tablename", nargs="?", action="store", default="twitter") # Change PostgreSQL table here
parser.add_argument('--noconsole', action="store_false", default=True)
parser.add_argument('--nolog', action="store_false", default=True)
parser.add_argument('--nobrowser', action="store_false", default=True)
parser.add_argument('--nosounds', action="store_false", default=True)
parser.add_argument('--nodb', action="store_false", default=True)
parser.add_argument('--nodiscord', action="store_false", default=True)
args = parser.parse_args()

## Options ##
console = args.noconsole
log = args.nolog
open_browser = args.nobrowser
play_sounds = args.nosounds
database = args.nodb
discord = args.nodiscord

# Get Twitter handle from argument
twitter_handle = args.username

# Create twitter scraper object
tw = TwitterScraper()

# Table name
table_name = args.tablename

# Variables for loop
new_tweet_id = ""
new_tweet_text = ""
new_tweet_hashtags = ""

# Keywords
keywords = "Crypto|crypto|BTC|btc|Bitcoin|bitcoin|DOGE|Doge|doge|💦|🚀|🌙|🌕|🌜|🌛|CUM|Cum|cum|Rocket|rocket|Shib|shib|Moon|moon|Money|money|Economy|economy|Market|market"

# Regular expression pattern for uppercase characters
regex_uppercase_pattern = ['[A-Z]+']

# Timestamp
timestamp = format(datetime.datetime.now())

# Iterator
i = 1

## Functions ##

# Convert a list to a string  
def listToString(s):     
    str1 = ""      
    for ele in s: 
        str1 += ele      
    return str1

# Remove characters from regex  
def format_regex(r):
    r.replace("\'", "").replace(" ", "").replace("[", "").replace("]", "").replace(",", "")
    return r

# Escape character that break INSERT
def format_tweet(t):
    t.replace("\'", "\\\'").replace("\"", "\\\"")
    return t

# Make tweet URL - this can also be retrieved from new_tweet_contents with ["url"]
def make_url():
    url = "https://twitter.com/" + twitter_handle + "/status/" + format(new_tweet_id)
    return url

# Print to console
def print_console():
    print("Iteration:", i)
    print("Timestamp:", timestamp)
    print("Twitter Handle: @" + twitter_handle)
    # Tweets
    print("Tweet ID:", new_tweet_id)
    print("Tweet Hashtags:", listToString(new_tweet_hashtags))
    print("Tweet Text:", new_tweet_text)       
    try:
        # Regular expression for keywords
        regex = re.search(keywords, new_tweet_text + new_tweet_hashtags)
        try:
            print("Keywords:", regex[0])
            regex = regex[0]
        except:
            print("Keywords:", regex)
        for p in regex_uppercase_pattern:
            regex_uppercase = format_regex(listToString(re.findall(p, new_tweet_text)))
        print("Upper Case:", regex_uppercase)
    except:
        print("Regex error")
    print("Tweet URL:", make_url(), "\n")

# Message Discord
""" def message_discord_text():
    embed = DiscordEmbed(title='@' + twitter_handle, description=new_tweet_text, color='03b2f8')
    # add fields to embed
    embed.add_embed_field(name='Keywords', value=regex)
    embed.add_embed_field(name='URL', value=make_url())
    # add embed object to webhook
    webhook.add_embed(embed)
    response = webhook.execute() """

# Create twitter table if it doesn't exist
if database:  
    table_query = "CREATE TABLE " + table_name + " (" + table_name + "_pkey SERIAL PRIMARY KEY, twitter_handle TEXT, tweet_id NUMERIC, hashtags TEXT, tweet_text TEXT, keywords TEXT, uppercase TEXT, tweet_url TEXT, profile_photo_url TEXT, profile_banner_url TEXT, timestamp TEXT);" 
    try:
        create_table(table_name, table_query)
    except:
        print("Create table error")

## Run once before looping ##
# Get Twitter profile data
try:
    profile = tw.get_profile(name=twitter_handle).__dict__
    profile_photo = profile["profileurl"]
    profile_banner = profile["bannerurl"]
    twitter_id = profile["id"]
except:
    print("Bad initial profile")
    print("Try again")
    exit()

# Get last 2 tweets and compare IDs to filter up to 1 pinned tweet
try:
    last_tweet_contents = tw.get_tweets(twitter_id, count=2).contents
    last_tweet_id = last_tweet_contents[0]["id"]
    last_tweet_id_2 = last_tweet_contents[1]["id"]
    if last_tweet_id_2 > last_tweet_id:
        last_tweet_id = last_tweet_id_2
        old_tweet = 0
    else:
        old_tweet = 1
    new_tweet_hashtags = listToString(last_tweet_contents[old_tweet]["hashtags"])
    # Log to database if not present
    #if check_table(last_tweet_id, tweet_id, table_name) == False
        #last_tweet_query = "INSERT INTO " + table_name + " (twitter_handle, tweet_id, hashtags, tweet_text, keywords, uppercase, tweet_url, profile_photo_url, profile_banner_url, timestamp) VALUES('" + twitter_handle + "', '" + format(last_tweet_id) + "', '" + last_tweet_hashtags + "', '" + format_tweet(last_tweet_text) + "', '" + format(regex) + "', '" + regex_uppercase + "', '" + make_url() + "', '" + new_profile_photo + "', '" + new_profile_banner + "', '" + timestamp + "');"
        #new_row(last_tweet_query)
except:
    print("No tweets detected")
    print("Try again")
    exit()

""" if check_table(last_tweet_id, tweet_id, twitter) != True:
    row_query = "INSERT INTO " + table_name + " (twitter_handle, tweet_id, hashtags, tweet_text, keywords, uppercase, tweet_url, profile_photo_url, profile_banner_url, timestamp) VALUES('" + twitter_handle + "', '" + format(new_tweet_id) + "', '" + new_tweet_hashtags + "', '" + format_tweet(new_tweet_text) + "', '" + format(regex) + "', '" + regex_uppercase + "', '" + make_url() + "', '" + new_profile_photo + "', '" + new_profile_banner + "', '" + timestamp + "');"
        try:
            new_row(row_query) 
        except:
            print("Database not detected") """

## Scrape Twitter and open in browser if new tweet, profile photo changed, or banner changed ##
while True:
    try:
        # Get new profile data
        new_profile = tw.get_profile(name=twitter_handle).__dict__
        new_profile_photo = new_profile["profileurl"]
        new_profile_banner = new_profile["bannerurl"]
    except:
        print("Bad profile \n")
    try:
        # Get 2 latest tweets and compare IDs to filter up to 1 pinned tweet
        new_tweet_contents = tw.get_tweets(twitter_id, count=2).contents
        new_tweet_id = new_tweet_contents[1]["id"]
        new_tweet_id_2 = new_tweet_contents[0]["id"]
        if new_tweet_id_2 > new_tweet_id:
            newest_tweet = 0
            new_tweet_id = new_tweet_id_2
        else:
            newest_tweet = 1
        new_tweet_text = new_tweet_contents[newest_tweet]["text"]
        new_tweet_hashtags = listToString(new_tweet_contents[newest_tweet]["hashtags"])
        # Compare new tweet to last tweet
        if open_browser:
            if new_tweet_id != last_tweet_id and new_tweet_id > last_tweet_id:
                webbrowser.open(make_url(), new=1)
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
        print("Iteration:", i)
        print("Timestamp:", timestamp)
        print("Twitter Handle: @" + twitter_handle)
        # Tweets
        print("Tweet ID:", new_tweet_id)
        print("Tweet Hashtags:", listToString(new_tweet_hashtags))
        print("Tweet Text:", new_tweet_text)       
        try:
            # Regular expression for keywords
            regex = re.search(keywords, new_tweet_text + new_tweet_hashtags)
            try:
                print("Keywords:", regex[0])
                regex = regex[0]
            except:
                print("Keywords:", regex)
            for p in regex_uppercase_pattern:
                regex_uppercase = format_regex(listToString(re.findall(p, new_tweet_text)))
            print("Upper Case:", regex_uppercase)
        except:
            print("Regex error")
        print("Tweet URL:", make_url(), "\n")
  
    #print_console()

    ## Send tweet to discord
    try:
        # Discord web hook, URL defined in secrets.py
        if discord and new_tweet_id > last_tweet_id:
            webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL)
            embed = DiscordEmbed(title='@' + twitter_handle, description=new_tweet_text, color='03b2f8')
            # add fields to embed
            if regex != None:
                embed.add_embed_field(name='Keywords', value=regex)
            embed.add_embed_field(name='URL', value=make_url())
            # add embed object to webhook
            webhook.add_embed(embed)
            response = webhook.execute()
    except:
        print("Discord error", "\n")

    ## Print results to log if new tweet, profile URL changed, or banner changed ##
    try:
        # Tweets
        if log and new_tweet_id > last_tweet_id:
            with open("twitter.log", "a", encoding="utf-8") as log:
                sys.stdout = log 
                print("Timestamp:", timestamp)
                print("Twitter Handle: @" + twitter_handle)
                print("Tweet ID:", new_tweet_id)
                print("Tweet Hashtags:", listToString(new_tweet_hashtags))
                print("Tweet Text:", new_tweet_text)
                print("Keywords:", regex)
                print("Upper Case:", regex_uppercase)
                print("Tweet URL:", make_url(), "\n")
                # Reset the standard output
                sys.stdout = original_stdout 
        # Photo
        if new_profile_photo != profile_photo:
            with open("twitter.log", "a") as log:
                sys.stdout = log 
                print("Timestamp:", timestamp)
                print("Twitter Handle: @" + twitter_handle)
                print("Profile URL:", new_profile_photo, "\n")
                # Reset the standard output
                sys.stdout = original_stdout
        # Banner
        if new_profile_banner != profile_banner:
            with open("twitter.log", "a") as log:
                sys.stdout = log 
                print("Timestamp:", timestamp)
                print("Twitter Handle: @" + twitter_handle)
                print("Banner URL:", new_profile_banner, "\n")
                # Reset the standard output
                sys.stdout = original_stdout
    except:
        print("Log error \n")

    ## Update twitter table in database ##
    if database and (new_tweet_id > last_tweet_id or new_profile_photo != profile_photo or new_profile_banner != profile_banner):
        row_query = "INSERT INTO " + table_name + " (twitter_handle, tweet_id, hashtags, tweet_text, keywords, uppercase, tweet_url, profile_photo_url, profile_banner_url, timestamp) VALUES('" + twitter_handle + "', '" + format(new_tweet_id) + "', '" + new_tweet_hashtags + "', '" + format_tweet(new_tweet_text) + "', '" + format(regex) + "', '" + regex_uppercase + "', '" + make_url() + "', '" + new_profile_photo + "', '" + new_profile_banner + "', '" + timestamp + "');"
        try:
            new_row(row_query) 
        except:
            print("Database not detected")     
    
    ## Play sound if keyword found or image changed ##
    try:
        if play_sounds and ((re.search(keywords, new_tweet_text) and new_tweet_id > last_tweet_id) or (new_profile_photo != profile_photo) or (new_profile_banner != profile_banner)):
            winsound.PlaySound("sound2.wav", winsound.SND_ASYNC)
    except:
        print("Error playing sound", "\n")
        
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