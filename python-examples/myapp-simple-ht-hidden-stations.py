# coding: utf-8

# This example considers two hidden stations in an 802.11n network which supports MPDU aggregation.
# The user can specify whether RTS/CTS is used and can set the number of aggregated MPDUs.
#
# Example: ./waf --pyrun "examples/wireless/simple-ht-hidden-stations.py --enableRts=True --nMpdus=8"
#
# Network topology:
#
#   Wifi 192.168.1.0
#
#        AP
#   *    *    *
#   |    |    |
#   n1   n2   n3
#
# Packets in this simulation aren't marked with a QosTag so they are considered
# belonging to BestEffort Access Class (AC_BE).


import sys
import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.wifi
import ns.point_to_point
import ns.mobility
import ns3 

import pandas as pd
import pandas as pd
import numpy as np
import scipy
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
import seaborn as sns
import statsmodels as sm
import scipy.stats as stats
import matplotlib.pyplot as plt
import os

import statsmodels.distributions.empirical_distribution as edf
from scipy.interpolate import interp1d
from scipy.stats.distributions import chi2
import random

# Desligando avisos
import warnings
warnings.filterwarnings("ignore")

# Opções de geração por "Trace" ou "PD"(Probability Distribution)
mt_RG = "Trace"
# Opções de geração de números aleatórios por "tcdf" ou "ecdf" 
tr_RG = "ecdf"

# Definindo variáveis globais

# Auxilia da geração de tempos na rede
aux_global_time = 0

# Variável que auxilia se os arquivos de trace estão prontos para serem lidos
# tr_reader = False
# Define o parametro de rede utilizado nas funções
parameter = ""

# Armazena em np.arrays() os dados dos traces
t_time = np.empty(1)
t_size = np.empty(1)

# Variáveis que armazenam os parametros das distribuições de probabilidade
# time
dist_time = ""
arg_time = []
loc_time = 0
scale_time = 0
# size
dist_size = ""
arg_size = []
loc_size = 0
scale_size = 0

# Variável de auxilio de parada da função tcdf
first_tcdf_time = 0
first_tcdf_size = 0

# Variável de auxilio de parada da função read_trace
first_trace_time = 0
first_trace_size = 0

# Listas que contém os números aleatórios gerados pelo NS3
size_ns3 = []
time_ns3 = []


# Função de leitura dos traces e atribuição dos respectivos dados aos vetores
def read_trace(parameter): 

    if parameter == "Size":
        # Chamando variáveis globais
        global t_size
        global first_trace_size

        # Abrindo arquivos .txt
        t_size = np.loadtxt("scratch/size.txt", usecols=0)
        # print("Trace Size: ", t_size)

        # Plot histograma de t_size:
        plt.hist(t_size)
        plt.title("Histogram of trace ("+parameter+")")
        plt.show()

        # Com ajuda da lib Pandas podemos encontrar algumas estatísticas importantes.
        # y_size_df = pd.DataFrame(y_size, columns=['Size'])
        # y_size_df.describe()

        # Definindo que o parametro size pode ser lido apenas uma vez.
        first_trace_size = 1
    
    
    if parameter == "Time":
        # Chamando variáveis globais
        global t_time
        global first_trace_time

        # Abrindo arquivos .txt
        t_time = np.loadtxt("scratch/time.txt", usecols=0)

        # Obtendo os tempos entre pacotes do trace
        sub = []
        i=0
        for i in range(len(t_time)-1):
            sub.append(t_time[i+1] - t_time[i])
        
        # Passando valores resultantes para a variável padrão t_time
        t_time = np.array(sub)
        # print("Trace Time: ", t_time)

        # Plot histograma t_time:
        plt.hist(t_time)
        plt.title("Histogram of trace ("+parameter+")")
        plt.show()

        # Com ajuda da lib Pandas pode-se encontrar algumas estatísticas importantes.
        # t_time_df = pd.DataFrame(t_time, columns=['Time'])
        # t_time_df.describe()

        # Definindo que o parametro time pode ser lido apenas uma vez.
        first_trace_time = 1        

# Função de geração de variáveis aleatórias por meio da ECDF
def ecdf(y, parameter):
        # Criando listas para os dados utilizados
        Fx = []
        Fx_ = []
        # Realizando ajustes para os vetores que selecionaram os valores gerados
        for i in range(len(y)):
            Fx.append(i/(len(y)+1))
            if i != 0:
                Fx_.append(i/(len(y)+1))
        # Adicionando 1 no vetor Fx_
        Fx_.append(1)    
    
        # print ("Fx: ", len(Fx))
        # print ("Fx_: ", len(Fx_))
        
        # Organizando o vetor com os dados do trace
        y.sort()
        # print ("Y: ", len(y))
        
        # Gerando um valor aleatório entre 0 e 1 uniforme
        rand = np.random.uniform(0,1)
        # print("Rand: ", rand)
        
        # Pecorrer todos os valores do vetor com dados do trace
        # para determinar o valor a ser gerado de acordo com o resultado da distribuição uniforme
        for i in range(len(y)):
            # Condição que define em qual classe o valor é encontrado
            if rand > Fx[i] and rand < Fx_[i]:
                # Determinando o valor resultante 
                r_N = y[i]

        # Condição para retorno do valor de acordo com o parametro de rede.
        if parameter == "Size":
            # print ("ECDF SIZE: ", r_N)
            return(int(r_N))

        if parameter == "Time":
            # print ("ECDF TIME: ", r_N)
            return(r_N)

