#!/usr/bin/env python3
"""this script creates a server that wrap the mysql database and provide
    four insert operations: creating new customer, create new student,
    register new class and add new transacion.
    as well as get operations"""

__version__ = '0.2'
__author__ = 'E lie'
#*********************************************imports*********************************************#
import sys
import re
import ast
import json
import argparse
import logging
import cherrypy
import mysql.connector
#***********************************************util***********************************************#
def malicius_input(txt):
    """check if the input include chars that could be used to attack the system"""
    # print(type(txt))
    if txt is None:
        return False
    bad_list = ['WHERE', 'DROP', 'SELECT', 'TABLE', 'NOT', 'INSERT', 'INTO', 'FROM']
    valids = re.sub(r"[^A-Za-z0-9]+", '', txt)
    for bad in bad_list:
        if bad in valids:
            return True
    return False
#*********************************************database*********************************************#
class Db():
    """object for database handling"""
    def __init__(self, config, dbName=None):
        super(Db, self).__init__()
        self.host = config["host"]
        self.db_name = dbName
        self.port = config["port"]
        self.passwd = config["password"]
        self.user = config["user"]
        self.cursor, self.data_base = self.create_connection()

    def create_connection(self):
        """creates connector object to the mySQL database"""
        if self.db_name is not None:
            mydb = mysql.connector.connect(
                host=self.host,
                user=self.user,
                auth_plugin='mysql_native_password',
                passwd=self.passwd,
                database=self.db_name,
                port=self.port
                )
            logging.info("Connected successfully to {}".format(self.db_name))
        else:
            mydb = mysql.connector.connect(
                host=self.host,
                user=self.user,
                auth_plugin='mysql_native_password',
                passwd=self.passwd,
                port=self.port
                )

        return mydb.cursor(buffered=True), mydb

    def close(self):
        """close the connection to the database
         and commit every uncommited ation"""
        self.data_base.commit()
        self.cursor.close()
        self.data_base.close()
        logging.info('shuting down server conneion')

    def create_db(self, name):
        """create new database, used only for initaliztion"""
        command = "CREATE DATABASE "+name
        self.cursor.execute("SHOW DATABASES")
        if (name,) in self.cursor:
            logging.warning("usersServer - db {} already exist,\
             if you want to replace it you should drop it first".format(name))
        try:
            self.cursor.execute(command)
        except Exception as e:
            logging.error("internal error during db creation: {}".format(e))
            return False
        return True

    def show_db(self):
        """show db list in the server, used only for the tests"""
        self.cursor.execute("SHOW DATABASES")
        lis = list(self.cursor)
        print(("users",) in lis)
        for name in lis:
            print(name)
        return lis

    # used for the database initialization
    def create_tables(self):
        """create the new tables in the database during initalization"""
        try:
            self.cursor.execute("CREATE TABLE customers\
                 (cid INT AUTO_INCREMENT PRIMARY KEY,\
                 price INT,\
                 balance INT,\
                 phone VARCHAR(255) NOT NULL UNIQUE,\
                 name VARCHAR(255),\
                 address VARCHAR(255))")
            self.cursor.execute("CREATE TABLE students\
                 (cid INT,\
                 sid INT AUTO_INCREMENT PRIMARY KEY,\
                 name VARCHAR(255) NOT NULL UNIQUE,\
                 phone VARCHAR(255),\
                 grade INT,\
                 FOREIGN KEY (cid) REFERENCES customers(cid))")
            self.cursor.execute("CREATE TABLE classes\
                 (id INT AUTO_INCREMENT PRIMARY KEY,\
                 sid INT , day DATE,hour TIME, length TIME, happend BOOLEAN,\
                 FOREIGN KEY (sid) REFERENCES students(sid))")
            self.cursor.execute("CREATE TABLE transactions\
                 (tid INT AUTO_INCREMENT PRIMARY KEY,\
                  cid INT, day DATE,amount INT,\
                 FOREIGN KEY (cid) REFERENCES customers(cid))")

            logging.info('4 tables have been created')
        except Exception as e:
            logging.error("internal error during tables creation: {}".format(e))
            return False
        return True

    def init_test(self):
        """still empty - should check the init process"""
        pass
    # very unsafe
    def injection(self, command):
        """dont ever use it"""
        print("[WARNING] - using direct typing of queries, considerd unsafe,\
            \n could be potention voulnerability")
        self.cursor.execute(command)

    def getIdFromCustomer(self, name):
        """conver name to id (one to one)"""
        if not malicius_input(name):
            #  parameters.name | pvalues.val
            command = "SELECT cid FROM customers\
             WHERE customers.name = '"+name+"';"
            debug_print(command)
            self.cursor.execute(command)
            lis = list(self.cursor)
            if lis == []:
                logging.warning("getIdFromCustomer for unknown name: {}".format(name))
                return -1
            return lis[0][0]
        else:
            logging.warning('[SECURITY] - possible injection attack in getIdFromCustomer:\n\
                getIdFromCustomer?name={}'.format(name))
            return -1

    def getIdFromStudent(self, name):
        """conver name to id (one to one)"""
        if not malicius_input(name):
            #  parameters.name | pvalues.val
            command = "SELECT sid FROM students\
             WHERE students.name = '"+name+"';"
            debug_print(command)
            self.cursor.execute(command)
            lis = list(self.cursor)
            if lis == []:
                logging.warning("getIdFromCustomer for unknown name: ".format(name))
                return -1
            return lis[0][0]
        else:
            logging.warning('[SECURITY] - possible injection attack in getIdFromStudent:\n\
            getIdFromStudent?name=%s', name)
            return -1

    @cherrypy.expose
    def newCustomer(self, name, phone, price, address):
        """one of the four exposed methods"""
        if not malicius_input(name)\
            and not malicius_input(price)\
            and not malicius_input(phone)\
            and not malicius_input(address):
            self.cursor.execute("INSERT INTO customers (price, balance, phone, name, address)\
             VALUES ({},{},{},{},{})".format(price, "0", phone, name, address))
            self.data_base.commit()
            return "True"
        else:
            return "False"

    @cherrypy.expose
    def newStudent(self, name, cname, phone, grade):
        """one of the four exposed methods"""
        if not malicius_input(name)\
            and not malicius_input(cname)\
            and not malicius_input(phone)\
            and not malicius_input(grade):
            if phone is None:
                phone = "NULL"
            cid = self.getIdFromCustomer(cname)
            # print("INSERT INTO classes (name, cid, phone, grade)\
            # VALUES ({},{},{},{})".format(name, cid, phone, grade))
            self.cursor.execute("INSERT INTO students (name, cid, phone, grade)\
             VALUES ({},{},{},{})".format(name, cid, phone, grade))
            self.data_base.commit()
            return "True"
        else:
            return "False"

    @cherrypy.expose
    def newClass(self, sname, day, hour, length):
        """
        day format: "yyyy-mm-dd"
        hour/length format: "hh:mm:ss"
        """
        if not malicius_input(sname)\
            and not malicius_input(day)\
            and not malicius_input(hour)\
            and not malicius_input(length):
            sid = self.getIdFromStudent(sname[1:-1])
            self.cursor.execute("INSERT INTO classes (sid, day, hour, length)\
             VALUES ({},{},{},{})".format(sid, str(day), str(hour), str(length)))
            self.data_base.commit()
            return "True"
        else:
            return "False"

    @cherrypy.expose
    def newTransaction(self, cname, da, amount):
        """
        day format: "yyyy-mm-dd"
        hour\\length format: "hh:mm:ss"
        """
        # print("************************",cname,da,amount)
        if not malicius_input(cname) and not malicius_input(da) and not malicius_input(amount):
            cid = self.getIdFromCustomer(cname)
            print("{}".format(da))
            self.cursor.execute("INSERT INTO transactions (cid, day, amount)\
             VALUES ({},{},{})".format(cid, str(da), amount))
            self.data_base.commit()
            return "True"
        else:
            return "False"

    @cherrypy.expose
    def updateClass(self, i, val):
        """update for class if it did exist"""
        # print
        command = "UPDATE classes SET happend = {}\
                    WHERE id = {}".format(val, i)
        self.cursor.execute(command)
        self.data_base.commit()
        return "True"

    @cherrypy.expose
    def getCustomerClasses(self, cname):
        # cid = self.getIdFromCustomer(cname)
        command = "SELECT classes.id,classes.day,classes.hour,classes.length,\
                    TIME_TO_SEC(classes.length)/3600*customers.price\
                    FROM classes INNER JOIN students on classes.sid = students.sid \
                    INNER JOIN customers on customers.cid = students.cid \
                    WHERE customers.name = \"{}\"\
                    ORDER BY classes.id desc".format(cname)
        self.cursor.execute(command)
        lis = list(self.cursor)
        if lis == []:
            print("[WARNING] - getCustomerClasses for customer without transactions\
                (might be unknown customer name, check warning above)")
            return ""
        else:
            return str(lis)

    @cherrypy.expose
    def getCustomerTransactions(self, cname):
        cid = self.getIdFromCustomer(cname)
        command = "SELECT transactions.tid,transactions.day, transactions.amount\
                    FROM transactions WHERE cid = {}".format(cid)
        self.cursor.execute(command)
        lis = list(self.cursor)
        if lis == []:
            print("[WARNING] - getCustomerTransactions for customer without transactions\
                (might be unknown customer name, check warning above)")
            return ""
        else:
            return str(lis)

    @ cherrypy.expose
    def getCustomerBalance(self, cname):
        command = "SELECT balance FROM customers WHERE name = \"{}\"".format(cname)
        # print(command)
        self.updateCustomerBalance(cname)
        self.cursor.execute(command)
        lis = list(self.cursor)
        if lis == []:
            print("[WARNING] - getCustomerBalance for unknown customer")
            return ""
        else:
            return str(lis[0][0])

    def sumCustomerTransactions(self, cname):
        # cid = self.getIdFromCustomer(cname)
        command = "SELECT SUM(transactions.amount) \
                    FROM transactions \
                    INNER JOIN customers on transactions.cid = customers.cid \
                    WHERE customers.name = \"{}\"".format(cname)
        self.cursor.execute(command)
        lis = list(self.cursor)
        if lis == []:
            print("[WARNING] - sumCustomerTransactions for customer without transactions\
                (might be unknown customer name, check warning above)")
            return ""
        else:
            return lis[0][0]
    def sumCustomerClasses(self, cname):
        command = "SELECT SUM(TIME_TO_SEC(classes.length)/3600*customers.price)\
                    FROM classes INNER JOIN students ON classes.sid = students.sid \
                    INNER JOIN customers ON customers.cid = students.cid \
                    WHERE customers.name = \"{}\" AND classes.happend = TRUE".format(cname)
        self.cursor.execute(command)
        lis = list(self.cursor)
        if lis == []:
            print("[WARNING] - sumCustomerClasses for customer without transactions\
                (might be unknown customer name, check warning above)")
            return ""
        else:
            return lis[0][0]

    def updateCustomerBalance(self, name):
        p = self.sumCustomerClasses(name)
        m = self.sumCustomerTransactions(name)
        if p is None:
            p = 0
        if m is None:
            m = 0
        new = p-m
        command = "UPDATE customers SET balance = {}\
                    WHERE name = \"{}\"".format(new, name)
        self.cursor.execute(command)
        self.data_base.commit()

    @cherrypy.expose
    def getScheme(self):
        """one of the four exposed methods"""
        self.cursor.execute("SELECT * FROM classes")
        return str(list(self.cursor))

