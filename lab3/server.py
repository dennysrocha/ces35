#!/usr/bin/env python3

import socket
import sys
import numpy as np
import threading
import os, re
from random import randint
import time

port = 50000
backlog = 5
size = 1024
threads = []
usernames = list()
desafiados = [("example1","example2")]
acabou = False
ganhador = []

# pegando meu NIC address
addresses = os.popen('IPCONFIG | FINDSTR /R "Ethernet adapter Local Area Connection .* Address.*[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*"')
nic = re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', addresses.read()).group()

host = nic
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(backlog)

print ("Servidor aberto em", nic, "\n")



def manager(client, address):
	"""thread manager function"""

	# jogo: a cada rodada eh jogada uma moeda que resulta em um valor de 1 a 19; o player ganha se a distancia dele ate o valor gerado for menor ou igual a distancia
	# do outro ate o mesmo valor; é improvavel mas pode acontecer dos dois players ganharem a partida (falta ajustar esse caso)
	def rochida(desafiado):
		global acabou
		global usernames
		global ganhador
		meuNome="".join([item[0] for item in usernames if item[2] == address])
		while not acabou:
			if acabou:
				break;
			randomico = randint(1,19) # convencao: 0 para "MENOR" e 1 para "MAIOR"
			time.sleep(0.5)
			print("O valor randomico gerado para o", meuNome, "eh", randomico)
			meuValor = client.recv(size).decode("utf-8") # valor numero digitado pelo usuario
			print("Recebido:", meuValor, "\ndo", meuNome)
			usernames = [item for item in usernames if item[0] != meuNome]
			usernames.append((meuNome,meuValor,address))

			while True:
				if ([item for item in usernames if (item[0] == desafiado and item[1]==-1)] == []): # verificar se a tupla ainda nao foi atualizada com o valor do desafiado
					break;
			valor = "".join([str(item[1]) for item in usernames if item[0] == desafiado]) # pega o valor inserido pelo desafiado
			
			# PROCESSO DE AVALIACAO PARA VER QUEM GANHOU A RODADA
			if abs(int(meuValor)-randomico)<=abs(int(valor)-randomico):
				print("-------------------------------------")
				print("O usuario", meuNome, "ganhou a rodada")
				print("-------------------------------------")
				myMessage = "GANHOURODADA"
				time.sleep(1)
			else:
				myMessage = "PERDEURODADA"
			client.send(myMessage.encode("utf-8")) # diz se perdeu ou ganhou a rodada

			usernames = [item for item in usernames if item[0] != meuNome]
			usernames.append((meuNome,-1,address))
			
			# PROCESSO DE AVALIACAO PARA VER SE O PLAYER ACABOU
			data = client.recv(size).decode("utf-8")
			time.sleep(1)
			print("Recebido:", data, "\ndo", meuNome)
			if data=="ACABEI":
				acabou = True
				ganhador = meuNome
			else:
				myMessage = "CONTINUAR"
				time.sleep(1)
				if not acabou:
					client.send(myMessage.encode("utf-8"))

		myMessage = "ACABOU"
		client.send(myMessage.encode("utf-8"))
		if ganhador == meuNome:
			client.send(meuNome.encode("utf-8"))
		else:
			client.send(desafiado.encode("utf-8"))



	global desafiados
	print("Conexao com", address, "estabelecida.")
	
	text = "Digite seu username: "
	client.send(text.encode("utf-8"))
	data = client.recv(size).decode("utf-8")
	print("Recebido:", data, "\ndo", address)
	usernames.append((data,-1,address)) # (username, valorDigitado)

	print("Usuário adicionado! \nNova lista de usuários:", [item[0] for item in usernames])
	meuNome = "".join([item[0] for item in usernames if item[2] == address])

	while True:
		data = client.recv(size).decode("utf-8")
		print("Recebido:", data, "\ndo", meuNome)
		if data:


			# O CLIENTE QUER SABER QUANTOS PLAYERS EXISTEM
			if data.upper()=="PLAYERS":
				text = ", ".join([x[0] for x in usernames])
				client.send(text.encode("utf-8"))


			# O CLIENTE QUER JOGAR COM ALGUEM
			elif data.upper()=="JOGAR":
				text = "DESAFIOU"
				client.send(text.encode("utf-8")) # envia o texto para entrar na secao de desafio no cliente
				data = client.recv(size).decode("utf-8") # recebendo o nome do desafiado
				print("Recebido:", data, "\ndo", meuNome)
				desafiados.append((data, meuNome)) # coloca o nome do desafiado na lista "desafiados"
				while(any(data in item[0] for item in desafiados)):
					pass
					# aguarda até o desafiado verificar que foi desafiado e aceitar o desafio
				text = "ACEITO"
				client.send(text.encode("utf-8"))
				rochida(data)


			# O CLIENTE QUER SABER SE TEM ALGUEM QUERENDO JOGAR COM ELE
			elif data.upper()=="STATUS":
				if([item[0] for item in desafiados if item[0] == meuNome] != []):
					text = "DESAFIADO" # voce esta na lista de pessoas desafiadas: foi DESAFIADO!
					# remova seu nome dos desafiados!					
					desafiador = "".join([item[1] for item in desafiados if item[0] == meuNome]) # encontra o nome do desafiador
					desafiados = [item for item in desafiados if item[0] != meuNome]
					text = "DESAFIADO"
					client.send(text.encode("utf-8"))
					rochida(desafiador)
				else:
					text = "Voce nao foi desafiado"
					client.send(text.encode("utf-8"))


			# ALGUMA MENSAGEM QUE NAO ATENDA AOS CRITERIOS ANTERIORES
			else:
				text = "Servidor recebeu a mensagem."
				client.send(text.encode("utf-8"))




while True:
	client, address = s.accept()
	t = threading.Thread(target=manager, args=(client, address))
	threads.append(t)
	t.start()
sys.exit()