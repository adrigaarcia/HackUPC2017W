#!/usr/bin/python
import http.server
import urllib
import uuid
import os
import threading
import time
import string
import random

import json

import numpy as np
import matplotlib.pyplot as plt

from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from sklearn.preprocessing import StandardScaler

PORT_NUMBER = 8080

DB_FILE_PATH = 'db'

SAMPLE_TIME_MAX_GAP = 10000000
CLUSTERIZING_PERIOD = 1

SIMULATE = True

if SIMULATE:
    # Generate random samples
    centers1 = [[51.505, -0.09], [51.484751, -0.535565], [51.479620, -0.422992], [51.688682, -0.104352], [51.356294, -0.094739], [51.46171, -0.26367]]
    centers2 = [[51.505, -0.09], [51.484751, -0.535565], [51.479620, -0.422992]]
    centers3 = [[51.688682, -0.104352], [51.356294, -0.094739], [51.46171, -0.26367]]
    print("Generating randomized simulation data")
    sim_data1, labels_true = make_blobs(n_samples=350, n_features=2, centers=centers1, cluster_std=0.05, random_state=0)
    sim_data2, labels_true = make_blobs(n_samples=350, n_features=2, centers=centers2, cluster_std=0.003, random_state=0)
    sim_data3, labels_true = make_blobs(n_samples=350, n_features=2, centers=centers3, cluster_std=0.003, random_state=0)

def clusterize(X):

    #print(X)
    #names = ['X','Y']
    #formats = ['f8','f8']
    #dtype = dict(names = names, formats=formats)
    XR = []
    XS = []
    order = []
    for x in X:
        genre = x[2].strip()
        order.append(genre)
        # if genre is 0
        if genre.startswith('0'):
            XR.append(x[0:2])
        else:
            XS.append(x[0:2])

    #print(len(order))

    XR = np.array(XR, dtype=float)
    XS = np.array(XS, dtype=float)

    #print(XR)
    #print(XS)
    #print(str(XR)+'\n')
    #print(str(XS)+'\n')
    
    XR = StandardScaler().fit_transform(XR)
    XS = StandardScaler().fit_transform(XS)

    XNorm = StandardScaler().fit_transform(X)

    dbscanR = DBSCAN(eps=0.2, min_samples=50).fit(XR)
    dbscanS = DBSCAN(eps=0.2, min_samples=50).fit(XS)
    db = DBSCAN(eps=0.2, min_samples=10).fit(XNorm)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    print(labels)

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    # print('Estimated number of clusters: %d' % n_clusters_)
    # print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
    # print("Completeness: %0.3f" % metrics.completeness_score(labels_true, labels))
    # print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
    # print("Adjusted Rand Index: %0.3f"
    #       % metrics.adjusted_rand_score(labels_true, labels))
    # print("Adjusted Mutual Information: %0.3f"
    #       % metrics.adjusted_mutual_info_score(labels_true, labels))
    # print("Silhouette Coefficient: %0.3f"
    #       % metrics.silhouette_score(X, labels))

    # # Black removed and is used for noise instead.
    # unique_labels = set(labels)
    # colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    # for k, col in zip(unique_labels, colors):
    #     if k == -1:
    #         # Black used for noise.
    #         col = 'k'

    #     class_member_mask = (labels == k)

    #     xy = X[class_member_mask & core_samples_mask]
    #     plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
    #              markeredgecolor='k', markersize=14)

    #     xy = X[class_member_mask & ~core_samples_mask]
    #     plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
    #              markeredgecolor='k', markersize=6)

    # plt.title('Estimated number of clusters: %d' % n_clusters_)
    # plt.show()

    # Getting the labels for each input point
    y_predR = dbscanR.labels_.astype(np.int)
    y_predS = dbscanS.labels_.astype(np.int)
    y_end= []

    y_predR = y_predR.tolist()
    y_predS = y_predS.tolist()

    XNorm = XNorm.tolist()

    dict_cluster = {}
    print(order)
    for genre in order:
        #print('patata')
        if (genre.startswith('1')) and (len(y_predS) > 0):
            #print('seguro')
            safe_cluster = y_predS.pop(0)
            if (safe_cluster == -1):
                y_end.append(safe_cluster)
            else:
                safe_cluster = -(safe_cluster + 2)
                y_end.append(safe_cluster)

            # Add to dictionary
            if safe_cluster in dict_cluster:
                puntos = dict_cluster[safe_cluster]
                coordenadas = X.pop(0)
                puntos.append({'lon': coordenadas[0] , 'lat': coordenadas[1]})
                dict_cluster[safe_cluster] = puntos
            else:
                coordenadas = X.pop(0)
                print(coordenadas)
                dict_cluster[safe_cluster] = [{'lon': coordenadas[0] , 'lat': coordenadas[1]}]

        elif len(y_predR) > 0:
            #print('riesgo')
            risk_cluster = y_predR.pop(0)
            if (risk_cluster == -1):
                risk_cluster = 0
                y_end.append(0)
            else:
                risk_cluster = risk_cluster + 2
                y_end.append(risk_cluster)

            # Add to dictionary
            if risk_cluster in dict_cluster:
                puntos = dict_cluster[risk_cluster]
                coordenadas = X.pop(0)
                puntos.append({'lon': coordenadas[0] , 'lat': coordenadas[1]})
                dict_cluster[risk_cluster] = puntos
            else:
                coordenadas = X.pop(0)
                dict_cluster[risk_cluster] = [{'lon': coordenadas[0] , 'lat': coordenadas[1]}]


        #print(dict_cluster)

    # # Black removed and is used for noise instead.
    # unique_labels = set(labels)
    # colors = plt.cm.Spectral(np.linspace(0, 1, len(unique_labels)))
    # for k, col in zip(unique_labels, colors):
    #     if k == -1:
    #         # Black used for noise.
    #         col = 'k'

    #     class_member_mask = (labels == k)

    #     xy = X[class_member_mask & core_samples_mask]
    #     plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
    #              markeredgecolor='k', markersize=14)

    #     xy = X[class_member_mask & ~core_samples_mask]
    #     plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=col,
    #              markeredgecolor='k', markersize=6)

    # plt.title('Estimated number of clusters: %d' % n_clusters_)
    # plt.show()

    return dict_cluster

