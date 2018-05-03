#!/usr/bin/python

# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#
"""
Test the ONAP Common Logging library in Python.
CommonLogger_test.py
"""


from __future__ import print_function   # for the example code below parsing command line options
import os, sys, getopt                  # for the example code below parsing command line options

import CommonLogger                     # all that is needed to import the CommonLogger library

import uuid                             # to create UUIDs for our log records
import time                             # to create elapsed time for our log records


#----- A client might want to allow specifying the configFile as a command line option
usage="usage: %s [ -c <configFile> ]" % ( os.path.basename(__file__) )
try:
    opts, args = getopt.getopt(sys.argv[1:], "c:")
except getopt.GetoptError:
    print(usage, file=sys.stderr)
    sys.exit(2)

configFile = "CommonLogger_test.config"
for opt, arg in opts:
    if opt == "-c":
        configFile = arg
    else:
        print(usage, file=sys.stderr)
        sys.exit(2)


#----- Instantiate the loggers

# The client's top-level program (e.g., vPRO.py) can create a unique identifier UUID to differentiate between multiple instances of itself.
instanceUUID = uuid.uuid1()

# The client should identify its ONAP component -- and if applicable -- its ONAP sub-component
serviceName = "DCAE/vPRO"

# Instantiate using a configuration file with a key specifying the log file name and set fields' default values
errorLog =   CommonLogger.CommonLogger(configFile, "error",   instanceUUID=instanceUUID, serviceName=serviceName)
metricsLog = CommonLogger.CommonLogger(configFile, "metrics", instanceUUID=instanceUUID, serviceName=serviceName)
auditLog =   CommonLogger.CommonLogger(configFile, "audit",   instanceUUID=instanceUUID, serviceName=serviceName)
debugLog =   CommonLogger.CommonLogger(configFile, "debug",   instanceUUID=instanceUUID, serviceName=serviceName)


#----- use the loggers

# both metrics and audit logs can have an event starting time. This only affects the next log message.
metricsLog.setStartRecordEvent()
auditLog.setStartRecordEvent()

# Simple log messages
debugLog.debug("a DEBUG message for the debug log")
metricsLog.info("an INFO message for the metrics log")
auditLog.info("an INFO message for the audit log")
errorLog.warn("a WARN message for the error log")
errorLog.error("an ERROR message for the error log")
errorLog.fatal("a FATAL message for the error log")


# Can override any of the other fields when writing each log record
debugLog.debug("demonstrating overriding all fields with atypical values", requestID="2", serviceInstanceID="3", threadID="4", serverName="5", serviceName="6", instanceUUID="7", severity="9", serverIPAddress="10", server="11", IPAddress="12", className="13", timer="14")


# The is an example of an interaction between two ONAP components:

# vPRO generates Closed Loop RESTful API requests to App-C, knowing this information:
requestClient = "netman@localdcae.att.com:~/vPRO_trinity/vPRO.py:905"  # uniquely identifies the requester
requestTime = "2015-08-20 20:57:14.463426"                             # unique ID of the request within the requester's scope
request = "Restart"

# Form the value for Common Logging's requestID field:
requestID = requestClient + "+" + requestTime  # vPRO will use this as the unique requestID
# requestID = uuid.uuid1()  # other services might generate a UUID as their requestID

# Form the value for Common Logging's serviceName field when an interaction between two ONAP components:
ourONAP = serviceName
peerONAP = "App-C"
operation = request
interaction = ourONAP + ":" + peerONAP + "." + operation

# Let's calculate and report elapsed times
start = time.time()

# Log the request
auditLog.info("Requesting %s to %s" %(peerONAP, operation), requestID=requestID, serviceName=interaction)

# Wait for first response
time.sleep(1)  # simulate processing the action, e.g., waiting for response from App-C

# Form the value for Common Logging's serviceName field when an interaction between two ONAP components:
operation = 'PENDING'
interaction = peerONAP + ":" + ourONAP + "." + operation

# Log the response with elapsed time
ms = int(round(1000 * (time.time() - start)))  # Calculate elapsed time in ms
auditLog.info("%s acknowledged receiving request for %s" %(peerONAP, operation), requestID=requestID, serviceName=interaction, timer=ms)

# Wait for next response
time.sleep(1)  # simulate processing the action, e.g., waiting for response from App-C

# Form the value for Common Logging's serviceName field when an interaction between two ONAP components:
operation = 'SUCCESS'
interaction = peerONAP + ":" + ourONAP + "." + operation

# Log the response with elapsed time
ms = int(round(1000 * (time.time() - start)))  # Calculate elapsed time in ms
auditLog.info("%s finished %s" %(peerONAP, operation), requestID=requestID, serviceName=interaction, timer=ms)


# Can change the fields' default values for a logger after instantiation if desired
debugLog.setFields(serviceName="DCAE", threadID='thread-2')

# Then subsequent logging will have the new default field values
debugLog.info("Something happened")
debugLog.warn("Something happened again")


# Unset (set=None) a field so the Common Logger will use the default value
debugLog.info("threadID should be default", threadID=None)
debugLog.setFields(threadID=None)
debugLog.info("threadID should be default")
