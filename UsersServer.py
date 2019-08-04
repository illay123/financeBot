#!/usr/bin/env python3
"""this script creates a server that wrap the mysql database and provide
 four operations on it creating new user, updating paramaters for users,
 get information previously inserted about user and get list of parameters each user can hold"""

__version__ = '0.1'
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
    """check if some potentially dangerous words are in the input"""
    bad_list = ['WHERE', 'DROP', 'SELECT', 'TABLE', 'NOT', 'INSERT', 'INTO', 'FROM']
    valids = re.sub(r"[^A-Za-z]+", '', txt)
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
        self.cursor.execute(command)

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
        self.cursor.execute("CREATE TABLE users\
             (id INT AUTO_INCREMENT PRIMARY KEY,\
             phone VARCHAR(255) NOT NULL UNIQUE,\
             name VARCHAR(255), birthday DATE)")
        self.cursor.execute("CREATE TABLE parameters\
         (pid INT AUTO_INCREMENT PRIMARY KEY,\
         name VARCHAR(255) NOT NULL UNIQUE,\
         dict VARCHAR(255))")
        self.cursor.execute("CREATE TABLE pvalues\
         (pid INT , id INT, val INT,\
         FOREIGN KEY (pid) REFERENCES parameters(pid),\
         FOREIGN KEY (id) REFERENCES users(id))")
        print('[INFO] - 3 tables have been created')

    def init_test(self):
        """still empty - should check the init process"""
        pass
    # very unsafe
    def injection(self, command):
        """dont ever use it"""
        print("[WARNING] - using direct typing of queries, considerd unsafe,\
            \n could be potention voulnerability")
        self.cursor.execute(command)

    @cherrypy.expose
    def newUser(self, name, phone, birthday):
        """one of the four exposed methods"""
        if not malicius_input(name) and not malicius_input(birthday):
            self.cursor.execute("INSERT INTO users (phone,name,birthday)\
             VALUES (%s, %s, %s)", (phone, name, birthday))
            self.data_base.commit()
            return "True"
        else:
            return "False"

    @cherrypy.expose
    def updateUser(self, phone, arglist):
        """one of the four exposed methods"""
        command = "SELECT id FROM users WHERE phone= '"+re.sub("[^0-9]", "", phone)+"';"
        self.cursor.execute(command)
        debug_print(arglist)
        idnum = self.cursor.fetchone()
        # pdb.set_trace
        dic = ast.literal_eval(arglist) #should be safety checked
        # print (dic, idnum[0], type(idnum[0]))
        for param in list(dic):
            debug_print("inserting "+str(param)+str(idnum[0])+str(dic[param]))
            command = "INSERT INTO pvalues (pid, id, val) VALUES \
            (%s,%s,%s);"%(str(param), str(idnum[0]), str(dic[param]))
            debug_print(command)
            self.cursor.execute(command)
        self.data_base.commit()
        return "True"

    @cherrypy.expose
    def getUser(self, phone):
        """one of the four exposed methods"""
        if not malicius_input(phone):
            #  parameters.name | pvalues.val
            command = "SELECT parameters.name,pvalues.val FROM users\
             INNER JOIN pvalues on users.id = pvalues.id\
             INNER JOIN parameters on pvalues.pid = parameters.pid\
             WHERE users.phone= '"+re.sub("[^0-9]", "", phone)+"';"
            debug_print(command)
            self.cursor.execute(command)
            lis = list(self.cursor)
            # self.cursor.execute("SELECT val FROM")
            return str(lis)
        else:
            print('[SECURITY] - possible injection attack in getUser:')
            print('getUser?phone=%s', phone)
            return "error"

    @cherrypy.expose
    def getScheme(self):
        """one of the four exposed methods"""
        self.cursor.execute("SELECT * FROM parameters")
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
        print('[INFO] - start initialyzing the users server')
        MDB = Db(host="localhost")
        MDB.create_db("users")
        MDB.cursor.execute("USE users")
        MDB.create_tables()
        if '--test' in sys.argv:
            print('[TEST] - start testing initialization')
            MDB.init_test()
            print('[TEST] - done')
        print('[INFO] finished initialization successfully')
        MDB.close()


    elif 'start' in sys.argv:
        print('[INFO] - starting the server')
        MDB = Db(dbName="users", host="localhost")
        cherrypy.quickstart(MDB)
    elif 'test' in sys.argv:
        MDB = Db(dbName="users", host="localhost")
        MDB.cursor.execute("INSERT INTO pvalues (pid, id, val) VALUES (2,2,1);")
        MDB.data_base.commit()
    else:
        print("[USAGE] users-server.py init/start/test [--debug]")

    # print (mdb.db, mdb.cursor)
