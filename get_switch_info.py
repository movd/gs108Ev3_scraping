#!/usr/bin/env python3

import requests
from dotenv import load_dotenv
import os
import sys
import datetime
from bs4 import BeautifulSoup

load_dotenv()

NETGEAR_PASSWORD = os.getenv('NETGEAR_PASSWORD')
NETGEAR_IPV4 = os.getenv('NETGEAR_IPV4')

data = {'password': NETGEAR_PASSWORD}

admin_url = (f'http://{NETGEAR_IPV4}')

# Routes
login_url = (f'{admin_url}/login.cgi')
switch_info_url = (f'{admin_url}/switch_info.htm')

s = requests.Session()

post_response = s.post(
    login_url,
    data=data
    )
response = s.get(switch_info_url)

# Abort if wrong password
text = 'The password is invalid.'
if text in post_response.text:
    print('‍🤦🏽‍ Wrong Password!')
    sys.exit()

# Abort if maximum connections reached
text = 'The maximum number of attempts has been reached'
if text in post_response.text:
    print('🔥  Slow down! Maxium connections reached')
    sys.exit()

soup = BeautifulSoup(response.text, 'html.parser')

# soup = BeautifulSoup(html_string, 'html.parser')

live_settings = {}

# Scrape table rows
table_rows = soup.select("#tbl1 tr")

for table_row in table_rows:
    cells = table_row.findAll('td')
    if len(cells) > 0:
        if cells[0].text:
            option = cells[0].get_text().strip().replace(" ", "")
        if len(cells[1].get_text().strip()) > 0 :
            parameter = cells[1].get_text().strip()
        else:
            parameter = cells[1].find('input')['value'].strip()
        # Populate the dictionary
        live_settings[option] = parameter


# Create a nice output: 
print(f'''
{live_settings['SwitchName']} runs version @ {live_settings['FirmwareVersion']}
''')

    

