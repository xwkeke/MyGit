from socket import *
import struct
import cs_pb2

cs_ip = '114.215.173.62'
#cs_ip = '172.10.0.2'
cs_port = 3521
obj_tcp = 0
obj_udp = 0

msg_g = 0
def inintal_media():
    global obj_tcp
    global obj_udp
    global msg_g
    obj_tcp = socket()
    try:
        obj_tcp.connect((cs_ip,cs_port))
        obj_tcp.settimeout(10)

        obj_udp = socket(AF_INET, SOCK_DGRAM)
        obj_udp.settimeout(10)
        msg_g = cs_pb2.Message()
    except Exception,ex:
        print "socket connect error"

 

def checkmedia_tcp(DevID):
    global obj_tcp
    sendmsg = creat_msg(DevID)
    msgdata = sendmsg.SerializeToString()
    head = struct.pack("HHHH", 0x3004 + len(msgdata), 0x3004, len(msgdata), 0)
    try:
        obj_tcp.sendall((head + msgdata))  
        revmsg = revdata_tcp(obj_tcp)
        if (revmsg.errorcode <> 0):
            print hex(revmsg.errorcode)
            return 0
        print 'TCP:vtduip',revmsg.response.realstream.vtduip,'port',revmsg.response.realstream.vtduport
        return 1
    except Exception,ex:
        print "tcp socket error:",Exception,':',ex

    try:
        obj_tcp = socket()
        obj_tcp.connect((cs_ip,cs_port))
        obj_tcp.settimeout(3)
    except Exception,ex:
        print "tcp socket error:",Exception,':',ex
    return 0


def checkmedia_udp(DevID):
    global obj_udp
    sendmsg = creat_msg(DevID)
    msgdata = sendmsg.SerializeToString()
    head = struct.pack("HHHH", 0x3004 + len(msgdata), 0x3004, len(msgdata), 0)
    try:
        obj_udp.sendto(head + msgdata,(cs_ip,cs_port)); 
        revmsg = revdata_udp(obj_udp)
        if (revmsg.errorcode <> 0):
            print hex(revmsg.errorcode)
            return 0
        print 'UDP:vtduip',revmsg.response.realstream.vtduip,'port',revmsg.response.realstream.vtduport
    except Exception,ex:
        print "udp socket error:",Exception,':',ex
    return 1

def revdata_tcp(obj):
    rev_size  = check_recv_head(obj)
    msg = check_recv_msg(obj,rev_size)
    return msg;

def revdata_udp(obj):
    data,addr = obj.recvfrom(128)
    crc, cmd, length, extend = struct.unpack("HHHH", data[0:8])
    msg = cs_pb2.Message()
    msg.ParseFromString(data[0 - length:])
    return msg;

def creat_msg(DevID):
    #DevID = '0002016123540158564234567_1'
    global msg_g
    msg_g.errorcode = 0
    msg_g.msgtype = cs_pb2.REALSTREAM_REQ
    msg_g.timeoutmillisec = 3000
    try:
        msg_g.request.realstream.deviceid = long(DevID[0:DevID.find('_')])
    except Exception,ex:
        msg_g.request.realstream.deviceid = long(DevID[0:10])
    #msg.request.realstream.deviceid = 16777216123291398
    msg_g.request.realstream.channel = int(DevID[DevID.find('_')-len(DevID)+1:])
    msg_g.request.realstream.resolution = 2
    msg_g.request.realstream.checkdeviceopen = 1
    return msg_g

def check_recv_head(s):
    data = s.recv(8)
    if (len(data) != 8):
        print "recv head error"
        return 0
    crc, cmd, length, extend = struct.unpack("HHHH", data)
    if (length > 0):
        pass
    else:
        print "recv head error"
    return length

def check_recv_msg(s, length):
    data = s.recv(length)
    if (len(data) != length):
        print "recv head error"
        return 0
    msg = cs_pb2.Message()
    msg.ParseFromString(data)
    return msg;