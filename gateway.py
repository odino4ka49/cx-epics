#!/usr/bin/env python
#!/bin/sh -

import cothread.catools as catools
import cothread
from cothread.catools import *
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from PyQt4 import QtCore
import pycx4.qcda as cda
import json
import time
import sys
import os

import logging

class PvCxChan:
    def __init__(self,chan,channame,pv,flags,datatype=None):
        self.chan = chan
        self.channame = channame
        self.pv = pv
        self.flags = flags
        self.datatype = datatype

class Server:
    def __init__(self,type,name,timestamp=None):
        self.type = type
        self.name = name
        self.timestamp = timestamp
    def delay_server(self):
        self.timestamp = time.time()
    def check_server(self):
        if not self.timestamp:
            return True
        if time.time()-self.timestamp>10:
            return True
        return False

def find_server(type,name):
    global servers
    return [x for x in servers if x.type == type and x.name == name][0]

def is_channel_work_delayed(channel):
    server = find_server("ioc",channel.pv.split(":",1)[0])
    if not server.check_server():
        return True
    server = find_server("cx",channel.channame.split(".",1)[0])
    if not server.check_server():
        return True
    return False

def set_server_delay(error):
    channelname = error.split(' ',1)[0]
    servername = channelname.split(":",1)[0]
    server = find_server("ioc",servername)
    if not server:
        servername = channelname.split(".",1)[0]
        server = find_server("cx",servername)
    if server:
        server.delay_server()
        return

def open_config_file(filename):
    with open(filename) as data_file:
        data = json.load(data_file)
    return data

def unicode_to_str(name):
    string = name.encode('ascii', 'ignore')
    return string

def printval(chan):
    print("cx "+str(chan.val))

def print_data(value):
    logging.info("pv "+str(value))

#one time copying of data from pv to cx channel
def set_pv_to_cx(channel):
    pv = channel.pv
    chan = channel.chan
    def updateChan():
        try:
            if is_channel_work_delayed(channel):
                return
            if channel.datatype!="str":
                pv_val = float(caget(pv))
            else:
                pv_val=str(caget(pv,datatype=DBR_STRING))
            if pv_val!=chan.val:
                chan.setValue(pv_val)
        except Exception as e:
            logging.info("Trouble in set_pv_to_cx_update with "+ str(e))
            set_server_delay(str(e))
    try:
        connect(pv)
        updateChan()
    except Exception as e:
            logging.info("Trouble in set_pv_to_cx with "+ str(e))

#one time copying of data from cx to pv channel
def set_cx_to_pv(channel):
    pv = channel.pv
    chan = channel.chan
    def updatePv(chan):
        try:
            if is_channel_work_delayed(channel):
                return
            if channel.datatype!="str":
                pv_val = float(caget(pv))
            else:
                pv_val=str(caget(pv,datatype=DBR_STRING))
            if pv_val!=chan.val:
                caput(pv,chan.val)
        except Exception as e:
            logging.info("Trouble in set_cx_to_pv_update with "+ str(e))
            set_server_delay(str(e))
    try:
        chan.valueMeasured.connect(updatePv)
    except Exception as e:
        logging.info("Trouble in set_cx_to_pv with "+ str(e))

#monitoring of changes in cx: if changed, copy information from pv again
def monit_pv_to_cx(channel):
    pv = channel.pv
    chan = channel.chan
    def updateChan():
        #print "cx was changed"+pv
        try:
            if is_channel_work_delayed(channel):
                return
            if channel.datatype!="str":
                pv_val = float(caget(pv))
            else:
                pv_val=str(caget(pv,datatype=DBR_STRING))
            if pv_val==None:
                return
            if chan.val!=pv_val:
                chan.setValue(pv_val)
        except Exception as e:
            logging.info("Trouble in monit_pv_to_cx_update with "+ str(e))
            set_server_delay(str(e))
    try:
        chan.valueChanged.connect(updateChan)
    except Exception as e:
        logging.info("Trouble in monit_pv_to_cx with "+ str(e))

