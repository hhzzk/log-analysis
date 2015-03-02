from os import path as _path

from constants import FLAG_HOST_NETSTATUS, FLAG_HOST_AUTHFAIL, \
                      FLAG_APP_NETSTATUS, FLAG_APP_STATUSCHANGE, \
                      FLAG_DEV_LOGINCONN, FLAG_DEV_AUTHFAIL, \
                      FLAG_DEV_DOOP, FLAG_DEV_ALARMOP, \
                      FLAG_DEV_MODIFYOP, FLAG_DEV_SCENEOP, \
                      FLAG_IP_OPEN, FLAG_SERVER_STATUSCHANGE, \
                      FLAG_SERVER_SERVERERROR, FLAG_SERVER_DBERROR, \
                      FLAG_SERVER_DEBUGERROR

# Log position
DIR_LOG    = '/var/log'
DIR_LOGOLD = '/var/log.old'

# PATH related
CUR_PATH = _path.dirname(_path.dirname(_path.realpath(__file__)))
CACHE_PATH = _path.join(CUR_PATH, 'cache')

CACHE_CREATATION_TIME = 'cache_time.conf'
# Cache file update time (second)
CACHE_UPDATE_TIME = 30
port = 9999

# Log configuration
MINER_LOGS            = '/var/log/'
MINER_OLD_LOGS        = '/var/log.old/'
MINER_LOG_NAME        = 'miner'
MINER_LOG_FILE        = MINER_LOGS + 'homerMiner.log'
LOG_BACKUP_COUNT      = 20
MAX_LOG_SIZE          = 1024 * 1024 * 5

# Whether to split returned data
IS_DIVISION_RETURN = False
MAX_HANDLE_LINES = 200

'''
search_items = ('handle_host_netstatus', 'handle_host_authfailtimes', \
                'handle_app_netstatus', 'handle_app_statuschange', \
                'handle_dev_loginconn', 'handle_dev_authfailtimes', \
                'handle_dev_doop', 'handle_dev_sceneop', 'handle_dev_alarmop', \
                'handle_dev_modifyop', 'handle_server_statuschange', \
                'handle_server_error', 'handle_ip_open', 'handle_expansion')
'''
search_items =  {'host_netstatus'      : {'logmodule' : 'homerServer',
                                          'condition' : {'first' : ['Host Disconnected', \
                                                                       'Host Connected']
                                                        },
                                          'flag'      : FLAG_HOST_NETSTATUS
                                         },
                 'host_authfailtimes'  : {'logmodule' : 'homerServer',
                                          'condition' : {'first' : ['SETUP with']},
                                          'flag'      : FLAG_HOST_AUTHFAIL
                                         },
                 'app_netstatus'       : {'logmodule' : 'homerServer',
                                          'condition' : {'first'  : ['DONE with'],
                                                         'second' : ['AID'],
                                                         'third'  : ['Network']
                                                        },
                                          'flag'      : FLAG_APP_NETSTATUS
                                         },
                 'app_statuschange'    : {'logmodule' : 'homerServer',
                                          'condition' : {'first'  : ['DONE with', 'RELAY with'],
                                                         'second' : ['STATUS']
                                                        },
                                          'flag'      : FLAG_APP_STATUSCHANGE
                                         },
                 'dev_loginconn'       : {'logmodule' : 'homerServer',
                                          'condition' : {'first' : ['INIT with',
                                                                    'AUTH with',
                                                                    'Connection Closed',
                                                                    'Close Connection']
                                                        },
                                          'flag'      : FLAG_DEV_LOGINCONN
                                         },
                 'dev_authfailtimes'   : {'logmodule' : 'homerServer',
                                          'condition' : {'first' : ['INIT with', 'AUTH with']},
                                          'flag'      : FLAG_DEV_AUTHFAIL
                                         },
                 'dev_doop'            : {'logmodule' : 'homerServer',
                                          'condition' : {'first'  : ['DO with'],
                                                         'second' : ['AID', 'SID'],
                                                         'third'  : ['OID'],
                                                         'fourth' : ['OP']
                                                        },
                                          'flag'      : FLAG_DEV_DOOP
                                         },
                 'dev_sceneop'         : {'logmodule' : 'homerServer',
                                          'condition' : {'first' : ['SCENE with']},
                                          'flag'      : FLAG_DEV_SCENEOP
                                         },
                 'dev_modifyop'        : {'logmodule' : 'homerServer',
                                          'condition' : {'first' : ['MODIFY with']},
                                          'flag'      : FLAG_DEV_MODIFYOP
                                         },
                 'dev_alarmop'         : {'logmodule' : 'homerServer',
                                          'condition' : {'first' : ['ALARM with']},
                                          'flag'      : FLAG_DEV_ALARMOP
                                         },
                 'ip_open'             : {'logmodule' : 'homerServer',
                                          'condition' : {'first' : ['Open']},
                                          'flag'      : FLAG_IP_OPEN
                                         },
                 'server_statuschange' : {'logmodule' : 'homerServerDaemon',
                                          'condition' : {},
                                          'flag'      : FLAG_SERVER_STATUSCHANGE
                                         },
                 'server_servererror'  : {'logmodule' : 'homerServer',
                                          'condition' : {'first' : ['WARNING','EXCEPTION']},
                                          'flag'      : FLAG_SERVER_SERVERERROR
                                         },
                 'server_dberror'      : {'logmodule' : 'homerDBServer',
                                          'condition' : {'first' : ['WARNING','EXCEPTION']},
                                          'flag'      : FLAG_SERVER_DBERROR
                                         },
                 'server_debugerror'   : {'logmodule' : 'homerDebug',
                                          'condition' : {'first' : ['WARNING','EXCEPTION']},
                                          'flag'      : FLAG_SERVER_DEBUGERROR
                                         },

                }
