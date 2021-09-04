# Info

This script was originally created to gain an advantage in crypto trading (thanks Elon) but can be used for other purposes. For example, logging all of an account's tweets in case of tweet or account deletion. 

It loops every 5 seconds (can be changed with --frequency) and checks the last tweet of the specified account for keywords, profile photo changes, and banner changes. If a keyword is detected or an image changes, it plays a sound. It opens a new tab in the default browser to new tweets and images. Tweets are also analyzed for sentiment with NTLK. 

Results are displayed in the console, sent to Discord, logged to twitter.log, and a PostgreSQL database (optional). Comand line arguments can be supplied for username, table name, and to disable certain functionality. Twitter API key not required.

# Setup for Windows

1. Install Python3

2. Run "pip install -r requirements.txt"

3. Run nltk_setup.py (required for sentiment analysis)

4. Rename new_secrets.py to secrets.py and fill in a Discord webhook URL

### Complete the rest of the steps if a database is desired:

5. Install PostgreSQL and create a database

6. Rename new_db.ini to db.ini and fill in the database connection info

# How to use

Run "python3 twitter.py" to scrape the default account set in the argument parser definition.

Run "python3 twitter.py username" to scrape a different account.  
Example: "python3 twitter.py michaeljburry"

Run "python3 twitter.py username --tablename newtable" to create and use a different table in the database.  
Example: "python3 twitter.py michaeljburry --tablename stocks"

Keywords are stored in keywords.txt. Each word is on a new line. Specify a different file with --wordlist.  
Example: python3 twitter.py michaeljburry --wordlist stocks.txt

All functioinality is enabled by default but can be turned off with --noconsole, --nolog, --nobrowser, --nosounds,  
--nodb, and --nodiscord.  
Example: "python3 twitter.py michaeljburry --tablename stocks --nobrowser --nodiscord"

# Screenshots

![Screenshot](https://i.imgur.com/h8KvGd6.png)

![Screenshot](https://i.imgur.com/dpxorp8.png)

![Screenshot](https://i.imgur.com/lvAWToB.png)

![Screenshot](https://i.imgur.com/bhpmsxh.png)