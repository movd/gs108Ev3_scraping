#!/usr/bin/env python3

import requests
from dotenv import load_dotenv
import os
import sys
import datetime
from bs4 import BeautifulSoup
from hurry.filesize import size

load_dotenv()


NETGEAR_PASSWORD = os.getenv('NETGEAR_PASSWORD')
NETGEAR_IPV4 = os.getenv('NETGEAR_IPV4')

data = {'password': NETGEAR_PASSWORD}

admin_url = (f'http://{NETGEAR_IPV4}')

# Routes
login_url = (f'{admin_url}/login.cgi')
port_statistics_url = (f'{admin_url}/port_statistics.htm')

s = requests.Session()

post_response = s.post(
    login_url,
    data=data
)
response = s.get(port_statistics_url)

# Abort if wrong password
text = 'The password is invalid.'
if text in post_response.text:
    print('‍🤦🏽‍ Wrong Password!')
    sys.exit()

# Abort if maximum connections reached
text = 'The maximum number of attempts has been reached'
if text in post_response.text:
    print('🔥  Slow down! Maximum connections reached')
    sys.exit()

soup = BeautifulSoup(response.text, 'html.parser')

port_statistics = {}

switch_port_cells = soup.select('td.firstCol')

# Create Dict of Switch Ports
for cell in switch_port_cells:
    switch_port = int(cell.get_text().strip())
    port_statistics[switch_port] = {
        'BytesReceived': 0, 
        'BytesSent': 0,
        'CRCErrorPackets': 0
    }

# Populate Dict
# Bytes Received
rx_cells = soup.select('input[name="rxPkt"]')
switch_port = 1
for cell in rx_cells:
    # Convert to bytes Hex to Decimal
    nbytes_rx = int(cell['value'].strip(), 16)
    # Store a nice human readable string
    port_statistics[switch_port]['BytesReceived'] = nbytes_rx
    switch_port += 1

# Bytes Sent
tx_cells = soup.select('input[name="txpkt"]')
switch_port = 1
for cell in tx_cells:
    # Convert to bytes Hex to Decimal
    nbytes_tx = int(cell['value'].strip(), 16)
    port_statistics[switch_port]['BytesSent'] = nbytes_tx
    switch_port += 1

# CRC Error Packets
crc_cells = soup.select('input[name="crcPkt"]')
switch_port = 1
for cell in crc_cells:
    # Convert to bytes Hex to Decimal
    crc_packet = int(cell['value'].strip(), 16)
    port_statistics[switch_port]['CRCErrorPackets'] = crc_packet
    switch_port += 1

# Output in a human readable format
for port_id, stats in port_statistics.items():
    all_zero = all(v == 0 for v in stats.values())
    if not all_zero:
        nice_rx = size(stats["BytesReceived"])
        nice_tx = size(stats["BytesSent"])
        print(
            f'''Port {port_id}: [RX: {nice_rx}] [TX: {nice_tx}] [CRC: {stats["CRCErrorPackets"]}]''')


