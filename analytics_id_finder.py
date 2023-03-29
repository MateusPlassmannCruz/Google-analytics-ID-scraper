import csv, json
import sys
import psycopg2
import requests
import re
import itertools
from bs4 import BeautifulSoup

con = psycopg2.connect(host="localhost",
                       port="5432",
                       user="your_database_user",
                       password="your_database_user_password",
                       database="your_database_name")

cur = con.cursor()

link_filter = '^(https?:\/\/[^\/]+)'
url_list = []
with open('malicious_websites_dataset.cvs') as File:
    reader = csv.DictReader(File)

    for rows in itertools.islice(reader, 1000):
        urls = rows['url']
        filtered_link = re.match(link_filter, urls)

        if filtered_link:
            filtered = filtered_link.group(0)
            url_list.append(filtered)
        else:
            print("Error filtering link") 

for url in itertools.islice(url_list, 100):
    try:
        page_content = requests.get(url).content
        page_content
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        continue
    soup = BeautifulSoup(page_content, 'html.parser')

    google_analytics = str(soup.find_all('script'))
    regex = r"(?:UA|YT|MO)-\d{4,}-\d{1,2}"
    match = re.search(regex, google_analytics)

    if match:
        print(f"Google Analytics ID {match.group(0)} found for {url}")

        cur.execute("""
		INSERT INTO google_id (site_name, analytics_id)
		VALUES (%s, %s)
		""",
		(
			url,
			match.group(0)
		)	
	)	
    else:
        print("Google Analytics ID not found")
    
con.commit();

cur.close()
con.close()