# Função para definir a distribuição de probabilidade compatível com os 
# valores do trace utilizada para gerar valores aleatórios por TCDF
def tcdf(y, parameter):
    
    # Indexar o vetor y pelo vetor x
    x = np.arange(len(y))
    # Definindo o tamanho da massa de dados
    size = len(x)
    # Definindo a quantidade de bins (classes) dos dados
    nbins = int(np.sqrt(size))

    # Noemalização dos dados
    sc=StandardScaler()
    yy = y.reshape (-1,1)
    sc.fit(yy)
    y_std = sc.transform(yy)
    y_std = y_std.flatten()

    del yy

    # O python pode relatar avisos enquanto executa as distribuições

    # Mais distribuições podem ser encontradas no site da lib "scipy"
    # Veja https://docs.scipy.org/doc/scipy/reference/stats.html para mais detalhes
    dist_names = ['erlang',
                'expon',
                'gamma',
                'lognorm',
                'norm',
                'pareto',
                'triang',
                'uniform',
                'dweibull',
                'weibull_min',
                'weibull_max']
    # Obter os métodos de inferência KS test e Chi-squared
    # Configurar listas vazias para receber os resultados
    chi_square = []
    ks_values = []
    #--------------------------------------------------------#
    
    # Chi-square

    # Configurar os intervalos de classe (nbins) para o teste qui-quadrado
    # Os dados observados serão distribuídos uniformemente em todos os inervalos de classes
    percentile_bins = np.linspace(0,100,nbins)
    percentile_cutoffs = np.percentile(y_std, percentile_bins)
    observed_frequency, bins = (np.histogram(y_std, bins=percentile_cutoffs))
    cum_observed_frequency = np.cumsum(observed_frequency)

    # Repetir para as distribuições candidatas
    for distribution in dist_names:
        # Configurando a distribuição e obtendo os parâmetros ajustados da distribuição
        dist = getattr(scipy.stats, distribution)
        param = dist.fit(y_std)
        #
        # KS TEST
        #
        # Criando percentil
        percentile = np.linspace(0,100,len(y_std))
        percentile_cut = np.percentile(y_std, percentile) 
        
        # Criando CDF da teórica
        # Ft = dist.rvs(*param[:-2], loc=param[-2], scale=param[-1], size = size)
        Ft = dist.cdf(percentile_cut, *param[:-2], loc=param[-2], scale=param[-1])
        # Criando CDF Inversa 
        Ft_ = dist.ppf(percentile_cut, *param[:-2], loc=param[-2], scale=param[-1])

        # Adicionando dados do trace
        # for i in range(len(y)):
        #     y[i] = y[i]/np.mean(y)
        
        t_Fe = y


        # Criando listas para armazenar as ECDFs
        Fe = []
        Fe_ = []

        # Criando ECDFs
        for i in range(len(y)):
            # ecdf i-1/n
            Fe.append((i-1)/len(y))
            # ecdf i/n
            Fe_.append(i/len(y))

        # Transformando listas em np.arrays()
        Fe = np.array(Fe)
        Fe_ = np.array(Fe_)
        Ft = np.array(Ft)
        Ft_ = np.array(Ft_)


        # Ordenando dados
        t_Fe.sort()
        Ft.sort()
        Ft_.sort()
        Fe.sort()
        Fe_.sort()
        
        # Inicio cálculo de rejeição
        #
        # Ft(t)-FE-(i),FE+(i)-Ft(t)
        Ft_Fe_ = np.subtract(Ft, Fe_)
        Fe_Ft = np.subtract(Fe, Ft)
        
        # Max(Ft(t)-FE-(i),FE+(i)-Ft(t))
        Dcal_max = np.maximum(Ft_Fe_, Fe_Ft)
        
        # Dcal= Max(Max (Ft(t)-FE-(i),FE+(i)-Ft(t)))
        Dcal = np.max(Dcal_max)
        #
        # Fim cálculo de rejeição

        # Definir intervalo de confiança
        # IC = 99.90 -> alpha = 0.10
        # IC = 99.95 -> alpha = 0.05
        # IC = 99.975 -> alpha = 0.025
        # IC = 99.99 -> alpha = 0.01
        # IC = 99.995 -> alpha = 0.005
        # IC = 99.999 -> alpha = 0.001
        IC = 99.90
        
        # Condição para definir o D_critico de acordo com o tamanho dos dados
        if size > 35:
            if IC == 99.90:
                D_critico = 1.22/np.sqrt(len(y))
            
            if IC == 99.95:
                D_critico = 1.36/np.sqrt(len(y))
            
            if IC == 99.975:
                D_critico = 1.48/np.sqrt(len(y))
            
            if IC == 99.99:
                D_critico = 1.63/np.sqrt(len(y))
            
            if IC == 99.995:
                D_critico = 1.73/np.sqrt(len(y))
            if IC == 99.999:
                D_critico = 1.95/np.sqrt(len(y))

            # Condição para aceitar a hipótese nula do teste KS
            if Dcal > D_critico:
                rejects = "Reject the Null Hypothesis"
            else:
                rejects = "Fails to Reject the Null Hypothesis"

        # Imprimindo resultados do KS Test
        print("KS TEST:")
        print("Confidence degree: ", IC,"%")
        print(rejects, " of ", distribution)
        print("D observed: ", Dcal)
        print("D critical: ", D_critico)
        print(" ")
  
        # Obtém a estatística do teste KS e arredondar para 5 casas decimais
        Dcal = np.around(Dcal,  5)
        ks_values.append(Dcal)    

        # Obter contagens esperadas nos percentis
        # Isso se baseia em uma 'função de distribuição acumulada' (cdf)
        cdf_fitted = dist.cdf(percentile_cutoffs, *param[:-2], loc=param[-2], scale=param[-1])
        
        # Definindo a frequência esperada
        expected_frequency = []
        for bin in range(len(percentile_bins)-1):
            expected_cdf_area = cdf_fitted[bin+1] - cdf_fitted[bin]
            expected_frequency.append(expected_cdf_area)

        # Calculando o qui-quadrado
        expected_frequency = np.array(expected_frequency) * size
        cum_expected_frequency = np.cumsum(expected_frequency)
        ss = sum (((cum_expected_frequency - cum_observed_frequency) ** 2) / cum_observed_frequency)
        chi_square.append(ss)

        # Set x² with IC
        IC = IC/100
        x2 = chi2.ppf(IC, nbins-1)
        
        # Imprimindo resultados do teste Chi-square
        print("Chi-square test: ")
        print("Confidence degree: ", IC,"%")
        print("CS: ", ss)
        print("X²: ", x2)
        # Condição para aceitar a hipótese nula do teste Chi-square
        if x2 > ss:
            print("Fails to Reject the Null Hipothesis of ", distribution)
        else:
            print("Rejects the Null Hipothesis of ", distribution)
        print(" ")

    # Agrupar os resultados e classificar por qualidade de ajuste de acordo com o teste KS (melhor na parte superior)
    results = pd.DataFrame()
    results['Distribution'] = dist_names
    results['ks_value'] = ks_values
    results['chi_square'] = chi_square
    results.sort_values(['ks_value'], inplace=True, ascending=True)

    # Apresentar os resultados em uma tabela
    print ('\nDistributions sorted by KS Test:')
    print ('----------------------------------------')
    print (results)

    # Divida os dados observados em N posições para plotagem (isso pode ser alterado)
    bin_cutoffs = np.linspace(np.percentile(y,0), np.percentile(y,99), nbins)

    # Crie o gráfico
    h = plt.hist(y, bins = bin_cutoffs, color='0.75')

    # Receba as principais distribuições da fase anterior 
    # e seleciona a quantidade de distribuições.
    number_distributions_to_plot = 1
    dist_names = results['Distribution'].iloc[0:number_distributions_to_plot]

    # Crie uma lista vazia para armazenar parâmetros de distribuição ajustada
    parameters = []
    
    # Faça um loop pelas distribuições para obter o ajuste e os parâmetros da linha
    for dist_name in dist_names:
        # Chamando variáveis globais
        global arg_time
        global loc_time
        global scale_time
        global dist_time

        global arg_size
        global loc_size
        global scale_size
        global dist_size
        
        # Obtendo distribuições e seus parametros de acordo com o trace
        dist = getattr(scipy.stats, dist_name)
        param = dist.fit(y)
        parameters.append(param)

        arg = param[:-2]
        loc = param[-2]
        scale = param[-1]
        print(arg)
        if parameter == "Time":
            dist_time = dist_name
            loc_time = loc
            scale_time = scale
            arg_time = arg

        if parameter == "Size":
            dist_size = dist_name
            loc_size = loc
            scale_size = scale
            arg_size = arg

        # Obter linha para cada distribuição (e dimensionar para corresponder aos dados observados)
        pdf_fitted = dist.pdf(x, *param[:-2], loc=param[-2], scale=param[-1])
        scale_pdf = np.trapz (h[0], h[1][:-1]) / np.trapz (pdf_fitted, x)
        pdf_fitted *= scale_pdf
        
        # Adicione a linha ao gráfico
        plt.plot(pdf_fitted, label=dist_name)

        # Defina o eixo gráfico x para conter 99% dos dados
        # Isso pode ser removido, mas, às vezes, dados fora de padrão tornam o gráfico menos claro
        plt.xlim(0,np.percentile(y,99))
        plt.title("Histogram of trace (" + parameter + ") + theorical distribuition " + dist_name)
    # Adicionar legenda
    plt.legend()
    plt.show()

    # Armazenar parâmetros de distribuição em um quadro de dados (isso também pode ser salvo)
    dist_parameters = pd.DataFrame()
    dist_parameters['Distribution'] = (
            results['Distribution'].iloc[0:number_distributions_to_plot])
    dist_parameters['Distribution parameters'] = parameters

    # Printar os parâmetros
    print ('\nDistribution parameters:')
    print ('------------------------')

    for row in dist_parameters.iterrows():
        print ('\nDistribution:', row[0])
        print ('Parameters:', row[1] )

    
    # Plotando gráficos de inferência
    data = y_std.copy()
    # data = y

    data.sort()
    # Loop through selected distributions (as previously selected)
    
    for distribution in dist_names:
        # Set up distribution
        dist = getattr(scipy.stats, distribution)
        print("Dist: ",dist)
        param = dist.fit(y_std)

        print("MAX: ", max(y))
        print("PARAM: ", param)
        print("arg: ", *param[0:-2])
        print("loc: ", param[-2])
        print("scale: ", param[-1])
        print("Dist: ", dist)
        arg = param[:-2]
        loc = param[-2]
        scale = param[-1]

        #
        # KS TEST
        #
        # Criando percentil
        percentile = np.linspace(0,100,len(y_std))
        percentile_cut = np.percentile(y_std, percentile)
        
        # Criando CDF da teórica
        Ft = dist.cdf(percentile_cut, *param[:-2], loc=param[-2], scale=param[-1])
        # Criando CDF Inversa 
        Ft_ = dist.ppf(percentile_cut, *param[:-2], loc=param[-2], scale=param[-1])

        # Adicionando dados do trace
        t_Fe = y

        # Ordenando dados
        t_Fe.sort()
        Ft.sort()
        Ft_.sort()

        # Criando listas para armazenar as ECDFs
        Fe = []
        Fe_ = []

        # Criando ECDFs
        for i in range(len(y)):
            # ecdf i-1/n
            Fe.append((i-1)/len(y))
            # ecdf i/n
            Fe_.append(i/len(y))

        # Transformando listas em np.arrays()
        Fe = np.array(Fe)
        Fe_ = np.array(Fe_)
        Ft = np.array(Ft)
        Ft_ = np.array(Ft_)
        
        # Inicio cálculo de rejeição
        #
        # Ft(t)-FE-(i),FE+(i)-Ft(t)
        Ft_Fe_ = np.subtract(Ft, Fe_)
        Fe_Ft = np.subtract(Fe, Ft)
        
        # Max(Ft(t)-FE-(i),FE+(i)-Ft(t))
        Dcal_max = np.maximum(Ft_Fe_, Fe_Ft)
        
        # Dcal= Max(Max (Ft(t)-FE-(i),FE+(i)-Ft(t)))
        Dcal = np.max(Dcal_max)
        #
        # Fim cálculo de rejeição

        # Definir intervalo de confiança
        # IC = 99.90 -> alpha = 0.10
        # IC = 99.95 -> alpha = 0.05
        # IC = 99.975 -> alpha = 0.025
        # IC = 99.99 -> alpha = 0.01
        # IC = 99.995 -> alpha = 0.005
        # IC = 99.999 -> alpha = 0.001
        IC = 99.95        
        # Condição para definir o D_critico de acordo com o tamanho dos dados
        if size > 35:
            if IC == 99.90:
                D_critico = 1.22/np.sqrt(len(y))
            
            if IC == 99.95:
                D_critico = 1.36/np.sqrt(len(y))
            
            if IC == 99.975:
                D_critico = 1.48/np.sqrt(len(y))
            
            if IC == 99.99:
                D_critico = 1.63/np.sqrt(len(y))
            
            if IC == 99.995:
                D_critico = 1.73/np.sqrt(len(y))
            if IC == 99.999:
                D_critico = 1.95/np.sqrt(len(y))

            # Condição para aceitar a hipótese nula do teste KS
            if Dcal > D_critico:
                rejects = "Reject the Null Hypothesis"
            else:
                rejects = "Fails to Reject the Null Hypothesis"

        # Imprimindo resultados do KS Test
        print("KS TEST:")
        print("Confidence degree: ", IC,"%")
        print(rejects, " of ", distribution)
        print("D observed: ", Dcal)
        print("D critical: ", D_critico)
        print(" ")

        # Plotando resultados do teste KS
        plt.plot(t_Fe, Fe, 'o', label='Empirical Distribution')
        plt.plot(t_Fe, Ft, 'o', label='Teorical Distribution')
        
        # Definindo titulo
        plt.title("KS Test of Real Trace with " + distribution + " Distribution (" + parameter + ")")
        plt.legend()
        plt.show() 

        global first_tcdf_time
        global first_tcdf_size

        if parameter == "Size":
            first_tcdf_size = 1
        if parameter == "Time":
            first_tcdf_time = 1

