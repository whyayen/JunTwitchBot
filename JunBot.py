# -*- coding: utf-8 -*-
import sys, os
import socket
import requests
import time
import os
import yaml
import json
from irc import Irc
import re
import random
import math
def get_userList(channel):
    users = []
    session = requests.session()
    response = session.get('https://tmi.twitch.tv/group/user/%s/chatters' % channel).text
    data = json.loads(response)
    users = data['chatters']['moderators']
    users.extend(data['chatters']['viewers'])
    return users

def get_userPoint(token, channel, user):
    session = requests.session()
    headers = {'Authorization': 'Bearer %s' % token}
    response = session.get('https://api.streamelements.com/kappa/v1/points/%s/%s' % (channel, user), headers = headers).text
    data = json.loads(response)
    return data['points']

def change_userPoint(token, user, value):
    session = requests.session()
    headers = {'Authorization': 'Bearer %s' % token}
    session.put('https://api.streamelements.com/kappa/v1/points/%s/%d' % (user, value), headers = headers)

def main(config):
    twitch = config['twitch']

    irc = Irc(twitch)

    user = []
    print("Press Ctrl+C to kill the bot")
    
    try:
        k = True
        challenger = ["", ""]
        points = 0
        gap_time = time.time()
        while True:
            recv_msg = irc.get_socket()
            
            if(re.match(r'^[a-zA-Z0-9\.\_\-]+ .*$', str(recv_msg))):
            
                recv_arg = recv_msg.split(" ", 1)
                if(re.match(r'\!pk [a-zA-Z0-9\.\_\-]+', recv_arg[1]) and (k == True or (time.time() - gap_time) > 10)):
                    args = recv_msg.split(" ", 2)
                    
                    point = get_userPoint(config['api']['JWT_token'], twitch['channel'], args[0])
                    if(point == 0):
                        irc.send_message(twitch['channel'], "%s 您的戰鬥力不足！" % args[0])
                        time.sleep(10)
                    else:
                        users = get_userList(twitch['channel'])
                        if(args[2].strip().lower() in users or args[2].strip() != args[0].strip()):
                            irc.send_message(twitch['channel'], "%s 戰鬥力 %s 的 %s 向您發起挑戰，是否接受(y/n)?" % (args[2], point, args[0]))
                            challenger[0] = args[0].strip()
                            challenger[1] = args[2].strip()
                            points = point
                            k = False
                            gap_time = time.time()
                        else:
                            irc.send_message(twitch['channel'], "%s 找不到使用者:%s" % (args[0], args[2]))
                            time.sleep(10)
                elif(recv_arg[0].strip() == challenger[1] and recv_arg[1].strip().lower() == 'y'):
                    
                    point = get_userPoint(config['api']['JWT_token'], twitch['channel'], recv_arg[0].strip())
                    if(point == 0):
                        irc.send_message("%s 您的戰鬥力不足！" % recv_arg[0])
                        k = True
                        time.sleep(10)
                    else:
                        allpoint = points + point
                        nums = random.randint(0, 101)
                        if(nums <= math.ceil((points / allpoint) * 100)):
                            change_userPoint(config['api']['JWT_token'], challenger[0], point * 0.2)
                            change_userPoint(config['api']['JWT_token'], challenger[1], 0-(point * 0.2))
                            irc.send_message(twitch['channel'], "%s 恭喜您獲勝，獲得 %d 戰鬥力" % (challenger[0], point * 0.2))
                            irc.send_message(twitch['channel'], "%s 戰鬥失敗，失去 %d 戰鬥力" % (challenger[1], point * 0.2))
                        else:
                            change_userPoint(config['api']['JWT_token'], challenger[1], points * 0.2)
                            change_userPoint(config['api']['JWT_token'], challenger[0], 0 - (points * 0.2))
                            irc.send_message(twitch['channel'], "%s 恭喜您獲勝，獲得 %d 戰鬥力" % (challenger[1], points * 0.2))
                            irc.send_message(twitch['channel'], "%s 戰鬥失敗，失去 %d 戰鬥力" % (challenger[0], points * 0.2))
                        k = True
                        time.sleep(10)
                elif(recv_arg[0].strip() == challenger[1] and recv_arg[1].strip().lower() == 'n'):
                    irc.send_message(twitch['channel'], "戰鬥發起失敗")
                    k = True
                    time.sleep(10)
    except KeyboardInterrupt:
        print("Leaving channel")
    finally:
        irc.leave(twitch['channel'])

if __name__ == '__main__':
  lines = open(os.path.dirname(__file__)+'/config.yml').read()
  config = yaml.load(lines)
  main(config)
