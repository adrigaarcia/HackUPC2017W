#!/usr/bin/python
import http.server
import urllib
import uuid
import datetime
import os
import threading
import time
import string

#import numpy as np
#import matplotlib.pyplot as plt

#from sklearn.cluster import DBSCAN
#from sklearn import metrics
#from sklearn.datasets.samples_generator import make_blobs
#from sklearn.preprocessing import StandardScaler

PORT_NUMBER = 8080

DB_FILE_PATH = 'db'

SAMPLE_TIME_MAX_GAP = 10
CLUSTERIZING_PERIOD = 2

class ws_handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        uuid = query_params['id']
        current_datetime = datetime.datetime.timestamp()
        # Start of critical section
        db_lock.acquire()
        db[uuid]['user_state'] = query_params['user_state']
        db[uuid]['last_time'] = current_datetime
        db_lock.release()
        # End of critical section
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write("ACK")
        return

    def do_POST(self):
        new_uuid = uuid.uuid4()
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write(str(new_uuid))
        return

def filter_currying(time):
    def db_clean(element):
        return time - element['last_time'] < SAMPLE_TIME_MAX_GAP
    return db_clean

# Periodically request clustering of all samples
class cluster_requester(threading.Thread):
    def __init__(self, stop_flag):
        threading.Thread.__init__(self)
        self.stop_flag = stop_flag

    # Runnable function
    def run(self):
        print("running\n")
        while True:
            time.sleep(CLUSTERIZING_PERIOD)
            # check stop flag
            if stop_flag.wait():
                break
            db = filter(filter_currying(datetime.datetime.timestamp()), db)
            # need to format db in order to be clusterized
            clusterize(db)

db = dict()
# Mutex is needed to ensure safe read/write from multiple threads
db_lock = threading.Lock()

# Read current file
try:
    db_file = open(DB_FILE_PATH, 'r+')
    for line in db_file:
        # user_id lat long user_state last_time
        user_info = line.strip('\n').split(' ')
        db[user_info[0]] = dict()
        db[user_info[0]]['lon'] = user_info[1]
        db[user_info[0]]['lat'] = user_info[2]
        db[user_info[0]]['user_state'] = user_info[3]
        db[user_info[0]]['last_time'] = user_info[4]
    db_file.close()
    # Clean file
    os.remove(DB_FILE_PATH)
    db_file = open(DB_FILE_PATH, 'w+')
except IOError:
    db_file = open(DB_FILE_PATH, 'w+')

global stop_flag
stop_flag = threading.Event()
cluster_requester(stop_flag).start()

try:
    # Web server handler
    server = http.server.HTTPServer(('', PORT_NUMBER), ws_handler)
    print ('Started httpserver on port ' , PORT_NUMBER)

    server.serve_forever()

except KeyboardInterrupt:
    # Stop thread
    stop_flag.set()
    # Update database
    for key, value in db.items():
        db_file.write(key+' ')
        db_file.write(value['lon']+' ')
        db_file.write(value['lat']+' ')
        db_file.write(value['user_state']+' ')
        db_file.write(value['last_time']+'\n')
    print ('^C interrupt, saving db and shutting down...')
    # Shut down
    server.socket.close()