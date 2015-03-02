import sys
import os
import time
from datetime import datetime
from sys import path
path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from config.constants import TIME_FORMAT
from miner.handle import *
from miner.cache import CacheFile
from config.config import IS_DIVISION_RETURN, \
                          MAX_HANDLE_LINES


# From miner import SearchHandler
test_case = {   'host'   : ['netstatus', 'authfailtimes'],
                'app'    : ['netstatus', 'statuschange'],
                'dev'    : ['loginconn', 'authfailtimes', \
                            'doop', 'sceneop', 'alarmop', \
                            'modifyop'],
                'server' : ['statuschange', 'servererror', \
                            'dberror', 'debugerror'],
                'ip'     : ['open']
            }

def get_option():
    for option in test_case:
        print (option)
    option = raw_input('Please choose search option:')

    if option not in test_case:
        return get_option()

    return option

def get_context(option):
    for context in test_case[option]:
        print(context)

    context = raw_input('Please choose search context:')

    if context not in test_case[option]:
        return get_context(option)

    return context

def get_starttime():
    starttime = raw_input('Please input start time(format:2014-06-06 01:01:01):')

    try:
        datetime.strptime(starttime, TIME_FORMAT)
    except:
        return get_starttime()

    return starttime

def get_endtime():
    endtime = raw_input('Please input end time(empty means now,format:2014-06-06 01:01:01):')

    if not endtime:
        endtime = datetime.now()
        endtime = datetime.strftime(endtime, TIME_FORMAT)
        return endtime

    try:
        datetime.strptime(endtime, TIME_FORMAT)
    except:
        return get_endtime()

    return endtime

def get_arguments():

    option = get_option()
    context = get_context(option)
    starttime = get_starttime()
    endtime = get_endtime()
    optionid = raw_input('Please input option id(can be empty):')
    startver = ''
    endver = ''

    name = option + '_' + context
    args = {
        'starttime' : starttime,
        'endtime'   : endtime,
        'optionid'  : optionid,
        'startver'  : startver,
        'endver'    : endver
    }

    return name, args

def get_data(name, args):
    data = {}
    # Get and format time
    try:
        starttime = datetime.strptime(args['starttime'], TIME_FORMAT)
        endtime = datetime.strptime(args['endtime'], TIME_FORMAT)
    except:
        logger.exception('Time format error')
        return False

    if 'optionid' in args:
        optionid = args['optionid']
    else:
        optionid = ''

    # Get info list from cache file
    cache_obj = CacheFile(name)
    if cache_obj.endtime_obj < endtime:
        cache_obj.generate_cache()

    info_list = cache_obj.require_from_cachefile(starttime, endtime)
    # info list is empty
    if not info_list:
        data['FIN'] = True
        data['args'] ={}

        return data

    max_handle_lines = MAX_HANDLE_LINES
    if not IS_DIVISION_RETURN:
        max_handle_lines = len(info_list)

    # Split info_list
    sub_info_list = [info_list[i:i+max_handle_lines] \
                    for i in range(0, len(info_list), max_handle_lines)]

    for i in range(len(sub_info_list)):
        # Call handler function
        func_name = 'handle_' + name
        if name == 'dev_loginconn':
            startver = args['startver']
            endver = args['endver']
            display = handle_dev_loginconn(sub_info_list[i], optionid, \
                                            startver, endver)
        else:
            display = eval(func_name)(sub_info_list[i], optionid)

        # Add data finish flag
        if i != len(sub_info_list)-1:
            data['FIN'] = False
        else:
            data['FIN'] = True
        data['args'] = display

    return data

def start():
    name, args = get_arguments()

    print 'Begin to test ' + name + '...'
    begin = time.time()
    print str(begin)

    data = get_data(name, args)

    end = time.time()
    print str(end)
    print 'Test finish and use ' + str(end-begin)

if __name__ == '__main__':
    start()
