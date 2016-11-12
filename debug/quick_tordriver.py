#!/usr/local/opt/python3/bin/python3

from bencoding.bencode import encode, decode
import hashlib
import requests
import socket
import random
import os
from struct import unpack, pack
from string import ascii_letters, digits
from urllib.parse import urlparse

import pprint
pp = pprint.PrettyPrinter(indent=2)

# GLOBALS:
ALPHANUM = ascii_letters + digits
peer_id = ('-DE0001' + ''.join(random.sample(ALPHANUM, 13)))



def get_peer_list(torrent_path):
    # Open torrent and read data into data variable
    data = None
    with open(torrent_path, 'rb') as f:
        read_data = f.read()
        data = decode(read_data)

    # Generate hash of info field
    info_hash = hashlib.sha1(encode(data[b'info'])).digest()
    
    # Calculate length of all torrent files, assume these are all multi-torrent files
    length = 0
    for file in data[b'info'][b'files']:
        length += file[b'length']

    # Make requests to a bunch of trackers and get the list of peers
    decoded_peers = []
    if b'announce-list' in data:
        for tracker_list in data[b'announce-list']:
            for tracker in tracker_list:
                if(tracker.decode('utf-8')[:3] == 'udp'):
                    decoded_peers = request_peers_http('http' + tracker.decode('utf-8')[3:], info_hash, length)
                elif(tracker.decode('utf-8')[:4] == 'http'):
                    decoded_peers = request_peers_http(tracker.decode('utf-8'), info_hash, length)
                else:
                    print('skipping - Unknown tracker url format: ' + tracker[0])
    return(decoded_peers)

def send_handshake(peer, info_hash):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)

    handshake_request =  pack('!1s', bytearray(chr(19), 'utf8')) # length of the protocol string
    handshake_request += pack('!19s', bytearray('BitTorrent protocol', 'utf-8')) # protocol
    handshake_request += pack('!q', 0) # reserved should be all 0's
    handshake_request += pack('!20s', info_hash)
    handshake_request += pack('!20s', bytearray(peer_id, 'utf8'))
    
    try:
        sock.connect((peer[0], int(peer[1])))
    except Exception as e:
        print('connection refused, skipping peer...')
        return # skip trackers we can't connect to

    print('connected')

    print('sending handshake...')
    sock.send(handshake_request)

    try:
        response = sock.recv(68)
        if response:
            print('received response: ')
            print(response)
    except Exception as e:
        print(e)
        return

def request_peers_http(tracker, info_hash, length):
    decoded_peers = []
    payload = {'info_hash': info_hash, 'peer_id': peer_id, 'length': length, 'uploaded':0, 'downloaded':0, 'compact':1}
    try:
        print('Attempting connection to: ' + tracker)
        r = requests.get(tracker, params=payload, timeout=1, verify=False)
        if(r.status_code == 200):
            print('connection successfull, adding peers to list')
            # Grab the peers and split them into manageable chunks
            peers = decode(r.content)[b'peers']
            peers = [peers[i:i+6] for i in range(0, len(peers), 6)]
            # For each peer: print the ip and unpack the last 2 bytes as an int for the port
            for p in peers:
                ip = str(socket.inet_ntoa(p[:4]))
                port = str(unpack('>H', p[4:])[0])
                decoded_peers.append((ip, port))
    except Exception as e:
        print('connection refused')
        pass
    return(decoded_peers)

for file in os.listdir('sample_torrents'):
    print('\n========================================================================================')

    print('getting list of peers for ' + file)
    peers = get_peer_list('sample_torrents/' + file)
    print('got the following peers: ')
    pp.pprint(peers)

    if len(peers) == 0:
        continue

    print('---')

    data = None
    with open('sample_torrents/' + file, 'rb') as f:
        read_data = f.read()
        data = decode(read_data)
    #pp.pprint(data)
        
    # Generate hash of info field
    info_hash = hashlib.sha1(encode(data[b'info'])).digest()
    for p in peers:
        print('starting handshake with peer: ' + p[0])
        send_handshake(p, info_hash)

    print('========================================================================================')
