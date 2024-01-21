#!/usr/bin/env python
"""
GMU - CS 555 - Programming Assignment 1
DNS client -- the interface of the DNS client, which handles the interaction with users.

@author: Ying Meng (G#01409388)
@email: ymeng2@gmu.edu
"""
import argparse
import socket

from message import Message


class DNSClient(object):
    def __init__(self, server='8.8.8.8'):
        """Default DNS server is Google's public DNS server."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # set timeout to 10 seconds
        self.socket.settimeout(10)
        self.connect(server)
        
    def connect(self, server):
        """Connect to the server."""
        try:
            # Use UDP to connect to the server.
            print(f'[INFO] Connecting to server {server}...') 
            self.socket.connect((server, 53))
        except Exception:
            print(f'[ERROR] Unable to connect to server {server}.')
            return False
        
        print('[INFO] Connected.')
        self.server = server
        return True
    
    def query(self, domain, IPv6=False):
        """Query the server for the IP address of the given domain name."""
        
        # Encode the request.
        message = Message()
        request = message.encode(domain, IPv6)
        print(f'[INFO] Sending DNS query...')
        self.socket.send(request)
        
        # Wait for the response.
        try:
            response = self.socket.recv(1024)
        except socket.timeout:
            print(f'[ERROR] Timeout when querying {self.server}')
            exit(0)
        
        # Decode the response.
        message.decode(response)
        print(f'[INFO] Response from {self.server}:')
        message.display()
            
        if message.has_answer():
            print(f'[INFO] Query `{domain}` from `{self.server}`.')
            print(f'[INFO] Received IPs:\n{message.get_ips()}')
        else:
            print(f'[INFO] No answer from {self.server}.')
        print('_'*50)
    
    def disconnect(self):
        """Close the connection."""
        self.socket.close()
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DNS client.')
    parser.add_argument('hostname', nargs=1, metavar='name', help='Host name to request.')
    
    args = parser.parse_args()
    
    client = DNSClient()
    client.query(domain=args.hostname[0])
    client.disconnect()