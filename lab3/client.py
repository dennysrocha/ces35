#!/usr/bin/env python3

import sys
import socket

host   = '192.168.0.106'
port = 50000
size = 1024
pontos = 0

print ("Test client sending packets to IP {0}, via port {1}\n".format(host, port))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
data = s.recv(size).decode("utf-8")
print("Recebendo mensagem de", host)
print(data, end='')
myUsername = input()
s.send(myUsername.encode("utf-8"))
accepted = s.recv(size).decode("utf-8")

def jogar():
	global pontos
	global myUsername
	while pontos<3:
		myMessage = input("Digite um número: ")
		s.send(myMessage.encode("utf-8"))
		data = s.recv(size).decode("utf-8") # recebo a mensagem se ganhei ou perdi a rodada
		if data=="GANHOURODADA": # ganhou a rodada
			pontos=pontos+1

		# MANDO UMA MENSAGEM DIZENDO SE ALCANCEI 19 PTS
		if pontos>=3:
			myMessage = "ACABEI"
		else:
			myMessage = "NAOACABEI"
		s.send(myMessage.encode("utf-8"))

		data = s.recv(size).decode("utf-8") # recebo a mensagem se devo continuar ou se acabou a partida
		if data=="ACABOU":
			break;
	data = s.recv(size).decode("utf-8") # quem ganhou
	if data==myUsername:
		print("Fim de jogo!\nVoce ganhou! :)")
	else:
		print("Fim de jogo!\nVoce perdeu! :(")
	pontos=0

while True:

	# ESCOLHA QUAL O TIPO DE MENSAGEM QUER ENVIAR AO SERVIDOR
	myMessage = input("Digite a mensagem: ")
	s.send(myMessage.encode("utf-8"))


	# O SERVIDOR RESPONDEU À SUA MENSAGEM
	data = s.recv(size).decode("utf-8")

	# sua mensagem foi "JOGAR" e o servidor retornou "DESAFIOU"
	if data=="DESAFIOU":
		myMessage = input("Digite o nome do player a desafiar: ")
		s.send(myMessage.encode("utf-8"))
		data = s.recv(size).decode("utf-8")
		if data=="ACEITO": # o desafio foi aceito pelo adversario
			jogar()
	
	# sua mensagem foi "STATUS" e o servidor disse que voce foi "DESAFIADO"
	elif data=="DESAFIADO":
		print("Voce foi desafiado! Vamos jogar...")
		jogar()
	else:
		print(data)
sys.exit()