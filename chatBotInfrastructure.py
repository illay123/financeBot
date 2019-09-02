#!/usr/bin/env python3
"""script for the chat bot, handles every chat as a finite state machine"""

#**********************************************imports*********************************************#
import sys
import json
import time
import unittest
import requests
import ast
import logging
#**************************************************************************************************#

TOKEN = "660462542:AAFGXJ3D8iYC3Sai8Grouysz2TIdya-9fL8" #get rid of this
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
DBA = "http://127.0.0.1:8080/" #why not config?

#*********************************************util*********************************************#
def stripParameters(txt):
    """get parameters out of messege and retrun dict"""
    d = {}
    name = False
    val = ""
    p = ''
    i = 0
    while i < len(txt):
        if not name and txt[i] == '-' and txt[i+1] == '-':
            # print("here1: ", i)
            name = True
            i += 2
            p = txt[i]
            i += 1
        elif name and txt[i] == '-' and txt[i+1] == '-':
            # print("here2: ", i)
            d[p] = val[:-1]
            name = True
            i += 2
            p = txt[i]
            i += 1
            val = ""
        elif name:
            # print("here3: ", i, val)
            val += txt[i]
        i += 1
    # print("here4: ", i, p, val)
    d[p] = val
    logging.debug(d)
    return d

def get_url(url):
    """simple url request"""
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    """extract the json from http response"""
    content = get_url(url)
    js = json.loads(content)
    return js
#**************************************************************************************************#
class State():
    """state for the state machine"""
    def __init__(self, num, preQuestion, postQuestion):
        super(State, self).__init__()
        self.num = num
        self.pre = preQuestion
        self.post = postQuestion
    # arg should be dict
    # return question
    def pre_question(self, arg):
        """use first half of the state"""
        return self.pre(arg)
    # return state
    def post_question(self, arg, text):
        """second half of the state"""
        return self.post(arg, text)

#**************************************************************************************************#
class Session():
    """a session object created for every chat, hold the current state"""
    def __init__(self, chat_id):
        super(Session, self).__init__()
        self.current = STARTSTATE
        self.chat_id = chat_id
        self.arg = {}

    def send_message(self, text):
        """the only method for messege sending"""
        debug_print("actually sending?")
        url = URL + "sendMessage?text={}&chat_id={}".format(text, self.chat_id)
        get_url(url)

    def process(self, text):
        """send the messege text to the state for process
        move the state acordingly"""
        self.current = self.current.post_question(self.arg, text)
        debug_print(self.current.num)
        opt = self.current.pre_question(self.arg)
        debug_print("opt is: "+str(opt))
        if opt is None:
            debug_print("shoutDown session "+str(self.chat_id))
            self.send_message("Bye Bye")
            return -1
        elif opt is not None:
            debug_print("place")
            self.send_message(opt)

class Bot():
    """take updates from the instegram server"""
    def __init__(self, token, url):
        super(Bot, self).__init__()
        self.token = token
        self.url = url
        self.dict = {}

    def get_updates(self, offset=None):
        """get updates from the server by http"""
        nurl = self.url + "getUpdates?timeout=60"
        if offset:
            nurl += "&offset={}".format(offset)
        js = get_json_from_url(nurl)
        return js

    def get_last_update_id(self, updates):
        """figure what should be the id of the next message"""
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)

    def process(self, update):
        """pass the message to the right session for more processing"""
        try:
            debug_print("try1")
            text = update["message"]["text"]
        except KeyError:
            print("[INFO] - got image, cant process")
            text = "img"
        chat_id = update["message"]["chat"]["id"]
        try:
            debug_print("try2")
            ses = self.dict[chat_id]
            if ses is None:
                ses = Session(chat_id)
                self.dict[chat_id] = ses
        except KeyError:
            ses = Session(chat_id)
            self.dict[chat_id] = ses
        v = ses.process(text)
        if v == -1:
            self.dict[chat_id] = None

    def start(self):
        """main loop of the program"""
        last_update_id = None
        while True:
            # print(last_update_id)
            debug_print("updates?")
            updates = self.get_updates(last_update_id)
            if len(updates["result"]) > 0:
                debug_print("sure!")
                last_update_id = self.get_last_update_id(updates) + 1
                for update in updates["result"]:
                    self.process(update)
            time.sleep(0.5)
            # self.send_message(text, chat)

#***********************************************test***********************************************#
class TestMethods(unittest.TestCase):
    """test for the non class functions"""
    def test_dont_exist(self):
        """just a test..."""
        self.assertTrue(dont_exist("1"))
        self.assertFalse(dont_exist("972502006108"))

    # def test_isupper(self):
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())

    # def test_split(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)
class TestState(unittest.TestCase):
    """test for the state class"""
    def function(self):
        """actually empty"""
        pass