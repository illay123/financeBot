#!/usr/bin/env python3
"""this script creates a server that wrap the mysql database and provide
 four insert operations: creating new customer, create new student, register new class and add new transacion
 as well as get operations"""

__version__ = '0.2'
__author__ = 'E lie'

import sys
import re
import ast
import cherrypy
import mysql.connector

DEBUG = False

def debug_print(txt):
    """debug printing active only when --debug is used"""
    if DEBUG:
        print('[DEBUG] - ', txt)
def malicius_input(txt):
    # print(type(txt))
    if txt is None:
        return False
    """check if some potentially dangerous words are in the input"""
    bad_list = ['WHERE', 'DROP', 'SELECT', 'TABLE', 'NOT', 'INSERT', 'INTO', 'FROM']
    valids = re.sub(r"[^A-Za-z0-9]+", '', txt)
    for bad in bad_list:
        if bad in valids:
            return True
    return False

class Db(object):
    """object for database handling"""
    def __init__(self, dbName=None, host="localhost"):
        super(Db, self).__init__()
        self.host = host
        self.db_name = dbName
        self.cursor, self.data_base = self.create_connection()

    def create_connection(self):
        """creates connector object to the mySQL database"""
        if self.db_name != None:
            mydb = mysql.connector.connect(
                host=self.host,
                user="root",
                auth_plugin='mysql_native_password',
                passwd="ghkh12",
                database=self.db_name
                )
            print("[INFO] usersServer - Connected successfully to %s" % self.db_name)
        else:
            mydb = mysql.connector.connect(
                host=self.host,
                user="root",
                auth_plugin='mysql_native_password',
                passwd="ghkh12"
                )

        return mydb.cursor(buffered=True), mydb

    def close(self):
        """close the connection to the database
         and commit every uncommited ation"""
        self.data_base.commit()
        self.cursor.close()
        self.data_base.close()
        print('[INFO] - shuting down server conneion')

    def create_db(self, name):
        """create new database, used only for initaliztion"""
        command = "CREATE DATABASE "+name
        self.cursor.execute("SHOW DATABASES")
        if (name,) in self.cursor:
            print("[WARNING] usersServer - db %s already exist,\
             if you want to replace it you should drop it first" % name)
        try:
            self.cursor.execute(command)
        except Exception as e:
            print("[ERROR] - internal error during db creation: ", e)
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

            print('[INFO] - 4 tables have been created')
        except Exception as e:
            print ("[ERROR] - internal error during tables creation: ", e)
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
            return list(self.cursor)[0][0]
        else:
            print('[SECURITY] - possible injection attack in getIdFromCustomer:')
            print('getIdFromCustomer?name=%s', name)
            return "error"
        return 1

    def getIdFromStudent(self, name):
        """conver name to id (one to one)"""
        if not malicius_input(name):
            #  parameters.name | pvalues.val
            command = "SELECT sid FROM students\
             WHERE students.name = '"+name+"';"
            debug_print(command)
            self.cursor.execute(command)
            return list(self.cursor)[0][0]
        else:
            print('[SECURITY] - possible injection attack in getIdFromStudent:')
            print('getIdFromStudent?name=%s', name)
            return "error"
        return 1

    @cherrypy.expose
    def newCustomer(self, name, phone, price, address):
        """one of the four exposed methods"""
        if not malicius_input(name) and not malicius_input(price) and not malicius_input(phone) and not malicius_input(address):
            self.cursor.execute("INSERT INTO customers (price, balance, phone, name, address)\
             VALUES ({},{},{},{},{})".format(price, "0", phone, name, address))
            self.data_base.commit()
            return "True"
        else:
            return "False"

    @cherrypy.expose
    def newStudent(self, name, cname, phone, grade):
        """one of the four exposed methods"""
        if not malicius_input(name) and not malicius_input(cname) and not malicius_input(phone) and not malicius_input(grade):
            if phone is None:
                phone = "NULL"
            cid = self.getIdFromCustomer(cname)
            self.cursor.execute("INSERT INTO classes (name, cid, phone, grade)\
             VALUES ({},{},{},{})".format(name, cid, phone, grade))
            self.data_base.commit()
            return "True"
        else:
            return "False"

    @cherrypy.expose
    def newClass(self, sname, day, hour, length):
        """
        day format: "yyyy-mm-dd"
        hour\\length format: "hh:mm:ss"
        """
        if not malicius_input(sname) and not malicius_input(day) and not malicius_input(hour) and not malicius_input(length):
            sid = self.getIdFromStudent(sname)
            self.cursor.execute("INSERT INTO students (sid, day, hour, length)\
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
            print("%s",(da))
            self.cursor.execute("INSERT INTO transactions (cid, day, amount)\
             VALUES ({},{},{})".format(cid, str(da), amount))
            self.data_base.commit()
            return "True"
        else:
            return "False"

    @ cherrypy.expose
    def getUserBalance():
        pass
    # @cherrypy.expose
    # def updateUser(self, phone, arglist):
    #     """one of the four exposed methods"""
    #     command = "SELECT id FROM users WHERE phone= '"+re.sub("[^0-9]", "", phone)+"';"
    #     self.cursor.execute(command)
    #     debug_print(arglist)
    #     idnum = self.cursor.fetchone()
    #     # pdb.set_trace
    #     dic = ast.literal_eval(arglist) #should be safety checked
    #     # print (dic, idnum[0], type(idnum[0]))
    #     for param in list(dic):
    #         debug_print("inserting "+str(param)+str(idnum[0])+str(dic[param]))
    #         command = "INSERT INTO pvalues (pid, id, val) VALUES \
    #         (%s,%s,%s);"%(str(param), str(idnum[0]), str(dic[param]))
    #         debug_print(command)
    #         self.cursor.execute(command)
    #     self.data_base.commit()
    #     return "True"

    # @cherrypy.expose
    # def getUser(self, phone):
    #     """one of the four exposed methods"""
    #     if not malicius_input(phone):
    #         #  parameters.name | pvalues.val
    #         command = "SELECT parameters.name,pvalues.val FROM users\
    #          INNER JOIN pvalues on users.id = pvalues.id\
    #          INNER JOIN parameters on pvalues.pid = parameters.pid\
    #          WHERE users.phone= '"+re.sub("[^0-9]", "", phone)+"';"
    #         debug_print(command)
    #         self.cursor.execute(command)
    #         lis = list(self.cursor)
    #         # self.cursor.execute("SELECT val FROM")
    #         return str(lis)
    #     else:
    #         print('[SECURITY] - possible injection attack in getUser:')
    #         print('getUser?phone=%s', phone)
    #         return "error"

    @cherrypy.expose
    def getScheme(self):
        """one of the four exposed methods"""
        self.cursor.execute("SELECT * FROM classes")
        return str(list(self.cursor))

# class HelloWorld(object):
#     @cherrypy.expose
#     def index(self, num = 8):
#         return "new user" + str(int(num)*2)

if __name__ == '__main__':
    # config = {'server.socket_host': '0.0.0.0'}
    # cherrypy.config.update(config)
    if '--debug' in sys.argv:
        print("[INFO] - debug mode")
        DEBUG = True
        print('Number of arguments:', len(sys.argv), 'arguments.')
        print('Argument List:', sys.argv)
    if 'init' in sys.argv:
        good = True
        print('[INFO] - start initialyzing the finance server')
        MDB = Db(host="localhost")
        good = MDB.create_db("finance") and good
        MDB.cursor.execute("USE finance")
        good = MDB.create_tables() and good
        if '--test' in sys.argv:
            print('[TEST] - start testing initialization')
            MDB.init_test()
            print('[TEST] - done')
        if good:
            print('[INFO] finished initialization successfully')
        else:
            print("[INFO] some errors detected during the initialization process,\
             check the log for more information")
        MDB.close()


    elif 'start' in sys.argv:
        print('[INFO] - starting the server')
        MDB = Db(dbName="finance", host="localhost")
        cherrypy.quickstart(MDB)
    elif 'test' in sys.argv:
        print('[INFO] - starting the test')
        MDB = Db(dbName="finance", host="localhost")
        MDB.newStudent("yali", "ori", "0587788008", "7")
    else:
        print("[USAGE] users-server.py init/start/test [--debug]")
