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

"""ONAP Common Logging library in Python."""

#!/usr/bin/python
# -*- indent-tabs-mode: nil -*- vi: set expandtab:


from __future__ import print_function
import os, sys, getopt, logging, logging.handlers, time, re, uuid, socket, threading

class CommonLogger:
    """ONAP Common Logging object.

    Public methods:
    __init__
    setFields
    debug
    info
    warn
    error
    fatal
    """

    UnknownFile = -1
    ErrorFile = 0
    DebugFile = 1
    AuditFile = 2
    MetricsFile = 3
    DateFmt = '%Y-%m-%dT%H:%M:%S'
    verbose = False

    def __init__(self, configFile, logKey, **kwargs):
        """Construct a Common Logger for one Log File.

        Arguments:
        configFile             -- configuration filename.
        logKey                 -- the keyword in configFile that identifies the log filename.

        Keyword arguments: Annotations are d:debug, a=audit, m=metrics, e=error
        style                       -- the log file format (style) to use when writing log messages,
                                       one of CommonLogger.ErrorFile, CommonLogger.DebugFile,
                                       CommonLogger.AuditFile and CommonLogger.MetricsFile, or
                                       one of the strings "error", "debug", "audit" or "metrics".
                                       May also be set in the config file using a field named
                                       <logKey>Style (where <logKey> is the value of the logKey
                                       parameter). The keyword value overrides the value in the
                                       config file.
        requestID (dame)            -- optional default value for this log record field.
        serviceInstanceID (am)      -- optional default value for this log record field.
        threadID (am)               -- optional default value for this log record field.
        serverName (am)             -- optional default value for this log record field.
        serviceName (am)            -- optional default value for this log record field.
        instanceUUID (am)           -- optional default value for this log record field.
        severity (am)               -- optional default value for this log record field.
        serverIPAddress (am)        -- optional default value for this log record field.
        server (am)                 -- optional default value for this log record field.
        IPAddress (am)              -- optional default value for this log record field.
        className (am)              -- optional default value for this log record field.
        timer (am)                  -- (ElapsedTime) optional default value for this log record field.
        partnerName (ame)           -- optional default value for this log record field.
        targetEntity (me)           -- optional default value for this log record field.
        targetServiceName (me)      -- optional default value for this log record field.
        statusCode (am)             -- optional default value for this log record field.
        responseCode (am)           -- optional default value for this log record field.
        responseDescription (am)    -- optional default value for this log record field.
        processKey (am)             -- optional default value for this log record field.
        targetVirtualEntity (m)     -- optional default value for this log record field.
        customField1 (am)           -- optional default value for this log record field.
        customField2 (am)           -- optional default value for this log record field.
        customField3 (am)           -- optional default value for this log record field.
        customField4 (am)           -- optional default value for this log record field.
        errorCategory (e)           -- optional default value for this log record field.
        errorCode (e)               -- optional default value for this log record field.
        errorDescription (e)        -- optional default value for this log record field.

        Note:  the pipe '|' character is not allowed in any log record field.
        """

        self._monitorFlag = False

        # Get configuration parameters
        self._logKey = str(logKey)
        self._configFile = str(configFile)
        self._rotateMethod = 'time'
        self._timeRotateIntervalType = 'midnight'
        self._timeRotateInterval = 1
        self._sizeMaxBytes = 0
        self._sizeRotateMode = 'a'
        self._socketHost = None
        self._socketPort = 0
        self._typeLogger = 'filelogger'
        self._backupCount = 6
        self._logLevelThreshold = self._intLogLevel('')
        self._logFile = None
        self._begTime = None
        self._begMsec = 0
        self._fields = {}
        self._fields["style"] = CommonLogger.UnknownFile
        try:
            self._configFileModified = os.path.getmtime(self._configFile)
            for line in open(self._configFile):
                line = line.split('#',1)[0]    # remove comments
                if '=' in line:
                    key, value = [x.strip() for x in line.split('=',1)]
                    if key == 'rotateMethod' and value.lower() in ['time', 'size', 'none']:
                        self._rotateMethod = value.lower()
                    elif key == 'timeRotateIntervalType' and value in ['S', 'M', 'H', 'D', 'W0', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'midnight']:
                        self._timeRotateIntervalType = value
                    elif key == 'timeRotateInterval' and int( value ) > 0:
                        self._timeRotateInterval = int( value )
                    elif key == 'sizeMaxBytes' and int( value ) >= 0:
                        self._sizeMaxBytes = int( value )
                    elif key == 'sizeRotateMode' and value in ['a']:
                        self._sizeRotateMode = value
                    elif key == 'backupCount' and int( value ) >= 0:
                        self._backupCount = int( value )
                    elif key == self._logKey + 'SocketHost':
                        self._socketHost = value
                    elif key == self._logKey + 'SocketPort' and int( value ) == 0:
                        self._socketPort = int( value )
                    elif key == self._logKey + 'LogType' and value.lower() in ['filelogger', 'stdoutlogger', 'stderrlogger', 'socketlogger', 'nulllogger']:
                        self._typeLogger = value.lower()
                    elif key == self._logKey + 'LogLevel':
                        self._logLevelThreshold = self._intLogLevel(value.upper())
                    elif key == self._logKey + 'Style':
                        self._fields["style"] = value
                    elif key == self._logKey:
                        self._logFile = value
        except Exception as x:
            print("exception reading '%s' configuration file: %s" %(self._configFile, str(x)), file=sys.stderr)
            sys.exit(2)
        except:
            print("exception reading '%s' configuration file" %(self._configFile), file=sys.stderr)
            sys.exit(2)

        if self._logFile is None:
            print('configuration file %s is missing definition %s for log file' %(self._configFile, self._logKey), file=sys.stderr)
            sys.exit(2)


        # initialize default log fields
        # timestamp will automatically be generated
        for key in ['style', 'requestID', 'serviceInstanceID', 'threadID', 'serverName', 'serviceName', 'instanceUUID', \
                    'severity', 'serverIPAddress', 'server', 'IPAddress', 'className', 'timer', \
                    'partnerName', 'targetEntity', 'targetServiceName', 'statusCode', 'responseCode', \
                    'responseDescription', 'processKey', 'targetVirtualEntity', 'customField1', \
                    'customField2', 'customField3', 'customField4', 'errorCategory', 'errorCode', \
                    'errorDescription' ]:
            if key in kwargs and kwargs[key] != None:
                self._fields[key] = kwargs[key]

        self._resetStyleField()

        # Set up logger
        self._logLock = threading.Lock()
        with self._logLock:
            self._logger = logging.getLogger(self._logKey)
            self._logger.propagate = False
            self._createLogger()

        self._defaultServerInfo()

        # spawn a thread to monitor configFile for logLevel and logFile changes
        self._monitorFlag = True
        self._monitorThread = threading.Thread(target=self._monitorConfigFile, args=())
        self._monitorThread.daemon = True
        self._monitorThread.start()


    def _createLogger(self):
        if self._typeLogger == 'filelogger':
            self._mkdir_p(self._logFile)
            if self._rotateMethod == 'time':
                self._logHandler = logging.handlers.TimedRotatingFileHandler(self._logFile, \
                                                                             when=self._timeRotateIntervalType, interval=self._timeRotateInterval, \
                                                                             backupCount=self._backupCount, encoding=None, delay=False, utc=True)
            elif self._rotateMethod == 'size':
                self._logHandler = logging.handlers.RotatingFileHandler(self._logFile, \
                                                                        mode=self._sizeRotateMode, maxBytes=self._sizeMaxBytes, \
                                                                        backupCount=self._backupCount, encoding=None, delay=False)
                
            else:
                self._logHandler = logging.handlers.WatchedFileHandler(self._logFile, \
                                                                       mode=self._sizeRotateMode, \
                                                                       encoding=None, delay=False)
        elif self._typeLogger == 'stderrlogger':
            self._logHandler = logging.handlers.StreamHandler(sys.stderr)
        elif self._typeLogger == 'stdoutlogger':
            self._logHandler = logging.handlers.StreamHandler(sys.stdout)
        elif self._typeLogger == 'socketlogger':
            self._logHandler = logging.handlers.SocketHandler(self._socketHost, self._socketPort)
        elif self._typeLogger == 'nulllogger':
            self._logHandler = logging.handlers.NullHandler()

        if self._fields["style"] == CommonLogger.AuditFile or self._fields["style"] == CommonLogger.MetricsFile:
            self._logFormatter = logging.Formatter(fmt='%(begtime)s,%(begmsecs)03d+00:00|%(endtime)s,%(endmsecs)03d+00:00|%(message)s', datefmt=CommonLogger.DateFmt)
        else:
            self._logFormatter = logging.Formatter(fmt='%(asctime)s,%(msecs)03d+00:00|%(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
        self._logFormatter.converter = time.gmtime
        self._logHandler.setFormatter(self._logFormatter)
        self._logger.addHandler(self._logHandler)

    def _resetStyleField(self):
        styleFields = ["error", "debug", "audit", "metrics"]
        if self._fields['style'] in styleFields:
            self._fields['style'] = styleFields.index(self._fields['style'])

    def __del__(self):
        if self._monitorFlag == False:
            return

        self._monitorFlag = False

        if self._monitorThread is not None and self._monitorThread.is_alive():
            self._monitorThread.join()

        self._monitorThread = None


    def _defaultServerInfo(self):

        # If not set or purposely set = None, then set default
        if self._fields.get('server') is None:
            try:
                self._fields['server']          = socket.getfqdn()
            except Exception as err:
                try:
                    self._fields['server']      = socket.gethostname()
                except Exception as err:
                    self._fields['server']      = ""

        # If not set or purposely set = None, then set default
        if self._fields.get('serverIPAddress') is None:
            try:
                self._fields['serverIPAddress'] = socket.gethostbyname(self._fields['server'])
            except Exception as err:
                self._fields['serverIPAddress'] = ""


    def _monitorConfigFile(self):
        while self._monitorFlag:
            try:
                fileTime = os.path.getmtime(self._configFile)
                if fileTime > self._configFileModified:
                    self._configFileModified = fileTime
                    ReopenLogFile = False
                    logFile = self._logFile
                    with open(self._configFile) as fp:
                        for line in fp:
                            line = line.split('#',1)[0]    # remove comments
                            if '=' in line:
                                key, value = [x.strip() for x in line.split('=',1)]
                                if key == 'rotateMethod' and value.lower() in ['time', 'size', 'none'] and self._rotateMethod != value:
                                    self._rotateMethod = value.lower()
                                    ReopenLogFile = True
                                elif key == 'timeRotateIntervalType' and value in ['S', 'M', 'H', 'D', 'W0', 'W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'midnight']:
                                    self._timeRotateIntervalType = value
                                    ReopenLogFile = True
                                elif key == 'timeRotateInterval' and int( value ) > 0:
                                    self._timeRotateInterval = int( value )
                                    ReopenLogFile = True
                                elif key == 'sizeMaxBytes' and int( value ) >= 0:
                                    self._sizeMaxBytes = int( value )
                                    ReopenLogFile = True
                                elif key == 'sizeRotateMode' and value in ['a']:
                                    self._sizeRotateMode = value
                                    ReopenLogFile = True
                                elif key == 'backupCount' and int( value ) >= 0:
                                    self._backupCount = int( value )
                                    ReopenLogFile = True
                                elif key == self._logKey + 'SocketHost' and self._socketHost != value:
                                    self._socketHost = value
                                    ReopenLogFile = True
                                elif key == self._logKey + 'SocketPort' and self._socketPort > 0 and self._socketPort != int( value ):
                                    self._socketPort = int( value )
                                    ReopenLogFile = True
                                elif key == self._logKey + 'LogLevel' and self._logLevelThreshold != self._intLogLevel( value.upper() ):
                                    self._logLevelThreshold = self._intLogLevel(value.upper())
                                elif key == self._logKey + 'LogType' and self._typeLogger != value and value.lower() in ['filelogger', 'stdoutlogger', 'stderrlogger', 'socketlogger', 'nulllogger']:
                                    self._typeLogger = value.lower()
                                    ReopenLogFile = True
                                elif key == self._logKey + 'Style':
                                    self._fields["style"] = value
                                    self._resetStyleField()
                                elif key == self._logKey and self._logFile != value:
                                    logFile = value
                                    ReopenLogFile = True
                    if ReopenLogFile:
                        with self._logLock:
                            self._logger.removeHandler(self._logHandler)
                            self._logFile = logFile
                            self._createLogger()
            except Exception as err:
                pass

            time.sleep(5)


    def setFields(self, **kwargs):
        """Set default values for log fields.

        Keyword arguments: Annotations are d:debug, a=audit, m=metrics, e=error
        style                       -- the log file format (style) to use when writing log messages
        requestID (dame)            -- optional default value for this log record field.
        serviceInstanceID (am)      -- optional default value for this log record field.
        threadID (am)               -- optional default value for this log record field.
        serverName (am)             -- optional default value for this log record field.
        serviceName (am)            -- optional default value for this log record field.
        instanceUUID (am)           -- optional default value for this log record field.
        severity (am)               -- optional default value for this log record field.
        serverIPAddress (am)        -- optional default value for this log record field.
        server (am)                 -- optional default value for this log record field.
        IPAddress (am)              -- optional default value for this log record field.
        className (am)              -- optional default value for this log record field.
        timer (am)                  -- (ElapsedTime) optional default value for this log record field.
        partnerName (ame)           -- optional default value for this log record field.
        targetEntity (me)           -- optional default value for this log record field.
        targetServiceName (me)      -- optional default value for this log record field.
        statusCode (am)             -- optional default value for this log record field.
        responseCode (am)           -- optional default value for this log record field.
        responseDescription (am)    -- optional default value for this log record field.
        processKey (am)             -- optional default value for this log record field.
        targetVirtualEntity (m)     -- optional default value for this log record field.
        customField1 (am)           -- optional default value for this log record field.
        customField2 (am)           -- optional default value for this log record field.
        customField3 (am)           -- optional default value for this log record field.
        customField4 (am)           -- optional default value for this log record field.
        errorCategory (e)           -- optional default value for this log record field.
        errorCode (e)               -- optional default value for this log record field.
        errorDescription (e)        -- optional default value for this log record field.

        Note:  the pipe '|' character is not allowed in any log record field.
        """

        for key in ['style', 'requestID', 'serviceInstanceID', 'threadID', 'serverName', 'serviceName', 'instanceUUID', \
                    'severity', 'serverIPAddress', 'server', 'IPAddress', 'className', 'timer', \
                    'partnerName', 'targetEntity', 'targetServiceName', 'statusCode', 'responseCode', \
                    'responseDescription', 'processKey', 'targetVirtualEntity', 'customField1', \
                    'customField2', 'customField3', 'customField4', 'errorCategory', 'errorCode', \
                    'errorDescription' ]:
            if key in kwargs:
                if kwargs[key] != None:
                    self._fields[key] = kwargs[key]
                elif key in self._fields:
                    del self._fields[key]

        self._defaultServerInfo()


    def debug(self, message, **kwargs):
        """Write a DEBUG level message to the log file.

        Arguments:
        message           -- value for the last log record field.

        Keyword arguments: Annotations are d:debug, a=audit, m=metrics, e=error
        style                       -- the log file format (style) to use when writing log messages
        requestID (dame)            -- optional default value for this log record field.
        serviceInstanceID (am)      -- optional default value for this log record field.
        threadID (am)               -- optional default value for this log record field.
        serverName (am)             -- optional default value for this log record field.
        serviceName (am)            -- optional default value for this log record field.
        instanceUUID (am)           -- optional default value for this log record field.
        severity (am)               -- optional default value for this log record field.
        serverIPAddress (am)        -- optional default value for this log record field.
        server (am)                 -- optional default value for this log record field.
        IPAddress (am)              -- optional default value for this log record field.
        className (am)              -- optional default value for this log record field.
        timer (am)                  -- (ElapsedTime) optional default value for this log record field.
        partnerName (ame)           -- optional default value for this log record field.
        targetEntity (me)           -- optional default value for this log record field.
        targetServiceName (me)      -- optional default value for this log record field.
        statusCode (am)             -- optional default value for this log record field.
        responseCode (am)           -- optional default value for this log record field.
        responseDescription (am)    -- optional default value for this log record field.
        processKey (am)             -- optional default value for this log record field.
        targetVirtualEntity (m)     -- optional default value for this log record field.
        customField1 (am)           -- optional default value for this log record field.
        customField2 (am)           -- optional default value for this log record field.
        customField3 (am)           -- optional default value for this log record field.
        customField4 (am)           -- optional default value for this log record field.
        errorCategory (e)           -- optional default value for this log record field.
        errorCode (e)               -- optional default value for this log record field.
        errorDescription (e)        -- optional default value for this log record field.

        Note:  the pipe '|' character is not allowed in any log record field.
        """

        self._log('DEBUG', message, errorCategory = 'DEBUG', **kwargs)

    def info(self, message, **kwargs):
        """Write an INFO level message to the log file.

        Arguments:
        message           -- value for the last log record field.

        Keyword arguments: Annotations are d:debug, a=audit, m=metrics, e=error
        style                       -- the log file format (style) to use when writing log messages
        requestID (dame)            -- optional default value for this log record field.
        serviceInstanceID (am)      -- optional default value for this log record field.
        threadID (am)               -- optional default value for this log record field.
        serverName (am)             -- optional default value for this log record field.
        serviceName (am)            -- optional default value for this log record field.
        instanceUUID (am)           -- optional default value for this log record field.
        severity (am)               -- optional default value for this log record field.
        serverIPAddress (am)        -- optional default value for this log record field.
        server (am)                 -- optional default value for this log record field.
        IPAddress (am)              -- optional default value for this log record field.
        className (am)              -- optional default value for this log record field.
        timer (am)                  -- (ElapsedTime) optional default value for this log record field.
        partnerName (ame)           -- optional default value for this log record field.
        targetEntity (me)           -- optional default value for this log record field.
        targetServiceName (me)      -- optional default value for this log record field.
        statusCode (am)             -- optional default value for this log record field.
        responseCode (am)           -- optional default value for this log record field.
        responseDescription (am)    -- optional default value for this log record field.
        processKey (am)             -- optional default value for this log record field.
        targetVirtualEntity (m)     -- optional default value for this log record field.
        customField1 (am)           -- optional default value for this log record field.
        customField2 (am)           -- optional default value for this log record field.
        customField3 (am)           -- optional default value for this log record field.
        customField4 (am)           -- optional default value for this log record field.
        errorCategory (e)           -- optional default value for this log record field.
        errorCode (e)               -- optional default value for this log record field.
        errorDescription (e)        -- optional default value for this log record field.

        Note:  the pipe '|' character is not allowed in any log record field.
        """

        self._log('INFO', message, errorCategory = 'INFO', **kwargs)

    def warn(self, message, **kwargs):
        """Write a WARN level message to the log file.

        Arguments:
        message           -- value for the last log record field.

        Keyword arguments: Annotations are d:debug, a=audit, m=metrics, e=error
        style                       -- the log file format (style) to use when writing log messages
        requestID (dame)            -- optional default value for this log record field.
        serviceInstanceID (am)      -- optional default value for this log record field.
        threadID (am)               -- optional default value for this log record field.
        serverName (am)             -- optional default value for this log record field.
        serviceName (am)            -- optional default value for this log record field.
        instanceUUID (am)           -- optional default value for this log record field.
        severity (am)               -- optional default value for this log record field.
        serverIPAddress (am)        -- optional default value for this log record field.
        server (am)                 -- optional default value for this log record field.
        IPAddress (am)              -- optional default value for this log record field.
        className (am)              -- optional default value for this log record field.
        timer (am)                  -- (ElapsedTime) optional default value for this log record field.
        partnerName (ame)           -- optional default value for this log record field.
        targetEntity (me)           -- optional default value for this log record field.
        targetServiceName (me)      -- optional default value for this log record field.
        statusCode (am)             -- optional default value for this log record field.
        responseCode (am)           -- optional default value for this log record field.
        responseDescription (am)    -- optional default value for this log record field.
        processKey (am)             -- optional default value for this log record field.
        targetVirtualEntity (m)     -- optional default value for this log record field.
        customField1 (am)           -- optional default value for this log record field.
        customField2 (am)           -- optional default value for this log record field.
        customField3 (am)           -- optional default value for this log record field.
        customField4 (am)           -- optional default value for this log record field.
        errorCategory (e)           -- optional default value for this log record field.
        errorCode (e)               -- optional default value for this log record field.
        errorDescription (e)        -- optional default value for this log record field.

        Note:  the pipe '|' character is not allowed in any log record field.
        """

        self._log('WARN', message, errorCategory = 'WARN', **kwargs)

    def error(self, message, **kwargs):
        """Write an ERROR level message to the log file.

        Arguments:
        message           -- value for the last log record field.

        Keyword arguments: Annotations are d:debug, a=audit, m=metrics, e=error
        style                       -- the log file format (style) to use when writing log messages
        requestID (dame)            -- optional default value for this log record field.
        serviceInstanceID (am)      -- optional default value for this log record field.
        threadID (am)               -- optional default value for this log record field.
        serverName (am)             -- optional default value for this log record field.
        serviceName (am)            -- optional default value for this log record field.
        instanceUUID (am)           -- optional default value for this log record field.
        severity (am)               -- optional default value for this log record field.
        serverIPAddress (am)        -- optional default value for this log record field.
        server (am)                 -- optional default value for this log record field.
        IPAddress (am)              -- optional default value for this log record field.
        className (am)              -- optional default value for this log record field.
        timer (am)                  -- (ElapsedTime) optional default value for this log record field.
        partnerName (ame)           -- optional default value for this log record field.
        targetEntity (me)           -- optional default value for this log record field.
        targetServiceName (me)      -- optional default value for this log record field.
        statusCode (am)             -- optional default value for this log record field.
        responseCode (am)           -- optional default value for this log record field.
        responseDescription (am)    -- optional default value for this log record field.
        processKey (am)             -- optional default value for this log record field.
        targetVirtualEntity (m)     -- optional default value for this log record field.
        customField1 (am)           -- optional default value for this log record field.
        customField2 (am)           -- optional default value for this log record field.
        customField3 (am)           -- optional default value for this log record field.
        customField4 (am)           -- optional default value for this log record field.
        errorCategory (e)           -- optional default value for this log record field.
        errorCode (e)               -- optional default value for this log record field.
        errorDescription (e)        -- optional default value for this log record field.

        Note:  the pipe '|' character is not allowed in any log record field.
        """

        self._log('ERROR', message, errorCategory = 'ERROR', **kwargs)

    def fatal(self, message, **kwargs):
        """Write a FATAL level message to the log file.

        Arguments:
        message           -- value for the last log record field.

        Keyword arguments: Annotations are d:debug, a=audit, m=metrics, e=error
        style                       -- the log file format (style) to use when writing log messages
        requestID (dame)            -- optional default value for this log record field.
        serviceInstanceID (am)      -- optional default value for this log record field.
        threadID (am)               -- optional default value for this log record field.
        serverName (am)             -- optional default value for this log record field.
        serviceName (am)            -- optional default value for this log record field.
        instanceUUID (am)           -- optional default value for this log record field.
        severity (am)               -- optional default value for this log record field.
        serverIPAddress (am)        -- optional default value for this log record field.
        server (am)                 -- optional default value for this log record field.
        IPAddress (am)              -- optional default value for this log record field.
        className (am)              -- optional default value for this log record field.
        timer (am)                  -- (ElapsedTime) optional default value for this log record field.
        partnerName (ame)           -- optional default value for this log record field.
        targetEntity (me)           -- optional default value for this log record field.
        targetServiceName (me)      -- optional default value for this log record field.
        statusCode (am)             -- optional default value for this log record field.
        responseCode (am)           -- optional default value for this log record field.
        responseDescription (am)    -- optional default value for this log record field.
        processKey (am)             -- optional default value for this log record field.
        targetVirtualEntity (m)     -- optional default value for this log record field.
        customField1 (am)           -- optional default value for this log record field.
        customField2 (am)           -- optional default value for this log record field.
        customField3 (am)           -- optional default value for this log record field.
        customField4 (am)           -- optional default value for this log record field.
        errorCategory (e)           -- optional default value for this log record field.
        errorCode (e)               -- optional default value for this log record field.
        errorDescription (e)        -- optional default value for this log record field.

        Note:  the pipe '|' character is not allowed in any log record field.
        """

        self._log('FATAL', message, errorCategory = 'FATAL', **kwargs)

    def _log(self, logLevel, message, **kwargs):
        """Write a message to the log file.

        Arguments:
        logLevel          -- value ('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL', ...) for the log record.
        message           -- value for the last log record field.

        Keyword arguments: Annotations are d:debug, a=audit, m=metrics, e=error
        style                       -- the log file format (style) to use when writing log messages
        requestID (dame)            -- optional default value for this log record field.
        serviceInstanceID (am)      -- optional default value for this log record field.
        threadID (am)               -- optional default value for this log record field.
        serverName (am)             -- optional default value for this log record field.
        serviceName (am)            -- optional default value for this log record field.
        instanceUUID (am)           -- optional default value for this log record field.
        severity (am)               -- optional default value for this log record field.
        serverIPAddress (am)        -- optional default value for this log record field.
        server (am)                 -- optional default value for this log record field.
        IPAddress (am)              -- optional default value for this log record field.
        className (am)              -- optional default value for this log record field.
        timer (am)                  -- (ElapsedTime) optional default value for this log record field.
        partnerName (ame)           -- optional default value for this log record field.
        targetEntity (me)           -- optional default value for this log record field.
        targetServiceName (me)      -- optional default value for this log record field.
        statusCode (am)             -- optional default value for this log record field.
        responseCode (am)           -- optional default value for this log record field.
        responseDescription (am)    -- optional default value for this log record field.
        processKey (am)             -- optional default value for this log record field.
        targetVirtualEntity (m)     -- optional default value for this log record field.
        customField1 (am)           -- optional default value for this log record field.
        customField2 (am)           -- optional default value for this log record field.
        customField3 (am)           -- optional default value for this log record field.
        customField4 (am)           -- optional default value for this log record field.
        errorCategory (e)           -- optional default value for this log record field.
        errorCode (e)               -- optional default value for this log record field.
        errorDescription (e)        -- optional default value for this log record field.

        Note:  the pipe '|' character is not allowed in any log record field.
        """

        # timestamp will automatically be inserted
        style              = int(self._getVal('style',             '', **kwargs))
        requestID          = self._getVal('requestID',         '', **kwargs)
        serviceInstanceID  = self._getVal('serviceInstanceID', '', **kwargs)
        threadID           = self._getVal('threadID',          threading.currentThread().getName(), **kwargs)
        serverName         = self._getVal('serverName',        '', **kwargs)
        serviceName        = self._getVal('serviceName',       '', **kwargs)
        instanceUUID       = self._getVal('instanceUUID',      '', **kwargs)
        upperLogLevel      = self._noSep(logLevel.upper())
        severity           = self._getVal('severity',          '', **kwargs)
        serverIPAddress    = self._getVal('serverIPAddress',   '', **kwargs)
        server             = self._getVal('server',            '', **kwargs)
        IPAddress          = self._getVal('IPAddress',         '', **kwargs)
        className          = self._getVal('className',         '', **kwargs)
        timer              = self._getVal('timer',             '', **kwargs)
        partnerName        = self._getVal('partnerName', '', **kwargs)
        targetEntity       = self._getVal('targetEntity', '', **kwargs)
        targetServiceName  = self._getVal('targetServiceName', '', **kwargs)
        statusCode         = self._getVal('statusCode', '', **kwargs)
        responseCode       = self._getVal('responseCode', '', **kwargs)
        responseDescription = self._noSep(self._getVal('responseDescription', '', **kwargs))
        processKey          = self._getVal('processKey', '', **kwargs)
        targetVirtualEntity = self._getVal('targetVirtualEntity', '', **kwargs)
        customField1        = self._getVal('customField1', '', **kwargs)
        customField2        = self._getVal('customField2', '', **kwargs)
        customField3        = self._getVal('customField3', '', **kwargs)
        customField4        = self._getVal('customField4', '', **kwargs)
        errorCategory       = self._getVal('errorCategory', '', **kwargs)
        errorCode           = self._getVal('errorCode', '', **kwargs)
        errorDescription    = self._noSep(self._getVal('errorDescription', '', **kwargs))

        detailMessage     = self._noSep(message)
        if bool(re.match(r" *$", detailMessage)):
            return  # don't log empty messages

        useLevel = self._intLogLevel(upperLogLevel)
        if CommonLogger.verbose: print("logger STYLE=%s" % style)
        if useLevel < self._logLevelThreshold:
            if CommonLogger.verbose: print("skipping because of level")
            pass
        else:
            with self._logLock:
                if style == CommonLogger.ErrorFile:
                    if CommonLogger.verbose: print("using CommonLogger.ErrorFile")
                    self._logger.log(50, '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' \
                                     %(requestID, threadID, serviceName, partnerName, targetEntity, targetServiceName,
                                       errorCategory, errorCode, errorDescription, detailMessage))
                elif style == CommonLogger.DebugFile:
                    if CommonLogger.verbose: print("using CommonLogger.DebugFile")
                    self._logger.log(50, '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' \
                                     %(requestID, threadID, serverName, serviceName, instanceUUID, upperLogLevel,
                                       severity, serverIPAddress, server, IPAddress, className, timer, detailMessage))
                elif style == CommonLogger.AuditFile:
                    if CommonLogger.verbose: print("using CommonLogger.AuditFile")
                    endAuditTime, endAuditMsec = self._getTime()
                    if self._begTime is not None:
                        d = { 'begtime': self._begTime, 'begmsecs': self._begMsec, 'endtime': endAuditTime, 'endmsecs': endAuditMsec }
                    else:
                        d = { 'begtime': endAuditTime, 'begmsecs': endAuditMsec, 'endtime': endAuditTime, 'endmsecs': endAuditMsec }
                    self._begTime = None
                    unused = ""
                    self._logger.log(50, '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' \
                                     %(requestID, serviceInstanceID, threadID, serverName, serviceName, partnerName,
                                       statusCode, responseCode, responseDescription, instanceUUID, upperLogLevel,
                                       severity, serverIPAddress, timer, server, IPAddress, className, unused,
                                       processKey, customField1, customField2, customField3, customField4, detailMessage), extra=d)
                elif style == CommonLogger.MetricsFile:
                    if CommonLogger.verbose: print("using CommonLogger.MetricsFile")
                    endMetricsTime, endMetricsMsec = self._getTime()
                    if self._begTime is not None:
                        d = { 'begtime': self._begTime, 'begmsecs': self._begMsec, 'endtime': endMetricsTime, 'endmsecs': endMetricsMsec }
                    else:
                        d = { 'begtime': endMetricsTime, 'begmsecs': endMetricsMsec, 'endtime': endMetricsTime, 'endmsecs': endMetricsMsec }
                    self._begTime = None
                    unused = ""
                    self._logger.log(50, '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s' \
                                     %(requestID, serviceInstanceID, threadID, serverName, serviceName, partnerName,
                                       targetEntity, targetServiceName, statusCode, responseCode, responseDescription,
                                       instanceUUID, upperLogLevel, severity, serverIPAddress, timer, server, IPAddress,
                                       className, unused, processKey, targetVirtualEntity, customField1, customField2,
                                       customField3, customField4, detailMessage), extra=d)
                else:
                    print("!!!!!!!!!!!!!!!! style not set: %s" % self._fields["style"])

    def _getTime(self):
        ct = time.time()
        lt = time.localtime(ct)
        return (time.strftime(CommonLogger.DateFmt, lt), (ct - int(ct)) * 1000)

    def setStartRecordEvent(self):
        """
        Set the start time to be saved for both audit and metrics records
        """
        self._begTime, self._begMsec = self._getTime()

    def _getVal(self, key, default, **kwargs):
        val = self._fields.get(key)
        if key in kwargs: val = kwargs[key]
        if val is None: val = default
        return self._noSep(val)

    def _noSep(self, message):
        if message is None:  return ''
        return re.sub(r'[\|\n]', ' ', str(message))

    def _intLogLevel(self, logLevel):
        if   logLevel == 'FATAL':  useLevel = 50
        elif logLevel == 'ERROR':  useLevel = 40
        elif logLevel == 'WARN':   useLevel = 30
        elif logLevel == 'INFO':   useLevel = 20
        elif logLevel == 'DEBUG':  useLevel = 10
        else:                      useLevel = 0
        return useLevel

    def _mkdir_p(self, filename):
        """Create missing directories from a full filename path like mkdir -p"""

        if filename is None:
            return

        folder=os.path.dirname(filename)

        if folder == "":
            return

        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except OSError as err:
                print("error number %d creating %s directory to hold %s logfile: %s" %(err.errno, err.filename, filename, err.strerror), file=sys.stderr)
                sys.exit(2)
            except Exception as err:
                print("error creating %s directory to hold %s logfile: %s" %(folder, filename, str(err)), file=sys.stderr)
                sys.exit(2)

def __checkTime1(line):
    format = r'[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9],[0-9][0-9][0-9][+]00:00[|]'
    format = r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}[+]00:00[|]'
    m = re.match(format, line)
    if not m:
        print("ERROR: time string did not match proper time format, %s" %line)
        print("\t: format=%s" % format)
        return 1
    return 0

def __checkTime2(line, different):
    format = '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:([0-9][0-9]),([0-9][0-9][0-9])[+]00:00[|][0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:([0-9][0-9]),([0-9][0-9][0-9])[+]00:00[|]'
    format = r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:([0-9]{2}),([0-9]{3})[+]00:00[|][0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:([0-9]{2}),([0-9]{3})[+]00:00[|]'
    m = re.match(format, line)
    if not m:
        print("ERROR: time strings did not match proper time format, %s" %line)
        print("\t: format=%s" % format)
        return 1
    second1 = int(m.group(1))
    msec1 = int(m.group(2))
    second2 = int(m.group(3))
    msec2 = int(m.group(4))
    if second1 > second2: second2 += 60
    t1 = second1 * 1000 + msec1
    t2 = second2 * 1000 + msec2
    diff = t2 - t1
    # print("t1=%d (%d,%d)  t2=%d (%d,%d), diff = %d" % (t1, second1, msec1, t2, second2, msec2, diff))
    if different:
        if diff < 500:
            print("ERROR: times did not differ enough: %s" % line)
            return 1
    else:
        if diff > 10:
            print("ERROR: times were too far apart: %s" % line)
            return 1
    return 0

def __checkLog(logfile, numLines, numFields):
    lineCount = 0
    errorCount = 0
    with open(logfile, "r") as fp:
        for line in fp:
            # print("saw line %s" % line)
            lineCount += 1
            c = line.count('|')
            if c != numFields:
                print("ERROR: wrong number of fields. Expected %d, got %d: %s" % (numFields, c, line))
                errorCount += 1
            if re.search("should not appear", line):
                print("ERROR: a line appeared that should not have appeared, %s" % line)
                errorCount += 1
            elif re.search("single time", line):
                errorCount += __checkTime1(line)
            elif re.search("time should be the same", line):
                errorCount += __checkTime2(line, different=False)
            elif re.search("time should be different", line):
                errorCount += __checkTime2(line, different=True)
            else:
                print("ERROR: an unknown message appeared, %s" % line)
                errorCount += 1

    if lineCount != numLines:
        print("ERROR: expected %d lines, but got %d lines" % (numLines, lineCount))
        errorCount += 1
    return errorCount

if __name__ == "__main__":
    import os, argparse
    parser = argparse.ArgumentParser(description="test the CommonLogger functions")
    parser.add_argument("-k", "--keeplogs", help="Keep the log files after finishing the tests", action="store_true")
    parser.add_argument("-v", "--verbose", help="Print debugging messages", action="store_true")
    args = parser.parse_args()
        
    spid = str(os.getpid())
    if args.keeplogs:
        spid = ""
    logcfg = "/tmp/cl.log" + spid + ".cfg"
    errorLog = "/tmp/cl.error" + spid + ".log"
    metricsLog = "/tmp/cl.metrics" + spid + ".log"
    auditLog = "/tmp/cl.audit" + spid + ".log"
    debugLog = "/tmp/cl.debug" + spid + ".log"
    if args.verbose: CommonLogger.verbose = True

    import atexit
    def cleanupTmps():
        for f in [ logcfg, errorLog, metricsLog, auditLog, debugLog ]:
            try:
                os.remove(f)
            except:
                pass
    if not args.keeplogs: 
        atexit.register(cleanupTmps)

    with open(logcfg, "w") as o:
        o.write("error = " + errorLog + "\n" +
                "errorLogLevel   = WARN\n" +
                "metrics = " + metricsLog + "\n" +
                "metricsLogLevel = INFO\n" +
                "audit = " + auditLog + "\n" +
                "auditLogLevel   = INFO\n" +
                "debug = " + debugLog + "\n" +
                "debugLogLevel   = DEBUG\n")

    import uuid
    instanceUUID = uuid.uuid1()
    serviceName = "testharness"
    errorLogger = CommonLogger(logcfg, "error", style=CommonLogger.ErrorFile, instanceUUID=instanceUUID, serviceName=serviceName)
    debugLogger = CommonLogger(logcfg, "debug", style=CommonLogger.DebugFile, instanceUUID=instanceUUID, serviceName=serviceName)
    auditLogger = CommonLogger(logcfg, "audit", style=CommonLogger.AuditFile, instanceUUID=instanceUUID, serviceName=serviceName)
    metricsLogger = CommonLogger(logcfg, "metrics", style=CommonLogger.MetricsFile, instanceUUID=instanceUUID, serviceName=serviceName)

    testsRun = 0
    errorCount = 0
    errorLogger.debug("error calling debug (should not appear)")
    errorLogger.info("error calling info (should not appear)")
    errorLogger.warn("error calling warn (single time)")
    errorLogger.error("error calling error (single time)")
    errorLogger.setStartRecordEvent()
    time.sleep(1)
    errorLogger.fatal("error calling fatal, after setStartRecordEvent and sleep (start should be ignored, single time)")
    testsRun += 6
    errorCount += __checkLog(errorLog, 3, 10)

    auditLogger.debug("audit calling debug (should not appear)")
    auditLogger.info("audit calling info (time should be the same)")
    auditLogger.warn("audit calling warn (time should be the same)")
    auditLogger.error("audit calling error (time should be the same)")
    auditLogger.setStartRecordEvent()
    time.sleep(1)
    auditLogger.fatal("audit calling fatal, after setStartRecordEvent and sleep, time should be different)")
    testsRun += 6
    errorCount += __checkLog(auditLog, 4, 25)

    debugLogger.debug("debug calling debug (single time)")
    debugLogger.info("debug calling info (single time)")
    debugLogger.warn("debug calling warn (single time)")
    debugLogger.setStartRecordEvent()
    time.sleep(1)
    debugLogger.error("debug calling error, after SetStartRecordEvent and sleep (start should be ignored, single time)")
    debugLogger.fatal("debug calling fatal (single time)")
    errorCount += __checkLog(debugLog, 5, 13)
    testsRun += 6

    metricsLogger.debug("metrics calling debug (should not appear)")
    metricsLogger.info("metrics calling info (time should be the same)")
    metricsLogger.warn("metrics calling warn (time should be the same)")
    metricsLogger.setStartRecordEvent()
    time.sleep(1)
    metricsLogger.error("metrics calling error, after SetStartRecordEvent and sleep, time should be different")
    metricsLogger.fatal("metrics calling fatal (time should be the same)")
    testsRun += 6
    errorCount += __checkLog(metricsLog, 4, 28)

    print("%d tests run, %d errors found" % (testsRun, errorCount))
