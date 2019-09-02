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
import chatBotInfrastructure.state # local
#**************************************************************************************************#

TOKEN = "660462542:AAFGXJ3D8iYC3Sai8Grouysz2TIdya-9fL8" #get rid of this
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
DBA = "http://127.0.0.1:8080/" #why not config?

#*********************************************util*********************************************#
class datetime():
    """really stupid idea, i should find something better"""
    def __init__(self, arg):
        super(datetime, self).__init__()
        self.arg = arg
    def date(a,b,c):
        return str(c)+"\\"+str(b)+"\\"+str(a)
    def timedelta(a,b):
        return b/60

def Decimal(a):
    return float(a)

def updateClass(i):
    res = get_url(DBA+"""updateClass/?i={}&val=True""".format(i))
    # print(res)
    return res == "True"

def createNewClass(arg):
    """
    new class   -s [student name]
                -d [day in yyyy-mm-dd format]
                -h [set which hour in day in hh-mm-ss format]
                -l [length in same format]
                set new class, return class id
    """
    logging.debug("""newClass/?sname="{}"&day="{}"&hour="{}"&length="{}" """\
        .format(arg['s'], arg['d'], arg['h'], arg['l']))
    res = get_url(DBA+"""newClass/?sname=\""""+arg['s']+"\"&day=\""+arg['d']+"\"&hour=\""+arg['h']+"\"&length=\""+arg['l']+"\"")
    logging.debug(res)
    return res == "True"


def getClassesByName(name):
    """a database call to getCustomerClasses"""
    res = get_url(DBA+"""getCustomerClasses/?cname="""+name)
    if res == "":
        return None
    else:
        return res

def cleanClasses(response):
    """git dirty cllasses response and return it nice to show format"""
    logging.debug("got: {}".format(response))
    if response is None:
        return "no classes recorded yet"
    payList = eval(response)
    s = "num - date - length(min) - price(nis)\n"
    for pay in payList:
        # p = ast.literal_eval(pay)
        s += str(pay[0])+" - "+pay[1]+" - "+str(pay[3])+" - "+str(pay[4])+"\n"
    return s

def getBalaceByName(name):
    """a data base call to getCustomerBalance"""
    res = get_url(DBA+"""getCustomerBalance/?cname="""+name)
    if res == "":
        return None
    else:
        return res

def getPaymentsByName(name):
    """a database call to getCustomerTransactions"""
    res = get_url(DBA+"""getCustomerTransactions/?cname="""+name)
    if res == "":
        return None
    else:
        return res
def cleanPayments(response):
    logging.debug("got: {}".format(response))
    if response is None:
        return "no payments recorded yet"
    payList = eval(response)
    s = "num - date - value(nis)\n"
    for pay in payList:
        # p = ast.literal_eval(pay)
        s += str(pay[0])+" - "+pay[1]+" - "+str(pay[2])+"\n"
    return s
#**************************************************************************************************#

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
        new class --s [student name] --d [day in yyyy-mm-dd format] --h [set which hour in day in hh:mm:ss format] --l [length in same format] = set new class, return class id\n\
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
    elif text[:9] == "new class":
        arg["new class"] = text[10:]
        # arg = {**arg, **stripParameters(text[10:])}
        return NCLASSSTATE
    elif text[:12] == "update class":
        arg["update class"] = text[13:]
        return UCLASSSTATE
    elif text[:4]== "exit":
        exit()
    else:
        return ENDSTATE
FIRSTQSTATE = State(2, FIRSTQSTATE_PRE, FIRSTQSTATE_POST)

def BALANCESTATE_PRE(arg):
    return getBalaceByName(arg["balance"])+"\npress anything to continue"
def BALANCESTATE_POST(arg, txt):
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
LOOPSTATE = State(4, LOOPSTATE_PRE, LOOPSTATE_POST)
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

def NCLASSSTATE_PRE(arg):
    res = createNewClass(stripParameters(arg["new class"]))
    if res:
        return "done\npress any key to continue"
    else:
        return "somthing went wrong\npress any key to continue"
def NCLASSSTATE_POST(arg, txt):
    return LOOPSTATE

NCLASSSTATE = State(4, NCLASSSTATE_PRE, NCLASSSTATE_POST)

def UCLASSSTATE_PRE(arg):
    res = updateClass(arg["update class"])
    if res:
        return "done\npress any key to continue"
    else:
        return "somthing went wrong\npress any key to continue"
def UCLASSSTATE_POST(arg, txt):
    return LOOPSTATE

UCLASSSTATE = State(4, UCLASSSTATE_PRE, UCLASSSTATE_POST)

def close(arg):
    """f"""
    print("[INFO] - ended session")
    return None
ENDSTATE = State(4, close, None)