# Funções e classes do Django

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages

# Funções e classes do python

import threading

# Funções e classes proprias

class minhaThread(threading.Thread):
    def __init__(self, threadID, nome, problema):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.nome = nome
        self.problema = problema

    def run(self):
        print("Iniciando thread %s" % (self.nome))
        self.problema.busca(self.nome)

class Estado:
    
	# Classe estado se baseia na margem inicial (só precisamos saber quantos tem em um lado para saber quantos tem no outro lado)

    def __init__(self, canibais, missionarios, barco, criador):
        self.canibais = canibais # quantidade de canibais na margem inicial
        self.missionarios = missionarios # quantidade missionarios na margem inicial
        self.barco = barco # se o barco está na margem inicial
        self.criador = criador # qual thread criou esse estado
        
    def __str__(self):
        return ("("+str(self.canibais)+", "+str(self.missionarios)+", "+str(self.barco)+")")

class Problema:
    
    def __init__(self):
        self.caminho_thread1 = list() # caminho que a thread1 percorreu até a solução
        self.caminho_thread2 = list() # caminho que a thread2 percorreu até a solução
        self.visitados_thread1 = list() # todos estados que a thread1 criou até a solução
        self.visitados_thread2 = list() # todos os estados que a thread2 criou até a solução
        self.thread1 = 0 # contador para a busca em profundidade da thread1
        self.thread2 = 0 # contador para a busca em profundidade da thread2
        # Debugs #
        self.mostra_tentativas = True # Mude aqui para mostrar as tentativas ou não (True,False)
        self.execucao = list()
        
    # checaEstado = checagem se o estado é inválido(0), válido(1) ou final(2) #

    def checaEstado(self,estado):
        if(estado.criador == "inicio_pro_fim"):
            for estado_visitado in self.visitados_thread2:
                if((estado.canibais == estado_visitado.canibais) and (estado.missionarios == estado_visitado.missionarios) and (estado.barco == estado_visitado.barco)):
                    return 2
            for i in range (0,len(self.visitados_thread1)): 
                if((estado.canibais == self.visitados_thread1[i].canibais) and (estado.missionarios == self.visitados_thread1[i].missionarios) and (estado.barco == self.visitados_thread1[i].barco)):
                    return 0
        else:
            for estado_visitado in self.visitados_thread1:
                if((estado.canibais == estado_visitado.canibais) and (estado.missionarios == estado_visitado.missionarios) and (estado.barco == estado_visitado.barco)):
                    return 2
            for i in range (0,len(self.visitados_thread2)): 
                if((estado.canibais == self.visitados_thread2[i].canibais) and (estado.missionarios == self.visitados_thread2[i].missionarios) and (estado.barco == self.visitados_thread2[i].barco)):
                    return 0

        if((estado.canibais == estado.missionarios) or (estado.missionarios == 3) or (estado.missionarios == 0)):
            return 1
        else:
            return 0

   	# checaTransicao = checagem se a transicao do barco é possivel #
    
    def checaTransicao(self,transicao,criador):
        canibais = transicao[0] # quantidade de canibais tentando atravessar
        missionarios = transicao[1] # quantidade de missionarios tentando atravessar
        if criador == "inicio_pro_fim":
            estado_atual = self.caminho_thread1[len(self.caminho_thread1)-1]
            if(estado_atual.barco):
                if(estado_atual.canibais < canibais):
                    return 0
                elif(estado_atual.missionarios < missionarios):
                    return 0
            else:
                if((3 - estado_atual.canibais) < canibais):
                    return 0
                if((3 - estado_atual.missionarios) < missionarios):
                    return 0
            return 1
        else:
            estado_atual = self.caminho_thread2[len(self.caminho_thread2)-1]
            if(estado_atual.barco):
                if(estado_atual.canibais < canibais):
                    return 0
                elif(estado_atual.missionarios < missionarios):
                    return 0
            else:
                if((3 - estado_atual.canibais) < canibais):
                    return 0
                if((3 - estado_atual.missionarios) < missionarios):
                    return 0
            return 1

    # Função que atravessa e retorna um novo estado #

    def atravessa(self, canibais, missionarios, criador):
        if criador == "inicio_pro_fim":
            canibais_na_margem = self.caminho_thread1[len(self.caminho_thread1)-1].canibais
            missionarios_na_margem = self.caminho_thread1[len(self.caminho_thread1)-1].missionarios
            barco_na_margem = self.caminho_thread1[len(self.caminho_thread1)-1].barco
            if(barco_na_margem):
                return Estado((canibais_na_margem - canibais), (missionarios_na_margem - missionarios), not(barco_na_margem), criador)
            else:
                return Estado((canibais_na_margem + canibais), (missionarios_na_margem + missionarios), not(barco_na_margem), criador)
        else:
            canibais_na_margem = self.caminho_thread2[len(self.caminho_thread2)-1].canibais
            missionarios_na_margem = self.caminho_thread2[len(self.caminho_thread2)-1].missionarios
            barco_na_margem = self.caminho_thread2[len(self.caminho_thread2)-1].barco
            if(barco_na_margem):
                return Estado((canibais_na_margem - canibais), (missionarios_na_margem - missionarios), not(barco_na_margem), criador)
            else:
                return Estado((canibais_na_margem + canibais), (missionarios_na_margem + missionarios), not(barco_na_margem), criador)
            
    # Função que transforma um vetor de 5 possibilidades em uma transição [canibais,missionarios] #

    def transforma(self,numero):
        if(numero == 0):
            transicao = [1,0]
        elif(numero == 1):
            transicao = [0,1]        
        elif(numero == 2):
            transicao = [1,1]        
        elif(numero == 3):
            transicao = [2,0]        
        elif(numero == 4):
            transicao = [0,2]
        return transicao

    # Função de busca bidirecionada #

    def busca(self,criador):
    	# Direção 1 (inicio pro final) #
        if criador == "inicio_pro_fim":
            for i in range(0,5): 
                self.thread1 = self.thread1 + 1    
                transicao = self.transforma(i)
                if(self.mostra_tentativas): 
                	print(str(self.caminho_thread1[len(self.caminho_thread1)-1])+' ['+str(transicao)+']')
                	self.execucao.append(('Thread 1: '+str(self.caminho_thread1[len(self.caminho_thread1)-1])+' '+str(transicao)))
                if(self.checaTransicao(transicao,criador)):
                    nova_estado = self.atravessa(transicao[0],transicao[1],criador)
                    checkestado = self.checaEstado(nova_estado)
                    if (checkestado == 2):
                    	# Encontrou a solução #
                        self.caminho_thread1.append(nova_estado)
                        self.visitados_thread1.append(nova_estado)
                        return 1
                    elif(checkestado == 1):
                    	# Encontrou uma transição possivel #
                        self.caminho_thread1.append(nova_estado)
                        self.visitados_thread1.append(nova_estado)
                        if(self.busca(criador)): return 1 # Busca em profundidade (recursiva)
            self.caminho_thread1.pop()
            return 0
        # Direção 2 (final pro inicio) #
        # Código igual apenas espelhado com thread2 #
        else:
            for i in range(0,5):
                self.thread2 = self.thread2 + 1    
                transicao = self.transforma(i)
                if(self.mostra_tentativas): 
                	print(str(self.caminho_thread2[len(self.caminho_thread2)-1])+' ['+str(transicao)+']')
                	self.execucao.append(('Thread 2: '+str(self.caminho_thread2[len(self.caminho_thread2)-1])+' '+str(transicao)))
                if(self.checaTransicao(transicao,criador)):
                    nova_estado = self.atravessa(transicao[0],transicao[1],criador)
                    checkestado = self.checaEstado(nova_estado)
                    if (checkestado == 2):
                        self.caminho_thread2.append(nova_estado)
                        self.visitados_thread2.append(nova_estado)
                        return 1
                    elif(checkestado == 1):
                        self.caminho_thread2.append(nova_estado)
                        self.visitados_thread2.append(nova_estado)
                        if(self.busca(criador)): return 1
            self.caminho_thread2.pop()
            return 0

# Funções de redirecionamento do site

def home(request):
	data = {}    
	return render(request, 'app/index.html', data)

def tabela_solucao(request):
    data = {}

    # Criando o problema
    problema = Problema()
    problema.caminho_thread1.append(Estado(3,3,True,"inicio_pro_fim"))
    problema.caminho_thread2.append(Estado(0,0,False,"fim_pro_fim"))
    problema.visitados_thread1.append(Estado(3,3,True,"inicio_pro_fim"))
    problema.visitados_thread2.append(Estado(0,0,False,"fim_pro_inicio"))

    # Criando as threads
    thread1 = minhaThread(1, "inicio_pro_fim", problema)
    thread2 = minhaThread(2, "fim_pro_inicio", problema)

    # Comecando novas Threads
    thread1.start()
    thread2.start()

    threads = []
    threads.append(thread1)
    threads.append(thread2)

    for t in threads:
        t.join()

    data['problema'] = problema

    return render(request, 'app/tabela_solucao.html', data)

def conclusao(request):
	data = {}
	return render(request, 'app/conclusao.html', data)