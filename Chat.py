#!/usr/bin/env python3
"""script for the chat bot, handles every chat as a finite state machine"""

#**********************************************imports*********************************************#
import sys
import json
import time
import unittest
import requests
import ast
#**************************************************************************************************#

TOKEN = "660462542:AAFGXJ3D8iYC3Sai8Grouysz2TIdya-9fL8"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
DBA = "http://127.0.0.1:8080/"

#*********************************************util*********************************************#
DEBUG = False

class datetime(object):
    """docstring for datetime"""
    def __init__(self, arg):
        super(datetime, self).__init__()
        self.arg = arg
    def date(a,b,c):
        return str(c)+"\\"+str(b)+"\\"+str(a)
    def timedelta(a,b):
        return b/60

def Decimal(a):
    return float(a)

def getClassesByName(name):
    res = get_url(DBA+"""getCustomerClasses/?cname="""+name)
    if res == "":
        return None
    else:
        return res

def cleanClasses(response):
    debug_print("[cleanClasses] - got: "+ response)
    if response == None:
        return "no classes recorded yet"
    payList = eval(response)
    s = "num - date - length(min) - price(nis)\n"
    for pay in payList:
        # p = ast.literal_eval(pay)
        s+=str(pay[0])+" - "+pay[1]+" - "+str(pay[3])+" - "+str(pay[4])+"\n"
    return s


        

def getBalaceByName(name):
    res = get_url(DBA+"""getCustomerBalance/?cname="""+name)
    if res == "":
        return None
    else:
        return res

def getPaymentsByName(name):
    res = get_url(DBA+"""getCustomerTransactions/?cname="""+name)
    if res == "":
        return None
    else:
        return res
def cleanPayments(response):
    debug_print("[cleanPayments] - got: "+ response)
    if response == None:
        return "no payments recorded yet"
    payList = eval(response)
    s = "num - date - value(nis)\n"
    for pay in payList:
        # p = ast.literal_eval(pay)
        s+=str(pay[0])+" - "+pay[1]+" - "+str(pay[2])+"\n"
    return s

def debug_print(txt):
    """debug printing active only when --debug is used"""
    if DEBUG:
        print('[DEBUG] - ', txt)

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

# class simpleState(state):
#     """docstring for simpleState"""
#     def __init__(self, arg):
#         super(simpleState, self).__init__()
#         self.arg = arg
#     def getOptions(self):
#         return list(self.dict)
#     def nextState(self,choice):
#         try:
#             r = self.dict[choice]
#         except KeyError as e:
#             debugPrint("wrong choice " + str(choice) + " in state " + self.id)
#             return None
#         return r
#     def act(self,arg):
#         return self.action(arg)

#**********************************************states**********************************************#

def STARTSTATE_POST(arg, text):
    print("[INFO] - started a new session")
    if text != "/start":
        print("[ERORR] - in func hello some thing went wrong, txt is", text)
        return ENDSTATE
    return FIRSTQSTATE
STARTSTATE = State(1, None, STARTSTATE_POST)
def FIRSTQSTATE_PRE(arg):
    return "usage:\n\
        balance [customer name] = see the balance of specific customer\n\
        payments [customer name] = see all the payments got from specific customer\n\
        classes [customer name] = see all the classes with price for specific customer\n\
        new class -s [student name] -d [day in yyyy-mm-dd format] -h [set which hour in day in hh-mm-ss format] -l [length in same format] = set new class, return class id\n\
        update class [id] = update the existance of class\n\
        new man = start sub menu for new customers and students\n\
        open classes = see which classes that should have been passed is open\n\
        day Schedule [day] = see full class Schedule for specific day\n\
            "
def FIRSTQSTATE_POST(arg, text):
    if text[:7] == "balance":
        arg["balance"] = text[8:]
        return BALANCESTATE
    elif text[:8] == "payments":
        arg["payments"] = text[9:]
        return PAYMENTSTATE
    elif text[:7] == "classes":
        arg["classes"] = text[8:]
        return CLASSESSTATE
    else:
        return ENDSTATE
FIRSTQSTATE = State(2, FIRSTQSTATE_PRE, FIRSTQSTATE_POST)

def BALANCESTATE_PRE(arg):
    return getBalaceByName(arg["balance"])+"\npress anything to continue"
def BALANCESTATE_POST(arg,txt):
    return LOOPSTATE
BALANCESTATE = State(3, BALANCESTATE_PRE, BALANCESTATE_POST)

def LOOPSTATE_PRE(arg):
    return "c = close connection \n\
            r = return to main menu"
def LOOPSTATE_POST(arg, txt):
    if txt == "c":
        return ENDSTATE
    elif txt == "r":
        return FIRSTQSTATE
    else:
        return LOOPSTATE
LOOPSTATE = State(4,LOOPSTATE_PRE, LOOPSTATE_POST)
def PAYMENTSTATE_PRE(arg):
    res = getPaymentsByName(arg["payments"])
    return cleanPayments(res)+"\npress anything to continue"

def PAYMENTSTATE_POST(arg, txt):
    return LOOPSTATE
PAYMENTSTATE = State(5, PAYMENTSTATE_PRE, PAYMENTSTATE_POST)

def CLASSESSTATE_PRE(arg):
    res = getClassesByName(arg["classes"])
    return cleanClasses(res)+"\npress anything to continue"

def CLASSESSTATE_POST(arg, txt):
    return LOOPSTATE
CLASSESSTATE = State(6, CLASSESSTATE_PRE, CLASSESSTATE_POST)

def close(arg):
    """f"""
    print("[INFO] - ended session")
    return None
ENDSTATE = State(4,close, None)

# def enough(arg):
#     """f"""
#     debug_print("sending?")
#     return "it is enough"
# def empty(arg, text):
#     """f"""
#     return SHOUTDOWNSTATE
# def hello(arg, text):
#     """f"""
#     if text != "/start":
#         print("[ERORR] - in func hello some thing went wrong")
#     return FIRSTQSTATE
# NEWUSERSTATE = State(2, None, hello)
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
        if v==-1:
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

#**************************************************************************************************#

#***********************************************main***********************************************#
if __name__ == '__main__':
    if '--debug' in sys.argv:
        print("[INFO] - debug mode")
        DEBUG = True
        print('Number of arguments:', len(sys.argv), 'arguments.')
        print('Argument List:', sys.argv)
    if "start" in sys.argv:
        print("[INFO] - starting the bot")
        BOT = Bot(TOKEN, URL)
        BOT.start()
    elif "test" in sys.argv:
        print("[INFO] - starting tests, the bot will shout down automaticlly after")
        unittest.main()
    else:
        print("[USAGE] Chat.py start/test [--debug]")
