import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from json import dumps, loads
from datetime import datetime, timedelta
import time
from tornado.websocket import WebSocketHandler

from handle import *
from cache import CacheFile
from logger import mlogger as logger
from config.config import port, IS_DIVISION_RETURN, \
                          MAX_HANDLE_LINES, search_items
from config.constants import TIME_FORMAT, TIME_FORMAT_MS, \
                             REG_CONNID
from log_analysis import get_value, LogFileAnalysis


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')

# Subclass of tornado.websocket.WebSocketHander
# Class used to handle log search
class SearchHandler(WebSocketHandler):
    def open(self):
        super(SearchHandler, self).open()

    def check_origin(self,origin):
        return True

    def on_message(self, msg):
        if not msg:
            self.close()
            return

        logger.info("Search message " + msg)

        name, args = self.get_arguments(msg)

        if name == 'expansion':
            ret = self.handle_expansion(name, args)
        else:
            if name not in search_items:
                return
            ret = self.handle_nomal_search(name, args)

        if not ret:
            self.close()

        logger.info("Finsh sending data")

        return

    def on_close(self):
        super(SearchHandler, self).on_close()

    def close(self):
        super(SearchHandler, self).close()

    # Send json data to client
    def send_data(self, name, data):

        data['name'] = name

        json_data = dumps(data, sort_keys=True)
        self.write_message(json_data)

        return

    # Get name and args
    def get_arguments(self, msg):
        try:
            value = loads(msg)
        except:
            logger.exception('Msg format error')
            self.close()
            return

        if 'name' not in value:
            logger.warning('Missing event name')
            self.close()
            return
        if 'args' not in value:
            logger.warning('Missing event args')
            self.close()
            return

        name = value['name']
        args = value['args']

        return name, args

    def handle_nomal_search(self, name, args):
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

        cache_file = name
        # 'app_netstatus' and 'app_statuschange' use same cachefile
        if name == 'app_netstatus':
            cache_file = 'app_statuschange'

        # Get info list from cache file
        cache_obj = CacheFile(cache_file)
        if cache_obj.endtime_obj < endtime:
            cache_obj.generate_cache()

        info_list = cache_obj.require_from_cachefile(starttime, endtime)
        # info list is empty
        if not info_list:
            data['FIN'] = True
            data['args'] ={}
            self.send_data(name, data)

            return True

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

            self.send_data(name, data)

        return True

    def handle_expansion(self, name, args):
        data = {}
        display = []
        lineflag = { 'doop'     : ['DO', 'DONE'],
                     'alarmop'  : ['ALARM', 'ALARMOK'],
                     'sceneop'  : ['SCENE', 'SCENEOK'],
                     'modifyop'   : ['MODIFY','UPDATE']
                   }

        try:
            threadid = args['threadid']
            context = args['context']
            strtime = args['time']
            time = datetime.strptime(strtime, TIME_FORMAT_MS)
        except:
            logger.exception('Args error')
            return False

        # Calcute start time and end time from strtime
        starttime = time + timedelta(seconds=-10)
        endtime = time + timedelta(seconds=50)

        # Get relate log line
        logfile = LogFileAnalysis.get_logfile_list(starttime, \
                                                   endtime, 'homerServer')
        logline = LogFileAnalysis.get_log_lines(starttime, \
                                                  endtime, logfile[0])

        for i in range(0, len(logline)):
            if strtime in logline[i] and \
               threadid in logline[i]:
                display.append(logline[i].replace('\n', ''))
                connid = get_value(REG_CONNID, logline[i])
                # Find need line according to operation type
                if lineflag[context][0]+' with' in logline[i]:
                    for j in range(i+1, len(logline)):
                        if 'Start Processing (' + connid + '): ' + lineflag[context][0] in logline[j]:
                            display.append(logline[j].replace('\n', ''))
                            for m in range(j+1, len(logline)):
                                if 'Sent (' + connid + '): ' + lineflag[context][0] in logline[m]:
                                    display.append(logline[m].replace('\n', ''))
                                    break
                        break
                break

        data['args'] = display
        self.send_data(name, data)

        return True

# Create and start tornado server
def run_server():
    CUR_PATH = os.path.dirname(os.path.realpath(__file__))
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers = [(r'/', IndexHandler),
                    (r'/result', SearchHandler)],
        template_path = os.path.join(os.path.dirname(CUR_PATH), 'templates'),
        static_path = os.path.join(os.path.dirname(CUR_PATH), 'static')
    )

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
