FLAG_HOST_NETSTATUS       = 1
FLAG_HOST_AUTHFAIL        = 2
FLAG_APP_NETSTATUS        = 3
FLAG_APP_STATUSCHANGE     = 4
FLAG_DEV_LOGINCONN        = 5
FLAG_DEV_AUTHFAIL         = 6
FLAG_DEV_DOOP             = 7
FLAG_DEV_ALARMOP          = 8
FLAG_DEV_MODIFYOP         = 9
FLAG_DEV_SCENEOP          = 10
FLAG_IP_OPEN              = 11
FLAG_SERVER_STATUSCHANGE  = 12
FLAG_SERVER_SERVERERROR   = 13
FLAG_SERVER_DBERROR       = 14
FLAG_SERVER_DEBUGERROR    = 15

# Define some regular expression
# used to get relate value
REG_CONNID   = r'\(([-a-z0-9]*)\)'
REG_SIDAID   = r'\'[SA]{1}ID\': u?\'([-a-z0-9]*)\''
REG_SID      = r'\'SID\': u?\'([-a-z0-9]*)\''
REG_AID      = r'\'AID\': u?\'([-a-z0-9]*)\''
REG_MAC      = r'\'MAC\': u?\'([a-z0-9]*)\''
REG_IP       = r'@ ([.\d]+)'
REG_OP       = r'\'OP\': (\d+)'
REG_SOP      = r'\'SOP\': (\d+)'
REG_WHEN     = r'\'WHEN\': (\d+)'
REG_NETWORK  = r'\'Network\': (\d)'
REG_OID      = r'\'OID\': u?\'([-a-z0-9]*)\''
REG_OPARGS   = r'\'OPARGS\': ({.*?})'
REG_STATUS   = r' ({.*})'
REG_THREADID = r' - ([0-9]{15}) - '
REG_DID      = r'\[([-a-z0-9]*)\]'
REG_VERSION  = r'\'VER\': u?\'([.0-9]*|VERSION)\''
REG_HID      = r'\'HID\': u?\'([-a-z0-9]*)\''
REG_ALID     = r'\'ALID\': u?\'([-a-z0-9]*)\''
REG_REMOVE_U = r'u\'(?=\w+)'
REG_DOARGS   = r'DO with ({.*})'
REG_SCENEARGS = r'SCENE with ({.*})'
REG_ALARMARGS = r'ALARM with ({.*})'
REG_MODIFYARGS = r'MODIFY with ({.*})'
REG_LF_TIME = r'(\d{4}-\d{2}-\d{2}-\d{2}:\d{2}:\d{2})'
REG_TIME = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})'

# Time format
TIME_FORMAT     = '%Y-%m-%d %H:%M:%S'
TIME_FORMAT_LF  = '%Y-%m-%d-%H:%M:%S'
TIME_FORMAT_MS  = '%Y-%m-%d %H:%M:%S,%f'
TIME_FORMAT_CST = '%a %b %d %H:%M:%S CST %Y'
