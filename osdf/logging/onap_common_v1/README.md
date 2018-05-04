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

# Common Logging Wrapper for Python

* CommonLogger.py is the module (library) to import
* CommonLogger_test.config is an example configuration file used by CommonLogger_test.py
* CommonLogger_test.py is an example of how to import and use the CommonLogger module

## Configuration File

Configure common logging for a python application in a configuration file.
In the file, put key = value assignments

* defining the filename for each log file you will create, such as
'error=/path/error.log', 'metrics=/path/metrics.log', 'audit=/path/audit.log',
and 'debug=/path/debug.log'.
The name used (shown here as 'error', 'metrics', etc.) is chosen in the program, allowing a single configuration file to be
used by numerous different programs.
(It will be referred to below as &lt;logKey&gt;.)
* defining the style of the log messages to be produced,
using &lt;logKey&gt; suffixed with 'Style', as in 'errorStyle=', and one of the
words 'error', 'metrics', 'audit' and 'debug'.
* defining the minimum level of log messages to be retained in a log file,
using &lt;logKey&gt; suffixed with 'LogLevel', as in 'errorLogLevel=WARN'.
The levels are DEBUG, INFO, WARN, ERROR, and FATAL.
So specifying WARN will retain only WARN, ERROR, and FATAL level
log messages, while specifying DEBUG will retain all levels of log messages:
DEBUG, INFO, WARN, ERROR, and FATAL.

Comments may be included on any line following a '#' character.

Common logging monitors the configuration file so if the file is edited
and any its values change, then common logging will implement the changes
in the running application.
This enables operations to change log levels or even log filenames without
interrupting the running application.

By default, log files are rotated daily at midnight UTC, retaining 6 backup versions by default.

Other strategies can be specified within the configuration file using the keywords:

* rotateMethod = one of 'time', 'size', and 'none' (case insensitive)

