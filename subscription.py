#!/usr/bin/env python

import sys
sys.path.append('/usr/share/pyshared')
sys.path.append('/usr/lib/pyshared/python2.7')
from pkg_resources import require
require('cothread')
import cothread.catools as catools
import cothread
from cothread.catools import *
import os
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from PyQt4 import QtCore
import pycx4.qcda as cda


import logging


def openListFile(filename):
    data = alist = [line.rstrip() for line in open(filename)]
    """f = open(filename,'r')
    list = f.read().splitlines() 
    for line in f:
        data.append(line)"""
    return data

def unicodeToStr(name):
    string = name.encode('ascii','ignore')
    return string

def printval(channel):
    print channel.val
    logging.info(str(channel.name)+"\t"+str(channel.val))

def setSubscription(channel):
    channel.valueChanged.connect(printval)

script_dir = os.path.dirname(__file__)

channels = []
channels = openListFile(os.path.join(script_dir,"cx_subscriptions"))
app = QtCore.QCoreApplication(sys.argv)

logging.basicConfig(format='%(asctime)s %(message)s', filename='subscription_info.log', level=logging.INFO)

chans = []
for chname in channels:
    chan = cda.Chan(unicodeToStr(chname))
    chans.append(chan)
    setSubscription(chan)
#chan = cda.Chan("vepp4-pult6:2.m5.dcct1")

sys.exit(app.exec_())
