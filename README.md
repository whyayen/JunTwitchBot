# JunTwitchBot

## Introduce
This is an Twitch bot using StreamElements API in Python.
Chatter can input !pk instruction to fight with anthoer one.
The system will ask anthoer chatter does him want to accept the fight.
If chatter input 'y', the system will count their points.

The chatter A's win rate **W** is:
**W** = (A's points) / ( A's points + B's points)

Generate a random number **X** between 0 and 100.
If **X** <= **W** Then A get (B's points * 0.2), or not B get (A's points * 0.2)

## How to use?
1. run ``$ pip install -r requirements.txt``
2. Rename ``sameple.config.yml`` to ``config.yml``
```
twtich:
  password: # The Twitch tmi Oauth 2 token
  channel: # The channel you want to stay in
  username: # Your bot username
  server: irc.chat.twitch.tv
  port: 6667
 api:
  JWT_token: StreamElements JWT_token
```
3. run ``$ python JunBot.py``
