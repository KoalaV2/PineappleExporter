#!/usr/bin/env python3

import json
import time
import prometheus_client
from dotenv import load_dotenv
import urllib3
import os

load_dotenv()
PINEAPPLE_IP=os.getenv("PINEAPPLE_IP")
PINEAPPLE_PASS=os.getenv('PINEAPPLE_PASS')

cpugauge = prometheus_client.Gauge('pineapple_cpu', 'Pineapples CPU Usage')
ramgauge = prometheus_client.Gauge('pineapple_memory', 'Pineapples RAM Usage')
clientsgague = prometheus_client.Gauge('pineapple_clients', 'Pineapples current connected clients')
rootusagegauge = prometheus_client.Gauge('pineapple_rootusage', 'Pineapples root disk usage')
prevclientsgauge = prometheus_client.Gauge('pineapple_prevclients', 'Pineapples previously connected clients')

http = urllib3.PoolManager()

def auth():
    data = '{"username": "root", "password": "' + PINEAPPLE_PASS + '"}'
    response = http.request('POST', f'http://{PINEAPPLE_IP}:1471/api/login', body=data)
    responsedata = json.loads(response.data.decode('utf-8'))
    token = responsedata['token']
    return token

def data(token):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Authorization': token,
        'Connection': 'keep-alive',
        'Sec-GPC': '1',
        'DNT': '1',
        'Cache-Control': 'max-age=0',
    }

    response = http.request('GET', f'http://{PINEAPPLE_IP}:1471/api/dashboard/cards', headers=headers)
    jsondata = json.loads(response.data.decode('utf-8'))
    print(json.dumps(jsondata, indent=4, sort_keys=True))
    clients = jsondata['clientsConnected']
    diskusage = jsondata['diskUsage']
    systemstatus = jsondata['systemStatus']
    cpuusage = systemstatus['cpuUsage'].strip('%')
    memoryusage = systemstatus['memoryUsage'].strip('%')
    rootusage = diskusage['rootUsage'].strip('%')
    prevclients = jsondata['previousClients']

    cpugauge.set(cpuusage)
    ramgauge.set(memoryusage)
    clientsgague.set(clients)
    rootusagegauge.set(rootusage)
    prevclientsgauge.set(prevclients)


def main():
    token = auth()
    prometheus_client.start_http_server(9090)
    while True:
        data(token)
        time.sleep(10)
if __name__ == '__main__':
    main()
