# Instructions for Windows

1. Install Python3

2. Install PostgreSQL and create a database

3. Run "pip install -r requirement.txt"

4. Create db.ini and fill it out with your database connection info:
[postgresql]
host=
database=
user=
password=

5. Run "python3 create_table.py"

6. Run "python3 twitter.py username" to start scraping. If username is left blank, it defaults to elonmusk

# Screenshot

![Screenshot](https://i.imgur.com/KvDBJRf.png)