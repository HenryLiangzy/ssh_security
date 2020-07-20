#!/usr/bin/env python3

import os
import sys
import json
import time
import socket
import requests

header = {
    'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/81.0.4044.129 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'Accept-encoding': 'gzip, deflate, br',
    'Accept-language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive'
}


class loginMessage(object):

    def __init__(self, username, ip, hostname):
        self.username = username
        self.ip = str(ip)
        self.hostname = hostname
        self.time = time.strftime("%b %d %H:%M:%S", time.localtime())
        self.detail = None

        # get the detail of ip address
        self.get_detail()

    def get_detail(self):
        url = f'http://ip-api.com/json/{self.ip}'
        r = requests.get(url, headers=header)
        self.detail = r.json()

    def __str__(self):
        message = f'Time: {self.time}\nIP: {self.ip}\nHostname: {self.hostname}\n'
        detail = list()
        for key in self.detail:
            detail.append(f'{key}: {self.detail[key]}')

        return message + '\n'.join(detail)


def send_tg_message(message: loginMessage, token, chat_id):
    url = f'https://api.telegram.org/bot{token}'
    hint_message = 'Hi Master, I found new SSH login on server, detail as follow:\n'

    # send the text message to user
    payload = {
        "chat_id": chat_id,
        "text": hint_message+str(message)
    }
    r = requests.post(url+'/sendMessage', json=payload)

    # send the location message to user
    payload = {
        "chat_id": chat_id,
        "latitude": str(message.detail['lat']),
        "longitude": str(message.detail['lon'])
    }
    r = requests.post(url+'/sendLocation', json=payload)


def send_email(message: loginMessage):
    pass


def main():
    # load login data from system
    try:
        clientIp, clientPort, serverIp, serverPort = os.getenv("SSH_CONNECTION").split()
    except AttributeError as e:
        raise e

    hostname = socket.gethostname()
    username = os.getenv("USER")

    # get login IP address detail and output to terminal
    message = loginMessage(username, clientIp, hostname)
    print(message)

    # check if telegram bot configure file exist then execute
    if os.path.isfile('tgbot.json'):
        with open('tgbot.json', 'r') as fp:
            bot_figure = json.load(fp)

        send_tg_message(message, bot_figure['token'], bot_figure['chat_id'])

    if os.path.isfile('email.json'):
        pass
    

if __name__ == "__main__":
    main()
