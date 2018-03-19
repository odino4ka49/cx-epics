#!/usr/bin/env python

import cothread.catools as catools
import cothread
from cothread.catools import *
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from PyQt4 import QtCore
import pycx4.qcda as cda
import json


def openConfigFile(filename):
    data = []
    with open(filename) as data_file:
        data = json.load(data_file)
    return data

def unicodeToStr(name):
    string = name.encode('ascii','ignore')
    return string

def printval(chan):
    print "cx "+str(chan.val)

def print_data(value):
    print "pv "+str(value)

def setPvToCx(pv,chan):
    def updateChan(value):
        try:
            if chan.val!=float(value):
                print pv + " " + str(chan.val)+" "+str(value)
                chan.setValue(value)
        except Exception:
            print "Trouble in caget"
    camonitor(pv,updateChan)
    chan.valueChanged.connect(printval)

def setCxToPv(pv,chan):
    def updatePv(chan):
        try:
            pv_val = caget(pv)
            if float(pv_val)!=chan.val:
                #print "x "+str(chan.val) + " " + str(pv_val)
                caput(pv,chan.val)
                #print str(chan.val) + " " + str(caget(pv))
            else:
                print "Already right"
        except Exception:
            print "Trouble in caget"
    chan.valueChanged.connect(updatePv)

def setConnection(connection,chan):
    pv = unicodeToStr(connection["pv"])
    if connection["direction"]=="x":
        setCxToPv(pv,chan)
    elif connection["direction"]=="p":
        setPvToCx(pv,chan)
    elif connection["direction"]=="b":
        setCxToPv(pv,chan)
        setPvToCx(pv,chan)


config_info = []
config_info = openConfigFile("gateway_config.json")
app = cothread.iqt()

#setConnection(confinfo)

#channel = cda.Chan("vepp4-pult6:2.m5.dcct2")
#channel2 = cda.Chan("vepp4-pult6:2.cgvi.prescaler")
#setCxToPv("K500:M5_I:DCCT2-I",channel)
chans = []
for connection in config_info:
    chan = cda.Chan(unicodeToStr(connection["channel"]))
    chans.append(chan)
    setConnection(connection,chan)

chan = cda.Chan("vepp4-vm1:5.V3_CurrentTotal_RB")
#chan.valueChanged.connect(printval)
#camonitor("V3:CurrentLifeTime-RB", print_data)"""

cothread.WaitForQuit()
