import sys
import os
import subprocess
import optparse
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

class User:
    def __init__(self, elements):
        self.userID = elements[0]
        self.networkID = elements[1]
        self.accountType = elements[2]
        self.status = elements[3]
        self.dateCreated = elements[4]

def getUsers(dbuser,passwd,db,host):
    try:
        connection = mysql.connector.connect(host=host,database=db, user=dbuser, password=passwd)
        cursor = connection.cursor(prepared=True)
        query = 'select userID, networkID, accountType, status, dateCreated from user where status="active" and accountType != "%s"' % (SUPER_USER)
        cursor.execute(query)
        users = [];
        for row in cursor:
            user = User([el.decode('utf-8') if type(el) is bytearray else el for el in row])
            users.append(user)
        return users

    except mysql.connector.Error as error :
        print("Failed to update record to database:{}".format(error))
        connection.rollback()

    finally:
        if(connection.is_connected()):
            connection.close()

def isExpire(networkID,accountType,dateCreated):

    accountMonths = int(accountType.replace("hmvv",""))
    difference = datetime.now() - datetime.strptime(str(dateCreated), '%Y-%m-%d %H:%M:%S')
    print("--> %s is active for %s days " % (networkID,difference.days))
    monthsPassed = int(difference.days/30)
    if accountMonths > monthsPassed :
        return False
    else:
        return True

def updateExpiredUserStatus(networkID,dbuser,passwd,db,host):
    try:
        connection = mysql.connector.connect(host=host,database=db, user=dbuser, password=passwd)
        cursor = connection.cursor(prepared=True)
        query = "update user set status='inactive' where networkID = %s "
        cursor.execute(query,(networkID,))
        connection.commit()

    except mysql.connector.Error as error :
        print("Failed to update record to database:{}".format(error))
        connection.rollback()

    finally:
        if(connection.is_connected()):
            connection.close()

def deleteExpiredUser(networkID):
    ### cmd = "sudo rm -rf /home/" + networkID
    ### bashCommunicator(cmd)
    cmd = "sudo userdel " + networkID
    bashCommunicator(cmd)

def bashCommunicator(command,output_expected=False):
    process = subprocess.Popen([command],shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("Process failed %s %d %s %s" % (command,process.returncode, stdout, stderr))
    else:
        if output_expected:
            return [x for x in stdout.split("\n")]

def controlAccount(dbuser,passwd,db,host):

    users=getUsers(dbuser,passwd,db,host)

    if len(users)>0:
        print("processing user accounts...")
        for u in users:
            print("Evaluating userID: %s, accountType: %s, dateCreated: %s " % (u.networkID, u.accountType,u.dateCreated))
            if (u.accountType != SUPER_USER):
                if (isExpire(u.networkID,u.accountType,u.dateCreated)):
                    print("--> Deactivating userID: %s, accountType: %s, dateCreated: %s " % (u.networkID, u.accountType,u.dateCreated))
                    deleteExpiredUser(u.networkID)
                    updateExpiredUserStatus(u.networkID,dbuser,passwd,db,host)
                else:
                    print("--> %s does not qualify for deactivation." % (u.networkID) )

    else:
        print("No user account found for deactivation.")

try:
    parser = optparse.OptionParser()
    parser.add_option('-u', '--user', help = ' input user to connect to database')
    parser.add_option('-p', '--password', help = ' input user password to connect to database')
    parser.add_option('-d', '--database', help = ' input database')
    parser.add_option('-b', '--dbhost', help = ' input database host')
    options,args = parser.parse_args()
    dbuser = options.user
    passwd = options.password
    db = options.database
    host = options.dbhost

    SUPER_USER="hmvv999"

    controlAccount(dbuser,passwd,db,host)

except TypeError:
	print ("python account_control.py -help for help")