# Função de geração de variáveis aleatórias por meio da TCDF
def tcdf_generate(dist, loc, scale, arg, parameter):
    # Setar distribuição escolhida.
    dist_name = getattr(scipy.stats, dist)

    # Gerar número aleatório de acordo com a distribuição escolhida e seus parametros.
    r_N = dist_name.rvs(loc=loc, scale=scale, *arg)

    # Condição para retorno do valor de acordo com o parametro de rede.
    if parameter == "Size":
        # print("SIZE R_N:", r_N)
        return(int(r_N))

    if parameter == "Time":
        # print("TIME R_N:", r_N)
        return(float(r_N))

# Função de geração de variáveis aleatórias de acordo com distribuições 
# de probabilidade e parametros definidos
def wgwnet_PD(loc, scale, arg, dist_name, parameter):
    # Mais distribuições podem ser encontradas no site da lib "scipy"
    # Veja https://docs.scipy.org/doc/scipy/reference/stats.html para mais detalhes
    
    # Setando distribuição a escolhida e seus parametros 
    dist = getattr(scipy.stats, dist_name)

    # Gerando número aleatório de acordo com a distribuiução e os parametros definidos
    r_N = dist.rvs(loc=loc, scale=scale, *arg, size=1)
    
    # Condição para retorno do valor de acordo com o parametro de rede.
    if parameter == "Size":
        # print("SIZE R_N: ", int(r_N))
        return(int(r_N))
    if parameter == "Time":
        # print("TIME R_N: ", r_N)
        return(float(r_N))

