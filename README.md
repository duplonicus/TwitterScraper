# Info

This script was originally created to gain an advantage in crypto trading but can be used for other purposes. For example, logging Michael Burry's cryptic tweets before he deletes his twitter account. It loops every 5 seconds and checks the last tweet of the specified account for keywords, photo changes, and banner changes. If a keyword is detected or an image changes it plays a sound. It opens the default browser to new tweets and image changes as well. Results are displayed in the console and logged to twitter.log and a PostgreSQL database. 

# Setup for Windows

1. Install Python3

2. Run "pip install -r requirement.txt"

3. Install PostgreSQL and create a database

4. Rename new_db.ini to db.ini and fill it out with your database connection info

5. Run "python3 create_table.py"

# How to use

Run "python3 twitter.py" to scrape Elon Musk

Run "python3 twitter.py username" to scrape someone else
Example: "python3 twitter.py michaeljburry"

The keywords variable can be modified within twitter.py and are seperated by the | symbol

# Screenshot

![Screenshot](https://i.imgur.com/KvDBJRf.png)