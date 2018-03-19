#!/usr/bin/env python

import cothread.catools as catools
import cothread
from cothread.catools import *
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from PyQt4 import QtCore
import pycx4.qcda as cda
import json
import time
import os

import logging

class PvCxChan:
    def __init__(self,chan,pv,flags,datatype=None):
        self.chan = chan
        self.pv = pv
        self.flags = flags
        self.datatype = datatype


def openConfigFile(filename):
    with open(filename) as data_file:
        data = json.load(data_file)
    return data

def unicodeToStr(name):
    string = name.encode('ascii', 'ignore')
    return string

def printval(chan):
    logging.info("cx "+str(chan.val))

def print_data(value):
    logging.info("pv "+str(value))

def setPvToCx(channel):
    pv = channel.pv
    chan = channel.chan
    def updateChan(value):
        pv_val = value
        if channel.datatype!="str":
            pv_val = float(value)
        if pv_val!=chan.val:
            if channel.datatype=="str":
                chan.setValue(str(pv_val))
            else:
                chan.setValue(pv_val)
    try:
        connect(pv)
        updateChan(caget(pv))
    except Exception:
            logging.info("Trouble in setPvToCx with "+pv)

def setCxToPv(channel):
    pv = channel.pv
    chan = channel.chan
    def updatePv(chan):
        pv_val = caget(pv)
        if channel.datatype!="str":
            pv_val = float(pv_val)
        if pv_val!=chan.val:
            caput(pv,chan.val)
    try:
        chan.valueMeasured.connect(updatePv)
    except Exception:
        logging.info("Trouble in setCxToPv with "+pv)

def monitPvToCx(channel):
    pv = channel.pv
    chan = channel.chan
    def updateChan(value):
        try:
            if "cxstart" in channel.flags and channel.flags["cxstart"]:
                channel.flags["cxstart"] = False
                return None
            pv_val = value
            if channel.datatype!="str":
                pv_val = float(value)
            if chan.val!=pv_val:
                chan.setValue(pv_val)
        except Exception:
            logging.info("Trouble in monitPvToCx with "+pv)
    try:
        camonitor(pv,updateChan)
    except Exception:
        logging.info("Trouble in monitPvToCx with "+pv)

def monitCxToPv(channel):
    pv = channel.pv
    chan = channel.chan
    def updatePv(chan):
        try:
            if "pvstart" in channel.flags and channel.flags["pvstart"]:
                channel.flags["pvstart"] = False
                return
            pv_val = caget(pv)
            if channel.datatype!="str":
                pv_val = float(pv_val)
            if pv_val!=chan.val:
                if channel.datatype=="str":
                    chan.setValue(str(pv_val))
                else:
                    caput(pv,chan.val)
        except Exception:
            logging.info("Trouble in monitCxToPv with "+pv)
    try:
        chan.valueChanged.connect(updatePv)
    except Exception:
        logging.info("Trouble in monitCxToPv with "+pv)

def setConnection(channel,connection):
    if connection["direction"]=="x":
        setCxToPv(channel)
        monitCxToPv(channel)
    elif connection["direction"]=="p":
        setPvToCx(channel)
        monitPvToCx(channel)
    elif connection["direction"]=="b":
        if "pvstart" in channel.flags and channel.flags["pvstart"]:
            setPvToCx(channel)
        elif "cxstart" in channel.flags and channel.flags["cxstart"]:
            setCxToPv(channel)
        monitCxToPv(channel)
        monitPvToCx(channel)

script_dir = os.path.dirname(__file__)

config_info = openConfigFile(os.path.join(script_dir,"gateway_config.json"))
app = cothread.iqt()

logging.basicConfig(filename=os.path.join(script_dir,'info.log'), level=logging.INFO)
logging.info("Start")

chans = []
for connection in config_info:
    flags = {}
    datatype = None
    if "datatype" in connection and connection["datatype"]=="str":
        chan = cda.StrChan(unicodeToStr(connection["channel"]))
        datatype = connection["datatype"]
    else:
        chan = cda.Chan(unicodeToStr(connection["channel"]))
    pv = unicodeToStr(connection["pv"])
    if "priority" in connection:
        if connection["priority"]=="x":
            flags["cxstart"] = True
        elif connection["priority"]=="p":
            flags["pvstart"] = True
    channel = PvCxChan(chan,pv,flags,datatype)
    setConnection(channel,connection)
    chans.append(channel)
    chans.append(chan)

cothread.WaitForQuit()