# Classe de criação da aplicação do NS3
class MyApp(ns3.Application):
    # Criando variáveis auxiliares
    tid = ns3.TypeId("MyApp")
    tid.SetParent(ns3.Application.GetTypeId())
    m_socket = m_packetSize = m_nPackets = m_dataRate = m_packetsSent = 0
    m_peer = m_sendEvent = None
    m_running = False
    
    count_Setup = count_Start = count_Stop = count_SendPacket = count_ScheduleTx = count_GetSendPacket = count_GetTypeId = 0
    # Inicializador da simulação
    def __init__(self):
        super(MyApp, self).__init__()
    # def Setup(self, socket, address, packetSize, nPackets, dataRate):

    # Função de configuração da aplicação
    def Setup(self, socket, address, nPackets):
        self.count_Setup = self.count_Setup + 1
        self.m_socket = socket
        self.m_peer = address
        # self.m_packetSize = packetSize
        self.m_nPackets = nPackets
        # self.m_dataRate = dataRate

    # Função de inicialização da aplicação
    def StartApplication(self):
        self.count_Start = self.count_Start + 1
        if self.m_nPackets > 0 and self.m_nPackets > self.m_packetsSent:
            self.m_running = True
            self.m_packetsSent = 0
            self.m_socket.Bind()
            self.m_socket.Connect(self.m_peer)
            self.SendPacket()
        else:
            self.StopApplication()
    
    # Função de parada da aplicação
    def StopApplication(self):
        self.count_Stop = self.count_Stop + 1
        self.m_running = False
        if self.m_sendEvent != None and self.m_sendEvent.IsRunning() == True:
            ns3.Simulator.Cancel(self.m_sendEvent)
        if self.m_socket:
            self.m_socket.Close()

    # Função de envio de pacotes
    def SendPacket(self):
        # Contabiliza a quantidade de pacotes enviados
        self.count_SendPacket = self.count_SendPacket + 1
        
        # Chamando variáveis globais
        
        # Método de Geração de RN
        global mt_RG
        
        # Metodo de geração de RN por trace
        global tr_RG
        
        # Vetor com dados do parametro de tamanho dos pacotes obtidos do trace
        global t_size
        
        global parameter
        global arg_size
        global scale_size
        global loc_size
        global dist_size

        global first_tcdf_size
        global first_trace_size
        global size_ns3
        parameter = "Size"
        
        # Condição de escolha do método de geração de variáveis aleatórias 
        # diretamente por uma distribuição de probabiidade
        if mt_RG == "PD":
            # Selecionando distribuição de probabilidade
            dist_name = 'uniform'
            # Definindo parametros da distribuição
            loc = 1000
            scale = 1024
            arg = []
            
            # Chamando a função wgwnet_PD() e retornando valor gerado para uma variável auxiliar
            aux_packet = wgwnet_PD(loc,scale, arg, dist_name, parameter)
            
            # Transformando a variávei auxiliar em um metadado de pacote
            packet = ns3.Packet(aux_packet)

            # Concatenando valor gerado
            size_ns3.append(aux_packet)
        
        # Condição de escolha do método de geração de variáveis aleatórias 
        # baseado nos dados do trace
        if mt_RG == "Trace":
            
            # Condição de chamada única da função read_trace()
            if first_trace_size == 0:
                read_trace(parameter)
            
            # Condição de escolha do método por distribuições teórica equivalentes aos dados do trace
            if tr_RG == "tcdf":
                # Condição de chamada única da função tcdf()
                if first_tcdf_size == 0:
                    # Chamando a função tcdf para definir a distribuição de probabilidade compatível ao trace e 
                    # seus respectivos parametros para geração de números aleatórios
                    tcdf(t_size, parameter)

                # Chamando a função tcdf_generate e retornando valor gerado para uma variável auxiliar
                aux_packet = tcdf_generate(dist_size, loc_size, scale_size, arg_size, parameter)

                # Transformando a variávei auxiliar em um metadado de pacote
                packet = ns3.Packet(aux_packet)
                
                # Concatenando valor gerado
                size_ns3.append(aux_packet)

            # Condição de escolha do método pela distribuição empírica dos dados do trace
            if tr_RG == "ecdf":
                # Chamando a função ecdf e retornando valor gerado para uma variável auxiliar
                aux_packet = ecdf(t_size, parameter)

                # Transformando a variávei auxiliar em um metadado de pacote
                packet = ns3.Packet(aux_packet)

                # Concatenando valor de tamanho de pacote gerado
                size_ns3.append(aux_packet)
        print("PACKET: ", packet)
        # Imprimindo o tempo de envio do pacote e a quantidade de pacotes enviados
        print ("SendPacket(): ", str(ns3.Simulator.Now().GetSeconds()), "s,\t send ", str(self.m_packetsSent), "#")
        
        # Configurando o socket da rede para enviar o pacote
        self.m_socket.Send(packet, 0)
        
        # Incrementando a quantidade de pacotes enviados
        self.m_packetsSent = self.m_packetsSent + 1
        
        # Condição de parada da aplicação pela quantidade máxima de pacotes
        if self.m_packetsSent < self.m_nPackets:
            self.ScheduleTx()
        else:
            self.StopApplication()
    
    # Função que prepara os eventos de envio de pacotes
    def ScheduleTx(self):
        # Contabiliza a quantidade eventos que ocorrem na simulação
        self.count_ScheduleTx = self.count_ScheduleTx + 1

        # Condição que define se a aplicação ainda terá eventos
        if self.m_running:
            # Chamando variáveis globais
            # Auxiliar de tempo
            global aux_global_time
            # Método de Geração de RN
            global mt_RG
            
            # Metodo de geração de RN por trace
            global tr_RG
            
            # Vetor com dados do parametro de tamanho dos pacotes obtidos do trace
            
            global t_time
            global parameter
            global arg_time
            global scale_time
            global loc_time
            global dist_time

            global first_tcdf_time
            global first_trace_time
            global time_ns3
            parameter = "Time"
             # Condição de escolha do método de geração de variáveis aleatórias 
            # diretamente por uma distribuição de probabiidade
            if mt_RG == "PD":
                # Selecionando distribuição de probabilidade
                dist_name = 'uniform'
                # Definindo parametros da distribuição
                loc = 0.1
                scale = 1
                arg = []
                # Chamando a função wgwnet_PD() e retornando valor gerado para uma variável auxiliar
                aux_global_time = wgwnet_PD(loc, scale, arg, dist_name, parameter)
                
            # Condição de escolha do método de geração de variáveis aleatórias 
            # baseado nos dados do trace
            if mt_RG == "Trace":

                # Condição de chamada única da função read_trace()
                if first_trace_time == 0:
                    read_trace(parameter)
                
                # Condição de escolha do método por distribuições teórica equivalentes aos dados do trace
                if tr_RG == "tcdf":
                    # Condição de chamada única da função tcdf()
                    if first_tcdf_time == 0:
                        # Chamando a função tcdf para definir a distribuição de probabilidade compatível ao trace e 
                        # seus respectivos parametros para geração de números aleatórios
                        tcdf(t_time, parameter)
                    
                    # Chamando a função tcdf_generate e retornando valor gerado para uma variável auxiliar
                    aux_global_time = tcdf_generate(dist_time, loc_time, scale_time, arg_time, parameter)
                
                # Condição de escolha do método pela distribuição empírica dos dados do trace
                if tr_RG == "ecdf":
                    # Chamando a função ecdf e retornando valor gerado para uma variável auxiliar
                    aux_global_time = ecdf(t_time, parameter)

            # Concatenando o valor de tempo gerado
            time_ns3.append(aux_global_time)

            # Transformando a variávei auxiliar em um metadado de tempo 
            tNext = ns3.Seconds(aux_global_time)
            print("TIME: ", tNext)
            # dataRate = "1Mbps"
            # packetSize = 1024
            # tNext = ns3.Seconds(packetSize * 8.0 / ns3.DataRate(dataRate).GetBitRate())
            # print("tNEXT: ", tNext)

            # Criando evento de envio de pacote
            self.m_sendEvent = ns3.Simulator.Schedule(tNext, MyApp.SendPacket, self)

    def GetSendPacket(self):
        self.count_GetSendPacket = self.count_GetSendPacket + 1
        return self.m_packetsSent

    def GetTypeId(self):
        self.count_GetTypeId = self.count_GetTypeId + 1
        return self.tid

# Função de definição da janela de congestionamento
def CwndChange(app):
	# CwndChange(): 
	n = app.GetSendPacket()
	print ('CwndChange(): ' + str(ns3.Simulator.Now().GetSeconds()) + 's, \t sum(send packets) = ' + str(n))
	ns3.Simulator.Schedule(ns3.Seconds(1), CwndChange, app)

# def ChangeRate(self, ns3.DataRate newrate):
#     newrate = "1Mbps"
#     self.m_dataRate = newrate

# def IncRate(self, app):

    # app.ChangeRate(self.m_dataRate)

