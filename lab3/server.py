#!/usr/bin/env python3

import socket
import sys
import numpy as np
import threading
import os, re

port = 50000
backlog = 5
size = 1024
threads = []
N=2 # numero de jogadores

# pegando meu NIC address
addresses = os.popen('IPCONFIG | FINDSTR /R "Ethernet adapter Local Area Connection .* Address.*[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*"')
nic = re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', addresses.read()).group()

host = nic
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)

print ("Servidor aberto em", nic, "\n")

def parOuImpar(client, address):
	"""thread parOuImpar function"""
	while True:
		data = client.recv(size)
		if data:
			print("Recebendo", data.decode("utf-8"), "de", address, "\n")


while True:
	client, address = s.accept()
	t = threading.Thread(target=parOuImpar, args=(client, address))
	threads.append(t)
	t.start()
sys.exit()