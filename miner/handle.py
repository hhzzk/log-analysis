import re

from cache import CacheFile
from config.constants import REG_REMOVE_U, REG_NETWORK
from logger import mlogger as logger

__all__ = ('handle_host_netstatus', 'handle_host_authfailtimes', \
           'handle_app_netstatus', 'handle_app_statuschange', \
           'handle_dev_loginconn', 'handle_dev_authfailtimes', \
           'handle_dev_doop', 'handle_dev_sceneop', 'handle_dev_alarmop', \
           'handle_dev_modifyop', 'handle_server_statuschange', \
           'handle_server_servererror', 'handle_ip_open', \
           'handle_server_dberror', 'handle_server_debugerror'
           )

def handle_host_netstatus(info_list, optionid):
    display = {}

    if not info_list:
        return display

    # Create display
    for line in info_list:
        hid = line.split(' ')[-1].replace('\n', '')
        if optionid != '' and optionid != hid:
            continue
        time = line[0:23]
        if 'Connected' in line:
            info = 'Connected'
        elif 'Disconnected' in line:
            info = 'Disconnected'
        if hid in display:
            display[hid][time] = info
        else:
            display[hid] = {time : info}

    return display

def handle_host_authfailtimes(info_list, optionid):
    temp_list = []
    display = {}

    if not info_list:
        return display

    for info in info_list:
        hid = info.split('|')[1].replace('\n', '')
        if optionid != '' and optionid != hid:
            continue
        temp_list.append(hid)

    for hid in temp_list:
        if hid not in display:
            display[hid] = temp_list.count(hid)
        else:
            continue

    return display

def handle_app_netstatus(info_list, optionid):
    display = {}
    networks = ['Connected', 'Initalizing', 'Connecting', \
                'Disconnected', 'Maintenance']

    if not info_list:
        return display

    for i in range(0, len(info_list)):
        time, aid, status = info_list[i].split('|')
        if optionid != '' and optionid != aid:
            continue
        try:
            network = re.findall(REG_NETWORK, status)[0]
        except:
            continue
        msg = networks[int(network)]
        if aid in display:
            dic = display[aid]
            if msg != dic[sorted(dic.keys())[-1]]:
                display[aid][time] = msg
        else:
            display[aid] = { time : msg }

    return display

def handle_app_statuschange(info_list, optionid):
    display = {}

    if not info_list:
        return display

    for info in info_list:
        time, aid, status = info.split('|')
        if optionid != '' and optionid != aid:
            continue
        # Change string to dict
        status = re.sub(REG_REMOVE_U, '\'', status)
        status = eval(status)['STATUS']
        if aid not in display:
            display[aid] = {time : status}
            continue
        # Makesure no same status
        dic =  display[aid]
        status_exist = False
        for key in dic:
            if not cmp(dic[key], status):
                status_exist = True
                break
        if not status_exist:
            display[aid][time] = status

    return display

def handle_dev_loginconn(info_list, optionid, startver, endver):
    display = {}
    if not info_list:
        return display

    def get_close_info(connid):
        for info in info_list:
            if connid in info and \
               ('Logout' in info or \
               'Disconnecte' in info):
                infosplit = info.split('|')
                return infosplit[0], infosplit[2]
        return None, None

    for info in info_list:
        if 'Login' in info or \
           'Connected' in info:
            open_time, connid, did, mac, version, open_msg \
                            = info.split('|')
            if optionid != '' and optionid != mac:
                continue

            close_time, close_msg = get_close_info(connid)
            open_msg = open_msg.replace('\n', '')
            if version >= startver and version <= endver:
                if mac in display:
                    display[mac][open_time] = open_msg
                else:
                    display[mac] = { open_time : open_msg }
                if close_msg:
                    display[mac][close_time] = close_msg.replace('\n', '')
    return display

def handle_dev_authfailtimes(info_list, optionid):
    temp_list = []
    display = {}

    if not info_list:
        return display

    for info in info_list:
        mac = info.split('|')[1].replace('\n', '')
        if optionid != '' and optionid != mac:
            continue
        temp_list.append(mac)

    for mac in temp_list:
        if mac not in display:
            display[mac] = temp_list.count(mac)
        else:
            continue

    return display

# Generate map of did to mac
# Use cache file dev_loginconn
def generate_did_mac():
    did_mac = {}
    cache = CacheFile('dev_loginconn')
    cache.generate_cache()

    try:
        with open(cache.cachefile, 'r') as cachefile:
            lines = cachefile.readlines()
    except:
        return did_mac
    for line in lines:
        if 'Login' in line or \
           'Connected' in line:
            open_time, connid, did, mac, version, open_msg \
                            = line.split('|')
            # Check did, did can be '' 
            if did:
                did_mac[did] = mac
    return did_mac