# Função de impressão dos resultados da simulação do NS3
def print_stats(os, st):
    # os = open("stats.txt", "w")
    print (os, "  Tx Bytes: ", st.txBytes)
    print (os, "  Rx Bytes: ", st.rxBytes)
    print (os, "  Tx Packets: ", st.txPackets)
    print (os, "  Rx Packets: ", st.rxPackets)
    print (os, "  Lost Packets: ", st.lostPackets)
    if st.rxPackets > 0:
        print (os, "  Mean{Delay}: ", (st.delaySum.GetSeconds() / st.rxPackets))
        print (os, "  Mean{Jitter}: ", (st.jitterSum.GetSeconds() / (st.rxPackets)))
        print (os, "  Mean{Hop Count}: ", float(st.timesForwarded) / st.rxPackets + 1)

    if st.rxPackets == 0:
        print (os, "Delay Histogram")
        for i in range(st.delayHistogram.GetNBins()):
            print (os, " ", i, "(", st.delayHistogram.GetBinStart(i), "-", st.delayHistogram.GetBinEnd(i), "): ", st.delayHistogram.GetBinCount(i))
        print (os, "Jitter Histogram")
        for i in range(st.jitterHistogram.GetNBins()):
            print (os, " ", i, "(", st.jitterHistogram.GetBinStart(i), "-", st.jitterHistogram.GetBinEnd(i), "): ", st.jitterHistogram.GetBinCount(i))
        print (os, "PacketSize Histogram")
        for i in range(st.packetSizeHistogram.GetNBins()):
            print (os, " ", i, "(", st.packetSizeHistogram.GetBinStart(i), "-", st.packetSizeHistogram.GetBinEnd(i), "): ", st.packetSizeHistogram.GetBinCount(i))

    for reason, drops in enumerate(st.packetsDropped):
        print ("  Packets dropped by reason ", reason ,": ", drops)
    # for reason, drops in enumerate(st.bytesDropped):
        # print "Bytes dropped by reason %i: %i" % (reason, drops)
# Função de leitura dos arquivos .pcap através do termshark
# def read_pcap():
#     # Lendo arquivo .pcap
#     os.system("cd")
#     os.system("sudo cp /WGNet/trace-files/trace1.pcap /repos/ns-3-allinone/ns-3.30/")
#     # Tornando arquivo editável e legível
#     os.system("chmod 777 trace1.pcap")
#     # Atribuindo valor do tamanho do pacote em um arquivo .txt 
#     os.system("termshark -r trace1.pcap -T fields -E separator=/t  -e ip.len > scratch/size_ns3.txt")
#     # Atribuindo valor do tempo de envio cada pacote em um arquivo .txt
#     os.system("termshark -r trace1.pcap -T fields -E separator=/t -e frame.time_delta_displayed > scratch/time_ns3.txt")
#     # Tornando arquivos editáveis e legíveis
#     os.system("chmod 777 scratch/size_ns3.txt")
#     os.system("chmod 777 scratch/time_ns3.txt")