class ws_handler(http.server.BaseHTTPRequestHandler):

    def do_POST(self):
        global db
        global db_lock
        #print(self.path)
        url_split = self.path.strip('\n').split('/')
        # first idx is empty
        url_split.pop(0)
        #print(url_split)

        uuid = str(url_split[0])
        current_datetime = time.time()
        # Start of critical section
        db_lock.acquire()
        if uuid not in db.keys():
            db[uuid] = dict()
        db[uuid]['lon'] = url_split[1]
        db[uuid]['lat'] = url_split[2]
        db[uuid]['user_state'] = url_split[3]
        db[uuid]['last_time'] = current_datetime
        db_lock.release()
        # End of critical section
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write("ACK".encode())
        return

    def do_GET(self):
        global clustered_db
        global clustered_db_lock
        #print(self.path)
        url_split = self.path.strip('\n').split('/')
        # first idx is empty
        url_split.pop(0)
        #print(url_split)

        # cluster
        if 'cluster' in url_split:
            res = dict()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            clustered_db_lock.acquire()
            res = clustered_db
            clustered_db_lock.release()
            #print(str(json.dumps(res)))
            self.wfile.write(str(json.dumps(res)).encode())
        # new uuid requested
        else:
            new_uuid = uuid.uuid4()
            #print("new id: "+str(str(new_uuid).encode())+"\n")
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(str(new_uuid).encode())
        return

def filter_currying(time):
    def db_clean(element):
        if SIMULATE:
            return True
        else:
            return time - element['last_time'] < SAMPLE_TIME_MAX_GAP
    return db_clean

# Periodically request clustering of all samples
class cluster_requester(threading.Thread):
    def __init__(self, stop_flag):
        threading.Thread.__init__(self)
        self.stop_flag = stop_flag

    # Runnable function
    def run(self):
        global db
        global db_lock
        global clustered_db
        global clustered_db_lock
        while True:
            # check stop flag
            if stop_flag.wait(0.0):
                break

            time.sleep(CLUSTERIZING_PERIOD)
            #print(time.time())
            db_lock.acquire()
            db = { key : db[key] for key in db if filter_currying(time.time()) }
            db_lock.release()
            # need to format db in order to be clusterized
            db_aux = []
            for i in db.keys():
                line = []
                line.append(db[i]['lon'])
                line.append(db[i]['lat'])
                line.append(db[i]['user_state'])
                line.append(db[i]['last_time'])
                db_aux.append(line)
            #print("Requesting clusters")
            res = clusterize(db_aux)
            #print("Clusters:")
            #print(str(res))
            clustered_db_lock.acquire()
            clustered_db = res
            clustered_db_lock.release()
            #print(clustered_db)

db = dict()
clustered_db = dict()
# Mutex is needed to ensure safe read/write from multiple threads
db_lock = threading.Lock()
clustered_db_lock = threading.Lock()

# Use in-memory randomized data
if SIMULATE:
    current_datetime = time.time()
    print(str(current_datetime))
    for data in sim_data1:
        user_id = str(uuid.uuid4())
        is_at_risk = random.randint(1,3)
        if is_at_risk is 1:
            user_state = '0'
        else:
            user_state = '1'
        db[user_id] = dict()
        db[user_id]['lon'] = str(data[0])
        db[user_id]['lat'] = str(data[1])
        db[user_id]['user_state'] = user_state
        db[user_id]['last_time'] = str(current_datetime)
    for data in sim_data2:
        user_id = str(uuid.uuid4())
        db[user_id] = dict()
        db[user_id]['lon'] = str(data[0])
        db[user_id]['lat'] = str(data[1])
        db[user_id]['user_state'] = str(1)
        db[user_id]['last_time'] = str(current_datetime)
    for data in sim_data3:
        user_id = str(uuid.uuid4())
        db[user_id] = dict()
        db[user_id]['lon'] = str(data[0])
        db[user_id]['lat'] = str(data[1])
        db[user_id]['user_state'] = str(0)
        db[user_id]['last_time'] = str(current_datetime)

# Read/write data from/to local database
else:
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

try:
    global stop_flag
    stop_flag = threading.Event()
    cluster_requester(stop_flag).start()

    # Web server handler
    server = http.server.HTTPServer(('', PORT_NUMBER), ws_handler)
    print ('Started httpserver on port ' , PORT_NUMBER)

    server.serve_forever()

except KeyboardInterrupt:
    # Stop thread
    stop_flag.set()
    if not SIMULATE:
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