def handle_dev_doop(info_list, optionid):
    display = {}

    if not info_list:
        return display

    did_mac = generate_did_mac()
    for info in info_list:
        time, did, threadid, doargs \
                    = info.split('|', 3)

        try:
            mac = did_mac[did]
        except:
            continue
        if not mac:
            continue

        if optionid != '' and optionid != mac:
            continue
        # Change string to dict
        doargs = re.sub(REG_REMOVE_U, '\'', doargs)
        doargs = eval(doargs)
        doargs['THREADID'] = threadid
        del doargs['OID']
        if mac in display:
            display[mac][time] = doargs
        else:
            time_dict = {time : doargs}
            display[mac] = time_dict

    return display

def handle_dev_sceneop(info_list, optionid):
    display = {}

    if not info_list:
        return display

    did_mac = generate_did_mac()
    for info in info_list:
        time, did, threadid, sceneargs \
                        = info.split('|', 3)
        try:
            mac = did_mac[did]
        except:
            continue
        if not mac:
            continue

        if optionid != '' and optionid != mac:
            continue
        # Change string to dict
        sceneargs = re.sub(REG_REMOVE_U, '\'', sceneargs)
        sceneargs = eval(sceneargs)
        sceneargs['THREADID'] = threadid
        del sceneargs['OID']
        if mac in display:
            display[mac][time] = sceneargs
        else:
            time_dict = {time : sceneargs}
            display[mac] = time_dict

    return display

def handle_dev_alarmop(info_list, optionid):
    display = {}

    if not info_list:
        return display

    did_mac = generate_did_mac()
    for info in info_list:
        time, did, threadid, alarmargs \
                        = info.split('|', 3)

        try:
            mac = did_mac[did]
        except:
            continue
        if not mac:
            continue

        if optionid != '' and optionid != mac:
            continue
        # Change string to dict
        alarmargs = re.sub(REG_REMOVE_U, '\'', alarmargs)
        alarmargs = eval(alarmargs)
        alarmargs['THREADID'] = threadid
        del alarmargs['OID']
        if mac in display:
            display[mac][time] = alarmargs
        else:
            time_dict = {time : alarmargs}
            display[mac] = time_dict

    return display

def handle_dev_modifyop(info_list, optionid):
    display = {}

    if not info_list:
        return display

    did_mac = generate_did_mac()
    for info in info_list:
        time, did, threadid, modifyargs \
                    = info.split('|', 3)
        try:
            mac = did_mac[did]
        except:
            continue
        if not mac:
            continue

        if optionid != '' and optionid != mac:
            continue
        # Change string to dict
        modifyargs = re.sub(REG_REMOVE_U, '\'', modifyargs)
        modifyargs = eval(modifyargs)
        modifyargs['THREADID'] = threadid
        if mac in display:
            display[mac][time] = modifyargs
        else:
            time_dict = {time : modifyargs}
            display[mac] = time_dict

    return display

def handle_ip_open(info_list, optionid):
    temp_list = []
    display = {}

    if not info_list:
        return display

    for info in info_list:
        ip = info.split('|')[1].replace('\n', '')
        if optionid != '' and optionid != did:
            continue
        temp_list.append(ip)

    for ip in temp_list:
        if ip not in display:
            display[ip] = temp_list.count(ip)
        else:
            continue

    return display

def handle_server_statuschange(info_list, optionid=None):
    display = {}

    if not info_list:
        return display

    for info in info_list:
        time, msg = info.split('|')
        display[time] = msg.replace('\n', '')

    return display

def handle_server_servererror(info_list, optionid=None):
    display  = {}

    for info in info_list:
        time = info[0:23]
        if 'WARNING' in info:
            msg = info[info.index('WARNING'):].replace('\n', '')
        elif 'EXCEPTION' in line:
            msg = info[info.index('EXCEPTION:'):].replace('\n', '')

        display[time] = msg

    return display

def handle_server_dberror(info_list, optionid=None):
    display  = {}

    for info in info_list:
        time = info[0:23]
        if 'WARNING' in info:
            msg = info[info.index('WARNING'):].replace('\n', '')
        elif 'EXCEPTION' in line:
            msg = info[info.index('EXCEPTION:'):].replace('\n', '')

        display[time] = msg

    return display

def handle_server_debugerror(info_list, optionid=None):
    display  = {}

    for info in info_list:
        time = info[0:23]
        if 'WARNING' in info:
            msg = info[info.index('WARNING'):].replace('\n', '')
        elif 'EXCEPTION' in line:
            msg = info[info.index('EXCEPTION:'):].replace('\n', '')

        display[time] = msg

    return display