# Função de comparação dos resultados obtidos com o NS3 com os dados dos traces
# Esta função é utilizada apenas quando o método de geração variáveis aleatórias selecionado é por "Trace"
def compare():
    # Chamando variáveis globais
    global t_time
    global t_size

    global time_ns3
    global size_ns3
    
    global parameter
    
    
    # Métodos de comparação dos traces 
    # Opções: "qq_e_pp", "Graphical" ou "KS"
    compare = ""
    # compare = "qq_e_pp"
    if compare == "qq_e_pp":
        #
        # qq and pp plots
        #
        # Dados do Traces:
        
        # Time
        sc_time = StandardScaler()
        # Tornando dados do vetor np.array()
        t_time = np.array(t_time)
        # Normalizando valores
        yy_time = t_time.reshape (-1,1)
        sc_time.fit(yy_time)
        y_std_time = sc_time.transform(yy_time)
        y_std_time = y_std_time.flatten()
        data_time = y_std_time.copy()
        data_time.sort()

        # Size
        sc_size = StandardScaler()
        # Tornando dados do vetor np.array()
        t_size = np.array(t_size)
        # Normalizando valores
        yy_size = t_size.reshape (-1,1)
        sc_size.fit(yy_size)
        y_std_size = sc_size.transform(yy_size)
        y_std_size = y_std_size.flatten()

        data_size = y_std_size.copy()
        data_size.sort()

        # Dados gerados no NS3:

        # Time
        sc_time_ns3 = StandardScaler()
        time_ns3 = np.array(time_ns3)
        yy_time_ns3 = time_ns3.reshape (-1,1)
        sc_time_ns3.fit(yy_time_ns3)
        y_std_time_ns3 = sc_time_ns3.transform(yy_time_ns3)
        y_std_time_ns3 = y_std_time_ns3.flatten()

        data_time_ns3 = y_std_time_ns3.copy()
        data_time_ns3.sort()

        # Size
        sc_size_ns3 = StandardScaler()
        size_ns3 = np.array(size_ns3)
        yy_size_ns3 = size_ns3.reshape (-1,1)
        sc_size_ns3.fit(yy_size_ns3)
        y_std_size_ns3 = sc_size_ns3.transform(yy_size_ns3)
        y_std_size_ns3 = y_std_size_ns3.flatten()

        data_size_ns3 = y_std_size_ns3.copy()
        data_size_ns3.sort()

        #
        # SIZE 
        #
        # Definindo o parametro da rede a ser comparado
        parameter = "Size"
        distribution = 'real trace of '+ parameter

        # Adicionando valores gerados pelo NS3
        x = size_ns3 
        # x = data_size_ns3

        # Adicionando valores do trace
        y = t_size
        # y = data_size
        
        # Ordenando dados
        x.sort()
        y.sort()
        
        # Tornando vetores do mesmo tamanho
        if len(x) > len(y):
            x = x[0:len(y)]
        if len(x) < len(y):
            y = y[0:len(x)]

        # Criando variável com tamanho dos dados
        S_size = len(x)
        # Criando variável com o número de bins (classes)
        S_nbins = int(np.sqrt(S_size))
        
        # Criando figura
        fig = plt.figure(figsize=(8,5)) 

        # Adicionando subplot com método "qq plot"
        ax1 = fig.add_subplot(121) # Grid of 2x2, this is suplot 1
        
        # Plotando dados comparados
        ax1.plot(x,y,"o")
        
        # Definindo valor máximo e mínimo dos dados
        min_value = np.floor(min(min(x),min(y)))
        max_value = np.ceil(max(max(x),max(y)))

        # Plotando linha qua segue do minimo ao máximo
        ax1.plot([min_value,max_value],[min_value,max_value],'r--')

        # Setando limite dos dados dentro do valor máximo e mínimo
        ax1.set_xlim(min_value,max_value)

        # Definindo os títulos dos eixos x e y 
        ax1.set_xlabel('Real Trace quantiles')
        ax1.set_ylabel('Observed quantiles in NS3')

        # Definindo o título do gráfico
        title = 'qq plot for ' + distribution +' distribution'
        ax1.set_title(title)

        # Adicionando subplot com método "pp plot"
        ax2 = fig.add_subplot(122)
        
        # Calculate cumulative distributions
        # Criando classes dos dados por percentis
        S_bins = np.percentile(x,range(0,S_nbins))

        # Obtendo conunts e o número de classes de um histograma dos dados
        y_counts, S_bins = np.histogram(y, S_bins)
        x_counts, S_bins = np.histogram(x, S_bins)
        # print("y_COUNTS: ",y_counts)
        # print("x_Counts: ",x_counts)
        # print("y_Counts: ",y_counts)
        
        # Gerando somatória acumulada dos dados
        cum_y = np.cumsum(y_counts)
        cum_x = np.cumsum(x_counts)
        # print("CUMSUM_DATA: ", cum_y)

        # Normalizando a somatória acumulada dos dados
        cum_y = cum_y / max(cum_y)
        cum_x = cum_x / max(cum_x)
        #print("Cum_y: ",cum_y)
        #print("Cum_x: ",cum_x)

        # plot
        # Plotando dados 
        ax2.plot(cum_x,cum_y,"o")
        
        # Obtendo valores máximos e minimos
        min_value = np.floor(min(min(cum_x),min(cum_y)))
        max_value = np.ceil(max(max(cum_x),max(cum_y)))
        
        # Plotando linha entre valor máximo e mínimo dos dados
        ax2.plot([min_value,max_value],[min_value,max_value],'r--')

        # Definindo o limite dos dados entre os valores máximos e mínimos
        ax2.set_xlim(min_value,max_value)

        # Definindo titulos dos eixos x e y
        ax2.set_xlabel('Real Trace cumulative distribution')
        ax2.set_ylabel('Observed in NS3 cumulative distribution')

        # Definindo titulo do gráfico
        title = 'pp plot for ' + distribution +' distribution'
        ax2.set_title(title)

        # Exibindo gráficos
        plt.tight_layout(pad=4)
        plt.show()


        #
        # TIME COMPARE
        #
        # Definindo o parametro da rede a ser comparado
        parameter = "Time"
        distribution = 'real trace of '+ parameter

        # Adicionando valores gerados pelo NS3
        x = time_ns3 
        # x = data_time_ns3

        # Adicionando valores do trace
        y = t_time
        y = data_time

        # Ordenando dados
        x.sort()
        y.sort()
        
        # Tornando vetores do mesmo tamanho
        if len(x) > len(y):
            x = x[0:len(y)]
        if len(x) < len(y):
            y = y[0:len(x)]

        # Criando variável com tamanho dos dados
        T_size = len(x)
        # Criando variável com o número de bins (classes)
        T_nbins = int(np.sqrt(T_size))
        
        # Criando figura
        fig = plt.figure(figsize=(8,5)) 

        # Adicionando subplot com método "qq plot"
        ax1 = fig.add_subplot(121) # Grid of 2x2, this is suplot 1
        
        # Plotando dados comparados
        ax1.plot(x,y,"o")
        
        # Definindo valor máximo e mínimo dos dados
        min_value = np.floor(min(min(x),min(y)))
        max_value = np.ceil(max(max(x),max(y)))

        # Plotando linha qua segue do minimo ao máximo
        ax1.plot([min_value,max_value],[min_value,max_value],'r--')

        # Setando limite dos dados dentro do valor máximo e mínimo
        ax1.set_xlim(min_value,max_value)

        # Definindo os títulos dos eixos x e y 
        ax1.set_xlabel('Real Trace quantiles')
        ax1.set_ylabel('Observed quantiles in NS3')

        # Definindo o título do gráfico
        title = 'qq plot for ' + distribution +' distribution'
        ax1.set_title(title)

        # Adicionando subplot com método "pp plot"
        ax2 = fig.add_subplot(122)
        
        # Calculate cumulative distributions
        # Criando classes dos dados por percentis
        T_bins = np.percentile(x,range(0,T_nbins))

        # Obtendo conunts e o número de classes de um histograma dos dados
        y_counts, T_bins = np.histogram(y, T_bins)
        x_counts, T_bins = np.histogram(x, T_bins)
        # print("y_COUNTS: ",y_counts)
        # print("x_Counts: ",x_counts)
        # print("y_Counts: ",y_counts)
        
        # Gerando somatória acumulada dos dados
        cum_y = np.cumsum(y_counts)
        cum_x = np.cumsum(x_counts)
        # print("CUMSUM_DATA: ", cum_y)

        # Normalizando a somatória acumulada dos dados
        cum_y = cum_y / max(cum_y)
        cum_x = cum_x / max(cum_x)
        #print("Cum_y: ",cum_y)
        #print("Cum_x: ",cum_x)

        # plot
        # Plotando dados 
        ax2.plot(cum_x,cum_y,"o")
        
        # Obtendo valores máximos e minimos
        min_value = np.floor(min(min(cum_x),min(cum_y)))
        max_value = np.ceil(max(max(cum_x),max(cum_y)))
        
        # Plotando linha entre valor máximo e mínimo dos dados
        ax2.plot([min_value,max_value],[min_value,max_value],'r--')

        # Definindo o limite dos dados entre os valores máximos e mínimos
        ax2.set_xlim(min_value,max_value)

        # Definindo titulos dos eixos x e y
        ax2.set_xlabel('Real Trace cumulative distribution')
        ax2.set_ylabel('Observed in NS3 cumulative distribution')

        # Definindo titulo do gráfico
        title = 'pp plot for ' + distribution +' distribution'
        ax2.set_title(title)

        # Exibindo gráficos
        plt.tight_layout(pad=4)
        plt.show()
    
    # compare = "Graphical"
    if compare == "Graphical":

        #
        # SIZE COMPARE
        #
        # Definindo o parametro da rede a ser comparado
        parameter = "Size"
        distribution = 'real trace of '+ parameter

        # Adicionando valores gerado pelo NS3
        x = size_ns3
        # Adicionando valores obtidos do trace
        y = t_size

        # Ordenando os valores
        x.sort()
        y.sort()
        
        # Tornando os vetores do mesmo tamanho
        if len(x) > len(y):
            x = x[0:len(y)]
        if len(x) < len(y):
            y = y[0:len(x)]
        
        # print("X size: ", len(x))
        # print("Y size: ", len(y))
        # print("X: ", x)
        # print("Y: ", y)

        # Plotando dados x e y
        plt.plot(x,y,"o")

        # Definindo polinomial de x e y
        z = np.polyfit(x, y, 1)

        # Gerando polinomial de 1d com os dados de z e x 
        y_hat = np.poly1d(z)(x)

        # Plotando linha tracejada 
        plt.plot(x, y_hat, "r--", lw=1)

        # Imprimindo resultados da regressão linear dos dados comparados
        text = f"$y={z[0]:0.6f}x{z[1]:+0.6f}$\n$R^2 = {r2_score(y,y_hat):0.6f}$"
        plt.gca().text(0.05, 0.95, text,transform=plt.gca().transAxes,
            fontsize=14, verticalalignment='top')
        # Definindo titulo do gráfico
        plt.title('Graphical Method inference for ' + distribution +' Distribution ' + '('+parameter+')')
        plt.show() 
        
        #
        # TIME COMPARE
        #
        # Definindo o parametro da rede a ser comparado
        parameter = "Time"
        distribution = 'real trace of '+ parameter
        
        # Adicionando valores gerado pelo NS3
        x = time_ns3
        # Adicionando valores obtidos do trace
        y = t_time

        # Ordenando os valores
        x.sort()
        y.sort()
        
        # Tornando os vetores do mesmo tamanho
        if len(x) > len(y):
            x = x[0:len(y)]
        if len(x) < len(y):
            y = y[0:len(x)]
        
        # print("X size: ", len(x))
        # print("Y size: ", len(y))
        # print("X: ", x)
        # print("Y: ", y)

        # Plotando dados x e y
        plt.plot(x,y,"o")

        # Definindo polinomial de x e y
        z = np.polyfit(x, y, 1)

        # Gerando polinomial de 1d com os dados de z e x 
        y_hat = np.poly1d(z)(x)

        # Plotando linha tracejada 
        plt.plot(x, y_hat, "r--", lw=1)

        # Imprimindo resultados da regressão linear dos dados comparados
        text = f"$y={z[0]:0.6f}x{z[1]:+0.6f}$\n$R^2 = {r2_score(y,y_hat):0.6f}$"
        plt.gca().text(0.05, 0.95, text,transform=plt.gca().transAxes,
            fontsize=14, verticalalignment='top')
        # Definindo titulo do gráfico
        plt.title('Graphical Method inference for ' + distribution +' Distribution ' + '('+parameter+')')
        plt.show() 

    compare = "KS"
    if compare == "KS":
        #
        # KS TEST
        #
          
        #
        # Size
        #

        # Definindo o parametro da rede a ser comparado
        parameter = "Size"

        # Adicionando valores do trace
        Ft = t_size
        
        # Adocionando valores obtidos do NS3
        t_Fe = size_ns3


        # Ordenando valores 
        t_Fe.sort()
        Ft.sort()

        # print("FT: ", Ft)
        # print("t_Fe: ", t_Fe)
        
        # Criando listas para a ecdf
        Fe = []
        Fe_ = []
        
        # Definindo mesmo tamanho para os vetores
        if len(Ft) > len(t_Fe):
            Ft = Ft[0:len(t_Fe)]
        if len(Ft) < len(t_Fe):
            t_Fe = t_Fe[0:len(Ft)]
        
        # Criando ECDFs
        for i in range(len(Ft)):
            # ecdf i-1/n
            Fe.append((i-1)/len(Ft))
            # ecdf i/n
            Fe_.append(i/len(Ft))

        # Trandformando vetorem em np.arrays()
        Fe = np.array(Fe)
        Fe_ = np.array(Fe_)
        Ft = np.array(Ft)
        t_Fe = np.array(t_Fe)
        
        # Plotando resultados do teste KS
        plt.plot(t_Fe, Fe, 'o', label='Real Trace')
        plt.plot(Ft, Fe, 'o', label='Syntatic Trace')
        
        # Definindo titulo
        plt.title("KS test of Real Trace and Syntatic Trace" + ' ('+parameter+')')
        plt.legend()
        plt.show()  

        #
        # Time
        #
        # Definindo o parametro da rede a ser comparado
        parameter = "Time"

        # Adicionando valores do trace
        Ft = t_time

        # Adocionando valores obtidos do NS3
        t_Fe = time_ns3

        # Ordenando valores 
        t_Fe.sort()
        Ft.sort()

        # print("FT: ", Ft)
        # print("t_Fe: ", t_Fe)
        
        # Criando listas para a ecdf
        Fe = []
        Fe_ = []
        
        # Definindo mesmo tamanho para os vetores
        if len(Ft) > len(t_Fe):
            Ft = Ft[0:len(t_Fe)]
        if len(Ft) < len(t_Fe):
            t_Fe = t_Fe[0:len(Ft)]
        
        # Criando ECDFs
        for i in range(len(Ft)):
            # ecdf i-1/n
            Fe.append((i-1)/len(Ft))
            # ecdf i/n
            Fe_.append(i/len(Ft))

        # Trandformando vetorem em np.arrays()
        Fe = np.array(Fe)
        Fe_ = np.array(Fe_)
        Ft = np.array(Ft)
        t_Fe = np.array(t_Fe)
        
        # Plotando resultados do teste KS
        plt.plot(t_Fe, Fe, 'o', label='Real Trace')
        plt.plot(Ft, Fe, 'o', label='Syntatic Trace')
        
        # Definindo titulo
        plt.title("KS test of Real Trace and Syntatic Trace" + ' ('+parameter+')')
        plt.legend()
        plt.show() 

