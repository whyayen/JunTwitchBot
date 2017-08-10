#encoding=utf-8
import socket, re, time, sys

class Irc:

  def __init__(self, config):
    self.config = config
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.settimeout(30)
    self.get_irc_socket_object()

  def close():
    self.sock.close()

  def check_login_status(self, data):
    data = data.decode("utf-8")
    if re.match(r'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
      return False
    else:
      return True

  def send(self, msg):
    msg += '\r\n'
    self.sock.send(msg.encode())
    print("Sending message: {}".format(msg))

  def send_message(self, channel, message):
    self.send('PRIVMSG #{} :{}'.format(channel, message))

  def get_irc_socket_object(self):
    try:
      self.sock.connect((self.config['server'], int(self.config['port'])))
    except Exception as e:
      print('Cannot connect to server ({}:{}).'.format((self.config['server'], self.config['port']), 'error'))
      print("{}".format(e))

    self.sock.settimeout(None)

    self.send('USER {}'.format(self.config['username']))
    self.send('PASS {}'.format(self.config['password']))
    self.send('NICK {}'.format(self.config['username']))
    self.send("CAP REQ :twitch.tv/membership")
    self.send("CAP REQ :twitch.tv/commands")
    self.send("CAP REQ :twitch.tv/tags")

    if self.check_login_status(self.sock.recv(1024)):
      print('Log into TwitchIRC successful.')
    else:
      print("Log into TwitchIRC Unsuccessful.")
      sys.exit()

    self.join(self.config['channel'])
    return self.sock

  def join(self, channel):
    self.send('JOIN #{}'.format(channel))

  def leave(self, channel):
    self.send('PART {}'.format(channel))

  def get_socket(self):
    tmp = self.sock.recv(1024).decode('utf-8','replace')
    if( 'PING' in tmp[:len(tmp)]):
        self.send('PONG :tmi.twitch.tv')
    else:
        main_msg = re.search(r'@[a-zA-Z0-9\_\.\-]+\.tmi\.twitch\.tv PRIVMSG \#[a-zA-Z0-9\_\.\-]+ :.*', tmp)
        if(main_msg):
            strs = ""
            strs += main_msg.group().split(" ",3)[0].replace('.tmi.twitch.tv', '')[1:] + " "
            strs += main_msg.group().split(" ",3)[3].replace(':', '')
            return strs
        else:
            return tmp
