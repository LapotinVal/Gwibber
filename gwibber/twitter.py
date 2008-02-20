#!/usr/bin/env python

"""

Twitter interface for Gwibber
SegPhault (Ryan Paul) - 12/22/2007

"""

import urllib2, urllib, base64, simplejson, gtk
import time, datetime, gwui, config, gaw

from gwui import StatusMessage, ConfigPanel

def parse_time(t):
  return datetime.datetime.strptime(t, "%a %b %d %H:%M:%S +0000 %Y")

class Message:
  def __init__(self, client, data):
    self.client = client
    self.account = client.account
    self.data = data
    self.sender = data["user"]["name"]
    self.sender_nick = data["user"]["screen_name"]
    self.sender_id = data["user"]["id"]
    self.time = parse_time(data["created_at"])
    self.text = data["text"]
    self.image = data["user"]["profile_image_url"]
    self.bgcolor = "message_color"

  def is_new(self):
    return self.time > datetime.datetime(
      *time.strptime(config.Preferences()["last_update"])[0:6])

class Client:
  def __init__(self, acct):
    self.account = acct

  def can_send(self): return True
  def can_receive(self): return True

  def send_enabled(self):
    return self.account["send_enabled"] and \
      self.account["username"] != None and \
      self.account["password"] != None

  def receive_enabled(self):
    return self.account["receive_enabled"] and \
      self.account["username"] != None and \
      self.account["password"] != None

  def get_auth(self):
    return "Basic %s" % base64.encodestring(
      ("%s:%s" % (self.account["username"], self.account["password"]))).strip()

  def connect(self, url, data = None):
    return urllib2.urlopen(urllib2.Request(
      url, data, {"Authorization": self.get_auth()})).read()

  def get_data(self):
    return simplejson.loads(self.connect(
      "http://twitter.com/statuses/friends_timeline.json"))

  def get_messages(self):
    for data in self.get_data():
      yield Message(self, data)

  def transmit_status(self, message):
    return self.connect("http://twitter.com/statuses/update.json",
        urllib.urlencode({"status":message}))