#monitoring of changes in pv: if changed, copy information from cx again
def monit_cx_to_pv(channel):
    pv = channel.pv
    chan = channel.chan
    def updatePv(value):
        try:
            if is_channel_work_delayed(channel):
                return
            if chan.val==None:
                return
            if channel.datatype!="str":
                pv_val = float(value)
            else:
                pv_val=str(caget(pv,datatype=DBR_STRING))
            if pv_val!=chan.val:
                caput(pv,chan.val)
        except Exception as e:
            logging.info("Trouble in monit_cx_to_pv_update with "+ str(e))
            set_server_delay(str(e))
    try:
        camonitor(pv, updatePv)
    except Exception as e:
        logging.info("Trouble in monit_cx_to_pv with "+ str(e))

#subscribing of cx on pv channel
def subscribe_pv_to_cx(channel):
    pv = channel.pv
    chan = channel.chan
    def updateChan(value):
        #set_pv_to_cx(channel)
        try:
            if "cxstart" in channel.flags and channel.flags["cxstart"]:
                channel.flags["cxstart"] = False
                return None
            if is_channel_work_delayed(channel):
                return
            if channel.datatype!="str":
                pv_val = float(value)
            else:
                pv_val=str(caget(pv,datatype=DBR_STRING))
            if chan.val!=pv_val:
                chan.setValue(pv_val)
        except Exception as e:
            logging.info("Trouble in subscribe_pv_to_cx_update with "+ str(e))
            set_server_delay(str(e))
    try:
        camonitor(pv,updateChan)
    except Exception as e:
        logging.info("Trouble in subscribe_pv_to_cx with "+ str(e))

#subscribing of pv on cx channel
def subscribe_cx_to_pv(channel):
    pv = channel.pv
    chan = channel.chan
    def updatePv(chan):
        try:
            if "pvstart" in channel.flags and channel.flags["pvstart"]:
                channel.flags["pvstart"] = False
                return
            if is_channel_work_delayed(channel):
                return
            if channel.datatype!="str":
                pv_val = float(caget(pv))
            else:
                pv_val=str(caget(pv,datatype=DBR_STRING))
            if pv_val!=chan.val:
                caput(pv,chan.val)
        except Exception as e:
            logging.info("Trouble in subscribe_cx_to_pv_update with "+ str(e))
            set_server_delay(str(e))
    try:
        chan.valueChanged.connect(updatePv)
    except Exception as e:
        logging.info("Trouble in subscribe_cx_to_pv with "+ str(e))

def set_connection(channel,connection):
    if connection["direction"]=="x":
        #set_cx_to_pv(channel)
        subscribe_cx_to_pv(channel)
        monit_cx_to_pv(channel)
    elif connection["direction"]=="p":
        #set_pv_to_cx(channel)
        subscribe_pv_to_cx(channel)
        monit_pv_to_cx(channel)
    elif connection["direction"]=="b":
        if "pvstart" in channel.flags and channel.flags["pvstart"]:
            set_pv_to_cx(channel)
        elif "cxstart" in channel.flags and channel.flags["cxstart"]:
            set_cx_to_pv(channel)
        subscribe_cx_to_pv(channel)
        subscribe_pv_to_cx(channel)


script_dir = os.path.dirname(__file__)

config_info = open_config_file(os.path.join(script_dir,"gateway_config.json"))
a = QtCore.QCoreApplication(sys.argv)
app = cothread.iqt()

logging.basicConfig(filename=os.path.join(script_dir,'info.log'), level=logging.INFO)
logging.info("Start")

try:
	servers = []
	servers.extend((Server("ioc","K500"),Server("ioc","VEPP4"),Server("ioc","VEPP3"),Server("cx","vepp4-vm1:11"),Server("cx","vepp4-pult6:2")))

	chans = []
	for connection in config_info:
	    flags = {}
	    datatype = None
	    if "datatype" in connection and connection["datatype"]=="str":
		chan = cda.StrChan(unicode_to_str(connection["channel"]),on_update=True)
		datatype = connection["datatype"]
	    else:
		chan = cda.Chan(unicode_to_str(connection["channel"]),on_update=True)
	    pv = unicode_to_str(connection["pv"])
	    if "priority" in connection:
		if connection["priority"]=="x":
		    flags["cxstart"] = True
		elif connection["priority"]=="p":
		    flags["pvstart"] = True
	    channel = PvCxChan(chan,connection["channel"],pv,flags,datatype)
	    set_connection(channel,connection)
	    chans.append(channel)
except Exception as e:
	logging.info("Trouble!! "+ str(e))


cothread.WaitForQuit()