If rotateMethod is 'time', the following keywords apply:
* backupCount = Number of rotated backup files to retain, >= 0. 0 retains *all* backups.
* timeRotateIntervalType = one of 'S', 'M', 'H', 'D', 'W0', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'midnight'
(seconds, minutes, hours, days, weekday (0=Monday), or midnight UTC)
* timeRotateInterval = number of seconds/minutes/hours/days between rotations. (Ignored for W#.)

If rotateMethod is 'size', the following keywords apply:
* backupCount = Number of rotated backup files to retain, >= 0. 0 retains *no* backups.
* sizeMaxBytes = maximum number of bytes allowed in the file before rotation
* sizeRotateMode = for now, this defaults to 'a' and may only be specified as 'a'.
It is passed to the underlying Python Logging methods.


Besides logging to a file, it is also possible to send log messages elsewhere,
using &lt;logKey&gt; suffixed with 'LogType'.
You can set &lt;logKey&gt;LogType to any of 'filelogger', 'stdoutlogger', 'stderrlogger', 'socketlogger' orlogger 'null' (case insensitive).

* 'filelogger' is the default specifying logging to a file.
* 'stdoutlogger' and 'stderrlogger' send the output to the corresponding output streams.
* 'socketlogger' will send the output to the corresponding socket host.
* 'nulllogger' turns off logging.

If &lt;logKey&gt;LogType is 'socket', the following keywords apply:
* &lt;logKey&gt;SocketHost = FQDN or IP address for a host to sent the logs to
* &lt;logKey&gt;SocketPort = the port (> 0) to open on that host

This is an example configuration file:

    error           = /var/log/DCAE/vPRO/error.log
    errorLogLevel   = WARN
    errorStyle      = error

    metrics         = /var/log/DCAE/vPRO/metrics.log
    metricsLogLevel = INFO
    metricsStyle      = metrics

    audit           = /var/log/DCAE/vPRO/audit.log
    auditLogLevel   = INFO
    auditStyle      = audit

    debug           = /var/log/DCAE/vPRO/debug.log
    debugLogLevel   = DEBUG
    debugStyle      = debug

## Coding Python Applications to Produce ONAP Common Logging

A python application uses common logging by importing the CommonLogger
module, instantiating a CommonLogger object for each log file, and then
invoking each object's debug, info, warn, error, or fatal methods to log
messages to the file. There are four styles of logging:
error/info logs, debug logs, audit logs, and metrics logs.
The difference between the types of logs is in the list of fields that
are printed out.

### Importing the CommonLogger Module

Importing the CommonLogger module is typical:

    sys.path.append("/opt/app/dcae-commonlogging/python")
    import CommonLogger

### Creating a CommonLogger object:

When creating a CommonLogger object, three arguments are required:

1. The configuration filename.
2. The keyword name in the configuration file that
defines the log filename and parameters controlling rotation of the logfiles.
(This is the &lt;logKey&gt; referred to above.)
3. The keyword arguments for style and to set default values for the log record fields.

The style of the log (one of CommonLoger.DebugFile, CommonLogger.AuditFile,
CommonLogger.MetricsFile and CommonLogger.ErrorFile), must be specified either
in the configuration file (e.g., errorStyle=error or metricsStyle=metrics) or
using a style= keyword and one of the values: CommonLoger.DebugFile,
CommonLogger.AuditFile, CommonLogger.MetricsFile and CommonLogger.ErrorFile.

Keyword arguments for log record fields are as follows.
The annotation indicates whether the field is included in
(d) debug logs, (a) audit logs, (m) metrics logs, and (e) error logs.

* requestID (dame)
* serviceInstanceID (am)
* threadID (am)
* serverName (am)
* serviceName (am)
* instanceUUID (am)
* severity (am)
* serverIPAddress (am)
* server (am)
* IPAddress (am)
* className (am)
* timer (am)
* partnerName (ame)
* targetEntity (me)
* targetServiceName (me)
* statusCode (am)
* responseCode (am)
* responseDescription (am)
* processKey (am)
* targetVirtualEntity (m)
* customField1 (am)
* customField2 (am)
* customField3 (am)
* customField4 (am)
* errorCategory (e)
* errorCode (e)
* errorDescription (e)

Sample code:

    """ The style can be specified here or in the config file using errorStyle. """
    errorLog = CommonLogger.CommonLogger("my.config", "error", style=CommonLogger.ErrorFile, serviceName="DCAE/vPRO")
    infoLog = CommonLogger.CommonLogger("my.config", "info", serviceName="DCAE/vPRO")

### Setting default values for fields:

The object's setFields method allows keyword arguments changing default values for the log record fields.

    errorLog.setFields(serviceName="DCAE/vPRO", threadID="thread-2")

### Calling Methods

The object's debug(), info(), warn(), error(), and fatal() methods require a detailMessage argument
(which can be a zero-length string) and allow the keyword arguments for setting log record field
values for just that one message.
Any newlines or '|' characters in the message will be changed to a single space.

    infoLog.info("Something benign happened.")
    errorLog.fatal("Something very bad happened.", threadID="thread-4")

### Output

Note that no field may contain the '|' (pipe) field separation character, as that
character is used as the separator between fields.
Here is a possible example of a produced log record:

    2015-10-12T15:56:43,182+00:00|netman@localdcae.att.com:~/vPRO_trinity/vPRO.py:905+2015-08-20 20:57:14.463426||||DCAE/vPRO:App-C.Restart|d4d5fc66-70f9-11e5-b0b1-005056866a82|INFO||135.16.76.33|mtvpro01dev1.dev.att.com|||1001|Finished Restart
    2016-12-09T23:06:02,314+00:00||MainThread|DCAE/vPRO|||||||a FATAL message for the error log

### Example Code

The main within CommonLogger.py contains a regression test of the CommonLogger methods.

CommonLogger_test.py contains a complete demonstration of a python application
using the python CommonLogging wrapper module, including creating UUIDs,
setting default log field values, and timing operations.

## Upgrading from Previous Versions of CommonLogger

The current version of CommonLogger is 99% compatible with earlier versions of CommonLogger.
The key change, due to update ONAP logging requirements, is the choice to use different lists
of fields in different types of log files.
This required adding a mandatory "style" to be given, which we chose to do using either a
new keyword in the configuration file, or using a new parameter keyword when creating the logger.
