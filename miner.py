from  multiprocessing import Process
from miner.tornado_server import run_server
from miner.cache import create_cache

def start():

    # Generate initial cache file
    print('Creating initial cache file, please wait...')
    create_cache(False)
    print('Starting miner server...')

    # Create subprocess
    create_cache_proc = Process(target=create_cache, args=(True,))
    create_cache_proc.start()
    log_search_proc = Process(target=run_server, args=())
    log_search_proc.start()

if __name__ == '__main__':
    start()
