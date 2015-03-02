import os
import re
import gzip
from datetime import datetime, timedelta

from config.constants import *
from logger import mlogger as logger
from config.config import DIR_LOG, DIR_LOGOLD, search_items

# Check if the line accord with the condition
def check_line(line, condition_dict):
    flag = 0
    if not condition_dict:
        return True
    for key in condition_dict:
        for condition in condition_dict[key]:
            if condition in line:
                flag = 1
                break
        if flag == 0:
            return False
        else:
            flag = 0

    return True

# Compare time
def time_cmp(starttime, endtime):
    try:
        starttime = datetime.strptime(starttime, \
                                  TIME_FORMAT_MS)
        endtime = datetime.strptime(endtime, \
                                  TIME_FORMAT_MS)
    except:
        logger.exception('Format time error...' + endtime)
        return False

    return endtime - starttime

def get_value(regex, string):
    ret = re.findall(regex, string)
    if ret:
        return ret[0]
    return None

class LogFileAnalysis(object):
    def __init__(self, item):
        if item not in search_items:
            return False

        self.logmodule = search_items[item]['logmodule']
        self.condition = search_items[item]['condition']
        self.flag = search_items[item]['flag']

    # Get needed log file list
    @staticmethod
    def get_logfile_list(starttime, endtime, logmodule):
        lists = os.listdir(DIR_LOGOLD)
        lists = [name for name in lists if logmodule in name]
        lists.sort()
        loglist = []
        
        # Format string time
        def format_time(name)
            time = get_value(REG_LF_TIME, name)
            if not time:
                return False
            try:
                time = datetime.strptime(time, TIME_FORMAT_LF)
            except:
                logger.exception('Format time error...')
                False

            return time

        # Find proper log files from DIR_LOGOLD
        for name in lists:
            time = format_time(name)
            if not time:
                continue
            
            if time > starttime and time <= endtime:
                loglist.append(name)
            elif time > endtime:
                loglist.append(name)
                break

        # Find proper log file from DIR_LOG
        time = format_time(lists[-1])
        if not time:
            return loglist
        if endtime >= time:
            loglist.append(logmodule + '.log')

        return loglist

    # Get related log line from logfile according to time
    @staticmethod
    def get_log_lines(starttime, endtime, logfile):
        loglines = []
        # Open log file
        if logfile[-2:] == 'gz':
            try:
                path = os.path.join(DIR_LOGOLD, logfile)
                with gzip.open(path, 'rb') as filetext:
                    lines = filetext.readlines()
            except:
                return loglines
        else:
            try:
                path = os.path.join(DIR_LOG, logfile)
                with open(path, 'rb') as filetext:
                    lines = filetext.readlines()
            except:
                return loglines

        if 'homerServerDaemon' not in logfile:
            try:
                # Get first line's time and last line's time
                front = 0
                tail = len(lines)-1
                while(front < len(lines)):
                    try:
                        file_starttime = \
                            datetime.strptime(lines[front][0:19], TIME_FORMAT)
                        break
                    except:
                        front = front + 1
                        continue
                while(tail > 0):
                    try:
                        file_endtime = \
                            datetime.strptime(lines[tail][0:19], TIME_FORMAT)
                        break
                    except:
                        tail = tail - 1
                        continue
                if file_starttime >= starttime and \
                   file_endtime <= endtime:
                    loglines.extend(lines)
                elif file_starttime > endtime or \
                    file_endtime < starttime:
                    return loglines
                else:
                    for line in lines:
                        try:
                            time = datetime.strptime(line[0:19], TIME_FORMAT)
                            if time >= starttime and time <= endtime:
                                loglines.append(line)
                        except:
                            continue
            except:
                logger.exception('Format time error...')

        else:
            i = 0
            while i < len(lines):
                if 'CST' in lines[i]:
                    try:
                        logtime = datetime.strptime(lines[i][:-1], \
                                                    TIME_FORMAT_CST)
                        if logtime > starttime and logtime < endtime:
                            strtime = logtime.strftime(TIME_FORMAT_MS)
                            if 'Stop:' in lines[i+1] or 'Start:' in lines[i+1]:
                                if 'server: Succeeded' in lines[i+3]:
                                    loglines.append(strtime + '|' + lines[i+1][:-2] + '\n')
                                    i = i + 3
                            elif 'Restart:' in lines[i+1]:
                                if 'server: Succeeded' in lines[i+5]:
                                    linelines.append(strtime + '|' + lines[i+1][:-2] + '\n')
                                    i = i+5
                        i = i + 1
                    except:
                        i = i + 1
                        continue
                else:
                    i = i + 1

        return loglines

    # Get relate info from log file
    def log_analysis(self, logline):
        error_con = { 'first' : ['Discarding', 'Not Processing', \
                                  'Error Spawning', 'Cannot Process', \
                                  'Error Processing'] }

        line_list = []
        for i in range(0, len(logline)):
            if check_line(logline[i], self.condition):
                # Get time
                time = get_value(REG_TIME, logline[i])
                if not time:
                    continue

                if self.flag == FLAG_DEV_LOGINCONN:
                    if "Close Connection:" in logline[i] or \
                       "Connection Closed:" in logline[i]:
                        connid = logline[i].split(" ")[-1].replace("\n", "")

                        # Define time interval 500ms
                        time_interval = timedelta(0, 0, 500000)
                        k = i-1
                        # Confirm the logline is logout or disconnected
                        while k >= 0:
                            time_check = get_value(REG_TIME, logline[k])
                            if not time_check:
                                k = k - 1
                                continue
                            ret = time_cmp(time_check, time)
                            if not ret:
                                break
                            if ret <= time_interval:
                                if 'Received (' + connid + '): PUSHINFO with' in logline[k] and \
                                   '\'OPTION\': 1' in logline[k]:
                                    line_list.append(time + '|' + connid + '|Logout\n')
                                    break
                            if ret > time_interval:
                                line_list.append(time + '|' + connid + '|Disconnected\n')
                                break
                            k = k - 1
                    else:
                        connid = get_value(REG_CONNID, logline[i])
                        version = get_value(REG_VERSION, logline[i])
                        mac = get_value(REG_MAC, logline[i])
                        # Make sure no value is None
                        if not (connid and version and mac):
                            continue
                        conn_close = 'Connection Closed: ' + connid
                        close_conn = 'Close Connection: ' + connid
                        error_con['first'].append('REJECT with')
                        error_con['second'] = [connid]

                        did_con = {'first'  : ['Start Processing'],
                                   'second' : ['PUSHINFO', 'DO', 'ALARM', 'MODIFY', 'SCENE']
                                  }
                        did_con['third'] = [connid]
                        
                        def line_list_append():
                            if 'INIT with' in logline[i]:
                                line_list.append(time + '|' + connid + '|' + did + \
                                                '|' + mac + '|' + version + '|Login\n')
                            else:
                                line_list.append(time + '|' + connid + '|' + did + \
                                                '|' + mac + '|' + version + '|Connected\n')

                        k = i+1
                        while k < len(logline):
                            # REJECT or error
                            if check_line(logline[k], error_con):
                                break
                            # Connection closed
                            elif close_conn in logline[k] or \
                               conn_close in logline[k]:
                                did = ''
                                line_list_append()
                                break
                            elif check_line(logline[k], did_con):
                                did = get_value(REG_DID, logline[k])
                                if not did:
                                    did = ''
                                line_list_append()
                                break
                            k = k + 1

                elif self.flag == FLAG_HOST_AUTHFAIL:
                    connid = get_value(REG_CONNID, logline[i])
                    hostid = get_value(REG_HID, logline[i])
                    # Make sure no value is None
                    if not (connid and hostid):
                        continue
                    close_conn = 'Close Connection: ' + connid
                    conn_close = 'Connection Closed: ' + connid
                    error_con['first'].append('REJECT with')
                    error_con['second'] = [connid]
                    for j in range(i+1, len(logline)):
                        if  'Sent (' + connid + '): OK with' in logline[j] or \
                            close_conn in logline[j] or \
                            conn_close in logline[j]:
                            break
                        elif check_line(logline[j], error_con):
                            line_list.append(time + '|' + hostid + '\n')
                            break

                elif self.flag == FLAG_DEV_AUTHFAIL:
                    connid = get_value(REG_CONNID, logline[i])
                    mac = get_value(REG_MAC, logline[i])
                    if not (connid and mac):
                        continue
                    close_conn = 'Close Connection: ' + connid
                    conn_close = 'Connection Closed: ' + connid
                    error_con['first'].append('REJECT with')
                    error_con['second'] = [connid]
                    for j in range(i+1, len(logline)):
                        # If find 'OK' or connectionn closed than break
                        if 'Sent (' + connid + '): OK with' in logline[j] or \
                           close_conn in logline[j] or \
                           conn_close in logline[j]:
                            break
                        elif check_line(logline[j], error_con):
                            line_list.append(time + '|' + mac + '\n')
                            break

                elif self.flag == FLAG_DEV_DOOP:
                    connid = get_value(REG_CONNID, logline[i])
                    # The value of sid_aid is sid or aid
                    sid_aid = get_value(REG_SIDAID, logline[i])
                    oid = get_value(REG_OID, logline[i])
                    doargs = get_value(REG_DOARGS, logline[i])
                    threadid = get_value(REG_THREADID, logline[i])
                    # Make sure no value is None
                    if not (connid and sid_aid and oid and \
                            doargs and threadid):
                        continue
                    conn_close = 'Connection Closed: ' + connid
                    close_conn = 'Close Connection: ' + connid
                    error_con['first'].append('FAIL with')
                    error_con['second'] = [connid]
                    # Find did
                    for j in range(i+1, len(logline)):
                        # If find error msg or connection closed than break
                        if check_line(logline[j], error_con) or \
                           close_conn in logline[j] or \
                           conn_close in logline[j]:
                            break
                        elif 'Start Processing (' + connid + '): DO' in logline[j]:
                            did = get_value(REG_DID, logline[j])
                            if not did:
                                continue
                            line_list.append(time + '|' + did + '|' + \
                                            threadid + '|' + doargs + '\n')
                            break

                elif self.flag == FLAG_DEV_SCENEOP:
                    connid = get_value(REG_CONNID, logline[i])
                    threadid = get_value(REG_THREADID, logline[i])
                    sceneargs = get_value(REG_SCENEARGS, logline[i])
                    # Make sure no value is None
                    if not (connid and threadid and \
                            sceneargs):
                        continue
                    close_conn = 'Close_Connection: ' + connid
                    conn_close = 'Connection Closed: ' + connid
                    error_con['first'].append('SCENEFAIL with')
                    error_con['second'] = [connid]
                    # Find did
                    for j in range(i+1, len(logline)):
                        # If find error msg or connection closed than break
                        if close_conn in logline[j] or \
                           conn_close in logline[j] or\
                           check_line(logline[j], error_con):
                            break
                        elif 'Start Processing (' + connid + '): SCENE' in logline[j]:
                            did = get_value(REG_DID, logline[j])
                            if not did:
                                continue
                            line_list.append(time + '|' + did + '|' + \
                                             threadid + '|' + sceneargs + '\n')
                            break

                elif self.flag == FLAG_DEV_ALARMOP:
                    connid = get_value(REG_CONNID, logline[i])
                    alarmargs = get_value(REG_ALARMARGS, logline[i])
                    threadid = get_value(REG_THREADID, logline[i])
                    # Make sure no value is None
                    if not (connid and alarmargs and \
                            threadid):
                        continue
                    conn_close = 'Connection Closed: ' + connid
                    close_conn = 'Close_Connection: ' + connid
                    error_con['first'].append('ALARMFAIL with')
                    error_con['second'] = [connid]
                    # Find did
                    for j in range(i+1, len(logline)):
                        # If find error msg or connection closed than break
                        if check_line(logline[j], error_con) or \
                           close_conn in logline[j] or\
                           conn_close in logline[j]:
                            break
                        elif 'Start Processing (' + connid + '): ALARM' in logline[j]:
                            did = get_value(REG_DID, logline[j])
                            if not did:
                                continue
                            line_list.append(time + '|' + did + '|' + \
                                             threadid + '|' + alarmargs + '\n')
                            break

                elif self.flag == FLAG_DEV_MODIFYOP:
                    connid = get_value(REG_CONNID, logline[i])
                    modifyargs = get_value(REG_MODIFYARGS, logline[i])
                    threadid = get_value(REG_THREADID, logline[i])
                    if not (connid and modifyargs and \
                            threadid):
                        continue
                    close_conn = 'Close_Connection: ' + connid
                    conn_close = 'Connection Closed: ' + connid
                    error_con['first'].append('MODIFYFAIL with')
                    # Find did
                    for j in range(i+1, len(logline)):
                        # If find error msg or connection closed than break
                        if close_conn in logline[j] or \
                           conn_close in logline[j] or \
                           check_line(logline[j], error_con):
                            break
                        elif 'Start Processing (' + connid + '): MODIFY' in logline[j]:
                            did = get_value(REG_DID, logline[j])
                            if not did:
                                continue
                            line_list.append(time + '|' + did + '|' + \
                                             threadid + '|' + modifyargs + '\n')
                            break

                elif self.flag == FLAG_APP_STATUSCHANGE:
                    connid = get_value(REG_CONNID, logline[i])
                    if not connid:
                        continue
                    open_conn = 'Open ' + connid

                    if 'DONE with' in logline[i]:
                        oid = get_value(REG_OID, logline[i])
                        if not oid:
                            continue
                        # Get aid
                        aid = get_value(REG_AID, logline[i])
                        # Log line without aid
                        # Find 'DO with' to get aid
                        if not aid:
                            j = i - 1
                            while j >= 0:
                                if 'Received (' + connid + '): DO with' in logline[j] and \
                                   oid in logline[j] and \
                                   'AID' in logline[j]:
                                    aid = get_value(REG_AID, logline[j])
                                    break
                                elif 'open_conn' in logline[j]:
                                    break
                                j = j - 1
                    #'RELAY with'
                    else:
                        # Get aid
                        aid = get_value(REG_AID, logline[i])

                    if not aid:
                        continue

                    # Get STATUS value
                    status = get_value(REG_STATUS, logline[i])
                    if not status:
                        continue
                    # Makesure no same status in line_list
                    status_exist = False
                    for line in line_list:
                        if status in line:
                            status_exist = True
                            break
                    if not status_exist:
                        line_list.append(time + '|' + aid + '|' + status + '\n')

                elif self.flag == FLAG_IP_OPEN:
                   '''
                    connid = logline[i].split(' ')[-1].replace('\n', '')
                    if i+1 < len(logline):
                        connid1 = get_value(REG_CONNID, logline[i+1])
                        if connid1 and connid1 == connid:
                            line_list.append(logline[i])
                            line_list.append(logline[i+1])
                    '''
                    ip = get_value(REG_IP, logline[i])
                    if not ip:
                        continue
                    line_list.append(time + '|' + ip + '\n')
                else:
                    line_list.append(logline[i])

        return line_list