#***********************************************test***********************************************#
class TestMethods(unittest.TestCase):
    """test for the non class functions"""
    def test_malicius_input(self):
        """just a test..."""
        self.assertTrue(malicius_input("DROP TABLE user;"))
        self.assertFalse(malicius_input("illay"))

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
#***********************************************main***********************************************#


def parseJson(fPath):
    if fPath is None:
        logging.info("no .config file found, starting with default")
    else:
        try:
            with open(fPath, 'r') as content_file:
                content = content_file.read()
                return json.loads(content)
        except FileNotFoundError as e:
            logging.error('parseJson: can not open file {}'.format(fPath))
            try:
                with open(""" C:\\Users\\Illay\\Desktop\\summer app\\configurations\\default.config """, 'r') as content_file:
                    content = content_file.read()
                    return json.loads(content)
            except FileNotFoundError as e:
                logging.error('parseJson: can find default.config'.format(fPath))

    return {"host":"localhost", "port":3306} #the basic default

def setPaser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-D", "--dev", help="using or setting the development database",
                    action="store_true")
    parser.add_argument("-d", "--debug", help="show debugging data when running",
                    action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")
    parser.add_argument("mode", help="operation mode of the server", 
                    choices=["start", "test", "init"])
    parser.add_argument("-c","--config",help="path to .config file, can be done by dragging")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    # config = {'server.socket_host': '0.0.0.0'}
    # cherrypy.config.update(config)
    serverMode = config["dbName"]
    args = setPaser()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(args)
        logging.info("debug mode")
        DEBUG = True
        logging.debug('Number of arguments: {} arguments'.format(len(sys.argv)))
        logging.debug('Argument List: {}'.format(sys.argv))

    config = parseJson(args.config)

    if args.dev:
        logging.info('operating in dev mode\n\
        same but with dev data so no debug in prod ;)')
        serverMode = config["devDbName"]

    if args.mode == 'init':
        good = True
        logging.info('start initialyzing the {} server'.format(serverMode))
        MDB = Db(config)
        good = MDB.create_db(serverMode) and good
        MDB.cursor.execute("USE {}".format(serverMode))
        good = MDB.create_tables() and good
        if good:
            logging.info('finished initialization successfully')
        else:
            logging.info("some errors detected during the initialization process,\
             check the log for more information")
        MDB.close()


    elif args.mode == 'start':
        logging.info('starting the server')
        MDB = Db(config, dbName=serverMode)
        cherrypy.quickstart(MDB)
    elif args.mode == 'test':
        logging.info('starting the test')
        MDB = Db(config, dbName=serverMode)
        # MDB.newStudent("yali", "ori", "0587788008", "7")
        # print(MDB.sumCustomerClasses("ori"))
        MDB.updateCustomerBalance("ori")
    