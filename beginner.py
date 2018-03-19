__author__ = 'oidin'
#!/usr/bin/env python
import sys
sys.path.append('/usr/share/pyshared')
sys.path.append('/usr/lib/pyshared/python2.7')
from pkg_resources import require
require('cothread')
import cothread
from cothread.catools import *

from PyQt4 import QtCore # import PyQt
import pycx4.qcda as cda # import qcda

# this makes python interpreter exit on Ctrl-C
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

# defining a collback or slot does'n matter how to name it
# function accepts on argument - a channel which sends this signal
# really it's a pointer to channel
def printval(chan):
    print chan.val,chan.dtype

app = QtCore.QCoreApplication(sys.argv) # first you need Qt app

print(caget('V4:InjPolarityOrder-RB'))

#chan = cda.Chan("vepp4-pult6:2.m5.Iset") # register a channel with given name
chan = cda.Chan("vepp4-vm1:5.V3_StatusOrder_RB")
#print chan.val
chan.valueMeasured.connect(printval)   # connect our callback to channel's signal
#chan.setValue(1)
#print wchan.val

sys.exit(app.exec_()) # run main loop