# Função principal do código
def main(argv):
    global tr_reader
    # Função para leitura de arquivos .pcap
    # if tr_reader == False:
    #     read_pcap()
    
    # Obtendo informações por linha de comando
    cmd = ns.core.CommandLine ()
    cmd.nPackets = 0
    cmd.timeStopSimulation = 10
    cmd.AddValue ("nPackets", "Número de pacotes enviados")
    cmd.AddValue ("timeStopSimulation", "Tempo final da simulação")
    cmd.Parse (sys.argv)
    # Definindo a quantidade de pacotes
    nPackets = int (cmd.nPackets)
    # Definindo o tempo de parada da simulação
    timeStopSimulation = float (cmd.timeStopSimulation)

    # packetSize = 1040
    # nPackets = 500
    # dataRate = "1Mbps"

    # Habilita todas as notificações no NS3
    ns3.LogComponentEnableAll(ns3.LOG_INFO)

    # enableRts = True

    # if enableRts == False:
    #     ns.core.Config.SetDefault ("ns3::WifiRemoteStationManager::RtsCtsThreshold", ns.core.StringValue ("999999"))	
    # else:
    #     ns.core.Config.SetDefault ("ns3::WifiRemoteStationManager::RtsCtsThreshold", ns.core.StringValue ("0"))    
        
    # ns.core.Config.SetDefault ("ns3::WifiRemoteStationManager::FragmentationThreshold", ns.core.StringValue ("990000"))

    # Set the maximum wireless range to 5 meters in order to reproduce a hidden nodes scenario, i.e. the distance between hidden stations is larger 	than 5 meters
    # ns.core.Config.SetDefault ("ns3::RangePropagationLossModel::MaxRange", ns.core.DoubleValue (10))

    wifiStaNodes = ns.network.NodeContainer ()
    wifiStaNodes.Create (2)

    wifiApNode = ns.network.NodeContainer ()
    wifiApNode.Create (1)

    channel = ns.wifi.YansWifiChannelHelper.Default ()
    # channel.AddPropagationLoss ("ns3::RangePropagationLossModel") # wireless range limited to 5 meters!

    phy = ns.wifi.YansWifiPhyHelper.Default ()
    phy.SetPcapDataLinkType (ns.wifi.YansWifiPhyHelper.DLT_IEEE802_11_RADIO)
    phy.SetChannel (channel.Create ())

    wifi = ns.wifi.WifiHelper ()
    wifi.SetStandard (ns.wifi.WIFI_PHY_STANDARD_80211n_5GHZ)
    wifi.SetRemoteStationManager ("ns3::ConstantRateWifiManager", "DataMode", ns.core.StringValue ("HtMcs7"), 
                                                                  "ControlMode", ns.core.StringValue ("HtMcs0"))
    mac = ns.wifi.WifiMacHelper ()

    ssid = ns.wifi.Ssid ("simple-mpdu-aggregation")
    mac.SetType ("ns3::StaWifiMac",
                "Ssid", ns.wifi.SsidValue (ssid),
                "ActiveProbing", ns.core.BooleanValue (False),
                "BE_MaxAmpduSize", ns.core.UintegerValue (10))

    staDevices = ns.network.NetDeviceContainer ()
    staDevices = wifi.Install (phy, mac, wifiStaNodes)

    mac.SetType ("ns3::ApWifiMac",
                "Ssid", ns.wifi.SsidValue (ssid),
                "EnableBeaconJitter", ns.core.BooleanValue (False),
                "BE_MaxAmpduSize", ns.core.UintegerValue (10))

    apDevice = ns.network.NetDeviceContainer ()
    apDevice = wifi.Install (phy, mac, wifiApNode)

    mobility = ns.mobility.MobilityHelper ()
    positionAlloc = ns.mobility.ListPositionAllocator ()

    positionAlloc.Add (ns.core.Vector3D (5.0, 0.0, 0.0))
    positionAlloc.Add (ns.core.Vector3D (5.0, 1.0, 0.0))
    positionAlloc.Add (ns.core.Vector3D (5.0, 0.0, 0.0))
    mobility.SetPositionAllocator (positionAlloc)

    mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel")
    mobility.Install (wifiApNode)
    mobility.Install (wifiStaNodes)

    stack = ns.internet.InternetStackHelper ()
    stack.Install (wifiApNode)
    stack.Install (wifiStaNodes)

    # Definindo IP dos nós
    # address = ns.internet.Ipv4AddressHelper ()
    # address.SetBase (ns.network.Ipv4Address ("192.168.1.0"), ns.network.Ipv4Mask ("255.255.255.0"))
    # StaInterface = ns.internet.Ipv4InterfaceContainer ()
    # StaInterface = address.Assign (staDevices)
    # ApInterface = ns.internet.Ipv4InterfaceContainer ()
    # ApInterface = address.Assign (apDevice)

    # Definindo IP dos nós
    address = ns3.Ipv4AddressHelper()
    address.SetBase(ns3.Ipv4Address("10.1.1.0"), ns3.Ipv4Mask("255.255.255.0"))
    ApInterface = ns.internet.Ipv4InterfaceContainer ()
    ApInterface = address.Assign (apDevice)
    StaInterface = ns.internet.Ipv4InterfaceContainer ()
    StaInterface = address.Assign (staDevices)

    
    # # Definindo taxa de erro
    # em = ns3.RateErrorModel()
    # em.SetRate(1e-5)
    # # Definindo taxa de erro por uma distribuição uniform
    # em.SetRandomVariable(ns.core.UniformRandomVariable())
    # # Instalando taxa de erro no nó 1
    # devices.Get(1).SetAttribute("ReceiveErrorModel", ns3.PointerValue(em))

    # Application TCP
    sinkPort = 8080
    
    # Serve Application
    packetSinkHelper = ns3.PacketSinkHelper("ns3::TcpSocketFactory", ns3.InetSocketAddress(ns3.Ipv4Address.GetAny(), sinkPort))
    sinkApps = packetSinkHelper.Install(wifiApNode.Get(0))
    sinkApps.Start(ns3.Seconds(timeStopSimulation/2))
    sinkApps.Stop(ns3.Seconds(timeStopSimulation))

    # Client Application
    sinkAddress = ns3.Address(ns3.InetSocketAddress(ApInterface.GetAddress (0), sinkPort))
    ns3TcpSocket = ns3.Socket.CreateSocket(wifiStaNodes.Get(0), ns3.TcpSocketFactory.GetTypeId())
    app = MyApp()
    # def Setup(self, socket, address, packetSize, nPackets, dataRate):
    # app.Setup(ns3TcpSocket, sinkAddress, packetSize, nPackets, ns3.DataRate(dataRate))
    app.Setup(ns3TcpSocket, sinkAddress, nPackets)
    wifiStaNodes.Get(1).AddApplication(app)
    app.SetStartTime(ns3.Seconds(timeStopSimulation/2))
    app.SetStopTime(ns3.Seconds(timeStopSimulation))

    ns3.Simulator.Schedule(ns3.Seconds(1), CwndChange, app)


    # Application UDP
    sinkPort = 9
    # Aplicação do servidor
    packetSinkHelper = ns3.PacketSinkHelper("ns3::UdpSocketFactory", ns3.InetSocketAddress(ApInterface.GetAddress (0), sinkPort))
    # packetSinkHelper = ns.applications.UdpServerHelper (sinkPort)
    sinkApps = packetSinkHelper.Install(wifiApNode.Get(0))
    sinkApps.Start(ns3.Seconds(0.1))
    sinkApps.Stop(ns3.Seconds(timeStopSimulation/2))


    # Aplicação do cliente 0
    sinkAddress0 = ns3.Address(ns3.InetSocketAddress(ApInterface.GetAddress (0), sinkPort))
    # sinkAddress0 = ns.applications.UdpClientHelper (ApInterface.GetAddress (0), sinkPort)
    ns3UdpSocket0 = ns3.Socket.CreateSocket(wifiStaNodes.Get(1), ns3.UdpSocketFactory.GetTypeId())
    
    # Definindo aplicação na classe Myapp
    app0 = MyApp()

    # Chamando a função setup para configurar a aplicação 0
    # def Setup(self, socket, address, packetSize, nPackets, dataRate):
    app0.Setup(ns3UdpSocket0, sinkAddress0, nPackets)
    # Configurando app no nó 0
    wifiStaNodes.Get(1).AddApplication(app0)
    # Inicio da aplicação
    app0.SetStartTime(ns3.Seconds(1))
    # Término da aplicação
    app0.SetStopTime(ns3.Seconds(timeStopSimulation/2))

    # # Aplicação do cliente 1
    # sinkAddress1 = ns3.Address(ns3.InetSocketAddress(ApInterface.GetAddress (0), sinkPort))
    # # sinkAddress1 = ns.applications.UdpClientHelper (ApInterface.GetAddress (0), sinkPort)
    # ns3UdpSocket1 = ns3.Socket.CreateSocket(wifiStaNodes.Get(1), ns3.UdpSocketFactory.GetTypeId())
    # # Definindo aplicação na classe Myapp 1
    # app1 = MyApp()

    # # Chamando a função setup para configurar a aplicação 1
    # # def Setup(self, socket, address, packetSize, nPackets, dataRate):
    # app1.Setup(ns3UdpSocket1, sinkAddress1, nPackets)
    # # Configurando app no nó 1
    # wifiStaNodes.Get(1).AddApplication(app1)
    # # Inicio da aplicação
    # app1.SetStartTime(ns3.Seconds((timeStopSimulation/2)+1))
    # # Término da aplicação
    # app1.SetStopTime(ns3.Seconds(timeStopSimulation))

    # ns3.Simulator.Schedule(ns3.Seconds(3), IncRate, app, ns3.DataRate(dataRate))

    # Inicializando Flowmonitor
    flowmon_helper = ns3.FlowMonitorHelper()
    # Instalando Flowmonitor em todos os nós
    monitor = flowmon_helper.InstallAll()
    monitor.SetAttribute("DelayBinWidth", ns3.DoubleValue(1e-3))
    monitor.SetAttribute("JitterBinWidth", ns3.DoubleValue(1e-3))
    monitor.SetAttribute("PacketSizeBinWidth", ns3.DoubleValue(20))
    monitor.SerializeToXmlFile ("Myapp-wifi-py.xml", True, True)

    # Gerador de .pcap da rede
    # p2p.EnablePcapAll("fifth")
    # ascii = ns3.AsciiTraceHelper().CreateFileStream("myapp-py.tr")
    # p2p.EnableAsciiAll(ascii)
    # p2p.EnablePcapAll ("myapp-py", True)

    # Controle de inicio e fim da simulação
    ns3.Simulator.Stop(ns3.Seconds(timeStopSimulation))
    ns3.Simulator.Run()
    ns3.Simulator.Destroy()
    

    # Chamando Flowmonitor para obter informações do fluxo
    monitor.GetAllProbes()
    classifier = flowmon_helper.GetClassifier()
    
    # Imprimir informações dos fluxos da rede
    flow_id = 0
    flow_stats = 0
    for flow_id, flow_stats in monitor.GetFlowStats():
        t = classifier.FindFlow(flow_id)
        proto = {6: 'TCP', 17: 'UDP'} [t.protocol]
        print ("FlowID: ", flow_id)
        print(proto)
        print(t.sourceAddress)
        print(t.sourcePort, " --> ")
        print(t.destinationAddress)
        print(t.destinationPort)
        print_stats(sys.stdout, flow_stats)
   
    
    global mt_RG

    if mt_RG == "Trace":
        compare()
    
 
    
if __name__ == '__main__':
    main(sys.argv)