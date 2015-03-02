import os
import fcntl
from time import sleep
from threading import Thread, Lock
from datetime import datetime, timedelta

from log_analysis import LogFileAnalysis
from config.config import CACHE_PATH, CACHE_UPDATE_TIME, \
                          CACHE_CREATATION_TIME, search_items
from config.constants import TIME_FORMAT_MS

class CacheFile(object):
    def __init__(self, filename):
        self.filelock = Lock()
        self.cachefilename = filename
        self.cachefile = os.path.join(CACHE_PATH, filename)
        self.cacheconfigfile = os.path.join(CACHE_PATH, CACHE_CREATATION_TIME)
        # Create cache path
        if not os.path.exists(CACHE_PATH):
            os.makedirs(CACHE_PATH)
        # Create related cache file
        if not os.path.exists(self.cachefile):
            open(self.cachefile, 'w').close()
        # Create cache time config file
        if not os.path.exists(self.cacheconfigfile) :
            open(self.cacheconfigfile, 'w').close()

        # Get endtime form cache config file
        with open(self.cacheconfigfile, 'r') as cachefile:
            lines = cachefile.readlines()
            for line in lines:
                if filename in line:
                    self.endtime = line[0:26]
                    self.endtime_obj = \
                        datetime.strptime(self.endtime, TIME_FORMAT_MS)
                    return
        # If filename not in cache config file, set endtime  2014-06-04
        with open(self.cacheconfigfile, 'a') as configfile:
            configfile.write('2014-06-04 01:01:01,000000|' + filename + '\n')
            self.endtime = ''
            self.endtime_obj = datetime(2014, 6, 4)

    # Get period of time content from related cache file
    def require_from_cachefile(self, begintime, endtime):
        content = []
        if not os.path.exists(self.cachefile):
            return False
        with open(self.cachefile, 'r') as cachefile:
             lines = cachefile.readlines()
             lines = sorted(set(lines))
             for line in lines:
                time = line[0:23]
                try:
                    time = datetime.strptime(time, TIME_FORMAT_MS)
                except:
                    continue

                if time > endtime:
                    break
                if time >= begintime and time <= endtime:
                    content.append(line)
        return content

    # Append related content to related cache file
    def append_to_cachefile(self, content):
        if not os.path.exists(self.cachefile):
            return False

        with open(self.cachefile, 'a') as cachefile:
            cachefile.writelines(content)
            cachefile.flush()

        return True

    # Remove duplicates and sort the content
    def sort_cache_file(self):
        with open(self.cachefile, 'r+') as cachefile:
            fcntl.flock(cachefile.fileno(), fcntl.LOCK_EX)
            lines = cachefile.readlines()
            lines = sorted(set(lines))
            cachefile.seek(0, 0)
            cachefile.truncate()
            cachefile.writelines(lines)
            cachefile.flush()
            fcntl.flock(cachefile.fileno(), fcntl.LOCK_UN)

    def update_config_time(self, endtime):
        if not os.path.exists(self.cacheconfigfile):
            return
        with open(self.cacheconfigfile, 'r') as cacheconfigfile:
            lines = cacheconfigfile.readlines()

        for i in range(0, len(lines)):
            if self.cachefilename in lines[i]:
                lines[i] = endtime + '|' + self.cachefilename + '\n'

        with open(self.cacheconfigfile, 'w+') as cacheconfigfile:
            cacheconfigfile.writelines(lines)
            cacheconfigfile.flush()

    # Get cache content
    # update cache file and config file
    def handle_cache_file(self, starttime, endtime):
        loglines = []
        item = self.cachefilename
        if  item not in search_items:
            return False
        logmodule = search_items[item]['logmodule']


        logfile_list = \
            LogFileAnalysis.get_logfile_list(starttime, \
                                        endtime, logmodule)
 
        logfile = LogFileAnalysis(self.cachefilename)
        for logfilename in logfile_list:
            loglines = loglines + logfile.get_log_lines(starttime, \
                                                endtime, logfilename)
        content = logfile.log_analysis(loglines)
        if not content:
            return True

        self.filelock.acquire()
        self.append_to_cachefile(content)
        self.filelock.release()

        return True

    def virtual_map_reduce(self, starttime, endtime):
        # Calculate days
        days = (endtime.date() - starttime.date()).days + 1                               
        start_time = starttime
        end_time = start_time.replace(hour=23,minute=59,second=59,microsecond=999999)

        threads = []
        threadid = range(0, days)
        for i in threadid:
            if end_time > endtime:
                end_time = endtime
            thread = Thread(target=self.handle_cache_file , \
                            args=(start_time, end_time))
            threads.append(thread)
            start_time = end_time + timedelta(microseconds=1)
            end_time = start_time.replace(hour=23,minute=59,second=59,microsecond=999999)

        for i in threadid:
            threads[i].start()

        for i in threadid:
            threads[i].join()

        return True

    def generate_cache(self):
        # Record cache file modify time
        mtime_old = os.stat(self.cachefile).st_mtime
        # Get start time
        if self.endtime == '':
            starttime = datetime(2014, 06, 04)
        else:
            starttime = self.endtime_obj

        endtime = datetime.now()
        self.virtual_map_reduce(starttime, endtime)

        # Update cache config file
        endtime = datetime.strftime(endtime, TIME_FORMAT_MS)
        self.update_config_time(endtime)

        # Check whether need to sort the content in cache file
        mtime_new = os.stat(self.cachefile).st_mtime
        if mtime_old != mtime_new:
            self.sort_cache_file()

        return True

def create_cache(loop):
    logfilenames = search_items.keys()
    count = 0
    while True:
        logfilename = logfilenames[count%len(logfilenames)]
        if logfilename == 'app_netstatus':
            count = count + 1
            continue
        cache = CacheFile(logfilename)
        cache.generate_cache()
        count = count + 1
        if count%len(logfilenames) == 0:
            if not loop:
                return
            count = 0
            sleep(CACHE_UPDATE_TIME)
