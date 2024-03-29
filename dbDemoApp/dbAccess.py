#!/usr/bin/python2.4
#
# Small script to show PostgreSQL and Pyscopg together
# TODO - fix string formatting so that rogue punctuation does not break any of the queries...
#
import os
import json
from flask import Flask
import psycopg2

app = Flask(__name__)

deviceId = os.getenv("DEVICE_ID")
port = os.getenv('VCAP_APP_PORT', '5000')

params = {
  'database': 'compose',
  'user': 'admin',
  'password': 'WZMJJZAEHMVMWHEQ',
  'host': 'haproxy525.aws-eu-west-1-portal.1.dblayer.com',
  'port': '10525'
}

dbAvailable=[]

def populateDbList():
    global dbAvailable
    try:
        conn = psycopg2.connect(** params)
        cursor = conn.cursor()
        cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
        for table in cursor.fetchall():
            dbAvailable.append(table)
        conn.commit() 
    except Exception as e:
        print "Error Populating DB list - %s" %(e)
    finally:
        conn.close()
        conn = None

@app.route('/new')
def createTableInPostGresDb(name="test"):
    global dbAvailable
    try:
        conn = psycopg2.connect(** params)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS %s" % (name))
        cursor.execute("CREATE TABLE %s (id serial PRIMARY KEY, num integer, data varchar);"%(name))
        cursor.execute("INSERT INTO %s (num, data) VALUES (%s, %s)" %(name, "%s", "%s") , (100, "abc'def"))
        dbAvailable.append(name)
        conn.commit() 
    except Exception as e:
        print "Error creating table - %s" %(e)
    finally:
        conn.close()
        conn = None
    return "Creating Table in DataBase"

@app.route('/del')
def destroyTableInPostGresDb(name='test'):
    global dbAvailable
    try:
        if len(dbAvailable) > 0 :
            conn = psycopg2.connect(** params)
            cursor = conn.cursor()
            for db in dbAvailable:
                cursor.execute("DROP TABLE IF EXISTS %s" % (name))
                #TODO - Clean up possible synchronisation issues
                dbAvailable.remove(db)
            conn.commit()
        else:
            return "No tables exist"
    except Exception as e:
        print "Error deleting tables - %s" %(e)
    finally:
        conn.close()
        conn = None
    return "DataBase Nuked"

@app.route('/add')
def EntryinDb(name='test'):
    global dbAvailable
    if len(dbAvailable) > 0:
        try:
            conn = psycopg2.connect(** params)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO %s (num, data) VALUES (%s, %s)" % (name, "%s", "%s"), (100, "abc'def"))
            conn.commit() 
        except Exception as e:
            print "Error adding Entry to Table - %s" %(e)
        finally:
            conn.close()
            conn = None
        return "Adding Entry to Table"
    else:
        return "No table available to insert Data into"

@app.route('/view')
def viewDb(name='test'):
    global dbAvailable
    tmp = None
    if len(dbAvailable) > 0:
    #if name in dbAvailable
        try:
            conn = psycopg2.connect(** params)
            cursor = conn.cursor()
            cursor.execute("SELECT * from %s" %(name))
            tmp = cursor.fetchall()
        except Exception as e:
            print "Error Viewing Table - %s" %(e)
        finally:
            conn.close()
            conn = None
        return "There are %s members in the array"% (len(tmp)) #requires jinja and some clever web stuff to return to the GUI, so for the moment return the size of array
    else:
        return "No Database available"

@app.route('/')
def hello():
    return 'Hello World! I am running on port ' + str(port) + '; Tables Present = ' + str(len(dbAvailable))+ ';'  
    
if __name__ == "__main__":  
    populateDbList()      
    app.run(host='0.0.0.0', port=int(port))