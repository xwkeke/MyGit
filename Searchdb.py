import commands
import struct
import time
import string
import thread
import redis
import MySQLdb


redis_host = '112.124.124.247'
redis_port = 6379
redis_db = 0
redis_pwd = 'TG20151216CS3521REDIS'
dbhost = '114.215.173.62'
dbuser = 'tg_admin'
#dbpassword = '123456'
#dbdatabase = 'guardon_19_20170314'
dbpassword = 'Qsc321admin'
dbdatabase = 'guardon'
dbport = 3306

devs_type = [2,4,6]
global dbconn
dbconn = 0
global cur
cur = 0
global r
r = 0

def inintal_db():
    global dbconn
    global cur
    global r
    dbconn = MySQLdb.connect(dbhost, dbuser, dbpassword, dbdatabase, dbport, charset='utf8')
    cur = dbconn.cursor()
    r = redis.Redis(redis_host, redis_port, redis_db, redis_pwd)

def end_db():
    global dbconn
    global cur
    cur.close()
    dbconn.commit()
    dbconn.close()


def getusernamebytype():
    username = []
    sql_str = u'SELECT accountinfo.acc_name FROM accountinfo JOIN account_details ON accountinfo.id = account_details.acc_id WHERE account_details.acc_type = 2'
    global cur
    cur.execute(sql_str)
    rows = cur.fetchall()
    for row in rows:
        username.append(row[0])
    return username


def GetDevbyUserName(UserName):
    data=[]
    sql_str = u'SELECT deviceinfo.id,deviceinfo.device_name,deviceinfo.device_type,deviceinfo.device_nodeid,deviceinfo.icloud_switch,\
    deviceinfo.lastonlinetime FROM accountinfo JOIN account_bind_device ON accountinfo.id = account_bind_device.account_id \
    JOIN deviceinfo ON account_bind_device.device_id = deviceinfo.id WHERE accountinfo.acc_name = \'' + UserName + '\''
    global cur
    cur.execute(sql_str)
    rows = cur.fetchall()
    for row in rows:
        if row[2] in devs_type:
            sql_str = u'SELECT deviceinfo.id,deviceinfo.device_name,deviceinfo.device_type,deviceinfo.device_nodeid,deviceinfo.icloud_switch,\
    deviceinfo.lastonlinetime FROM deviceinfo where device_nodeid like \'%s%%\''%row[3][:-1]
            cur.execute(sql_str)
            rows_2 = cur.fetchall()
            for row_2 in rows_2:
                data.append(row_2)
        else:
            data.append(row)
    return data

def CheckDevStatus(DevID):
    global r
    devid = DevID[0:DevID.find('_')+1].zfill(25)
    chanid= DevID[DevID.find('_')-len(DevID)+1:].zfill(3)
    dwde = DevID.find('ddd')
    key = '%s%s_1'%(devid,chanid)
    print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),'search:',key
    try:
        val = r.get(key)
        if val.find(r'"state":1')<>-1:
            return 1
        else:
            return 0
    except Exception,ex:
            pass
            print 'not find num'
            return 0

def CheckDevPlaystate(DevID):
    key = 'vtdustream_'+ DevID + '_2'
    try:
        val = r.get(key)
        if val:
            return 1
        else:
            return 0
    except Exception,ex:
        print 'not find  num'
        return 0


