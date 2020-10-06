# -*- Mode:Python; -*-
# /*
#  * This program is free software; you can redistribute it and/or modify
#  * it under the terms of the GNU General Public License version 2 as
#  * published by the Free Software Foundation
#  *
#  * This program is distributed in the hope that it will be useful,
#  * but WITHOUT ANY WARRANTY; without even the implied warranty of
#  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  * GNU General Public License for more details.
#  *
#  * You should have received a copy of the GNU General Public License
#  * along with this program; if not, write to the Free Software
#  * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#  */

## @file
#  @ingroup core-examples
#  @ingroup randomvariable
#  Demonstrate use of ns-3 as a random number generator integrated with
#  plotting tools.
#  
#  This is adapted from Gustavo Carneiro's ns-3 tutorial

import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point
import pandas as pd
import pandas as pd
import numpy as np
import scipy
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import statsmodels as sm
import scipy.stats as stats
import matplotlib.pyplot as plt
import os

# Desligando avisos
import warnings
warnings.filterwarnings("ignore")

aux_global_time = 0
def wgwnet():
    # Option "Trace" "PD" "SS"
    WGNet_Input = "PD"
    if WGNet_Input == "PD":
        data_set = np.loadtxt("scratch/time.txt", usecols=0)
        

        data_set = np.array(data_set)
        y = data_set
        print("Trace: ", y)

        # Indexar o vetor criado anteriormente Create an index array (x) for data

        x = np.arange(len(y))
        size = len(x)
        nbins = int(np.sqrt(size))

        #Plot histograma:
        plt.hist(y)
        plt.show()


        #Com ajuda da lib Pandas podemos encontrar algumas estatísticas importantes.
        y_df = pd.DataFrame(y, columns=['Data'])
        y_df.describe()
        
        # Variáveis para definir o método de geração de carga de trabalho por meio de Distribuições de Probabilidade
        cdf = []
        # Variável "para teorical cumulative distributin function"
        tcdf = True
        # Variável para "empirical cumulative distributin function"
        ecdf = False
        
        if tcdf:
            #Primeiro, vamos normalizar os dados
            sc=StandardScaler()
            yy = y.reshape (-1,1)
            sc.fit(yy)
            y_std = sc.transform(yy)
            y_std = y_std.flatten()
            y_std
            del yy

            #Python pode relatar avisos enquanto executa as distribuições

            # Mais distribuições podem ser encontradas no site do Scipy
            # Veja https://docs.scipy.org/doc/scipy/reference/stats.html para mais detalhes
            dist_names = ['beta',
                        'expon',
                        'gamma',
                        'lognorm',
                        'norm',
                        'loggamma',
                        'triang',
                        'uniform',
                        'weibull_min', 
                        'weibull_max',
                        'logistic',
                        'laplace',
                        'gamma',
                        'lognorm',
                        'loguniform']
            # Get the QQ and Chi-squared method of inference
            #Configurar listas vazias para receber os resultados
            chi_square = []
            p_values = []
            #--------------------------------------------------------#
            # Chi-square method
            
            # Configurar os 50 intervalos de classe para o teste qui-quadrado
            # Os dados observados serão distribuídos uniformemente em todos os inervalos de classes
            percentile_bins = np.linspace(0,100,nbins)
            percentile_cutoffs = np.percentile(y_std, percentile_bins)
            observed_frequency, bins = (np.histogram(y_std, bins=percentile_cutoffs))
            cum_observed_frequency = np.cumsum(observed_frequency)

            # Repetir para as distribuições candidatas
            for distribution in dist_names:
                # Configure a distribuição e obtenha parâmetros de distribuição ajustados
                dist = getattr(scipy.stats, distribution)
                param = dist.fit(y_std)

                # Obter a estatística P do teste KS, arredondar para 5 casas decimais
                p = scipy.stats.kstest(y_std, distribution, args=param)[1]
                p = np.around(p, 5)
                p_values.append(p)    

                # Obter contagens esperadas nos percentis
                # Isso se baseia em uma 'função de distribuição acumulada' (cdf)
                cdf_fitted = dist.cdf(percentile_cutoffs, *param[:-2], loc=param[-2], 
                                    scale=param[-1])
                expected_frequency = []
                for bin in range(len(percentile_bins)-1):
                    expected_cdf_area = cdf_fitted[bin+1] - cdf_fitted[bin]
                    expected_frequency.append(expected_cdf_area)

                # calculando o qui-quadrado
                expected_frequency = np.array(expected_frequency) * size
                cum_expected_frequency = np.cumsum(expected_frequency)
                ss = sum (((cum_expected_frequency - cum_observed_frequency) ** 2) / cum_observed_frequency)
                chi_square.append(ss)

            # Agrupar os resultados e classificar por qualidade de ajuste (melhor na parte superior)

            results = pd.DataFrame()
            results['Distribution'] = dist_names
            results['chi_square'] = chi_square
            results['p_value'] = p_values
            results.sort_values(['chi_square'], inplace=True)

            # Apresentar os resultados em uma tabela

            print ('\nDistributions sorted by goodness of fit:')
            print ('----------------------------------------')
            print (results)




            # Divida os dados observados em N posições para plotagem (isso pode ser alterado)
            bin_cutoffs = np.linspace(np.percentile(y,0), np.percentile(y,99), nbins)

            # Crie o gráfico
            h = plt.hist(y, bins = bin_cutoffs, color='0.75')

            # Receba as três principais distribuições da fase anterior
            number_distributions_to_plot = 1
            dist_names = results['Distribution'].iloc[0:number_distributions_to_plot]

            # Crie uma lista vazia para armazenar parâmetros de distribuição ajustada
            parameters = []

            # Faça um loop pelas distribuições para obter o ajuste e os parâmetros da linha
            for dist_name in dist_names:
                # Set up distribution and store distribution paraemters
                dist = getattr(scipy.stats, dist_name)
                param = dist.fit(y)
                parameters.append(param)

                # Obter linha para cada distribuição (e dimensionar para corresponder aos dados observados)
                pdf_fitted = dist.pdf(x, *param[:-2], loc=param[-2], scale=param[-1])
                scale_pdf = np.trapz (h[0], h[1][:-1]) / np.trapz (pdf_fitted, x)
                pdf_fitted *= scale_pdf

                # Adicione a linha ao gráfico
                plt.plot(pdf_fitted, label=dist_name)

                # Defina o eixo gráfico x para conter 99% dos dados
                # Isso pode ser removido, mas, às vezes, dados fora de padrão tornam o gráfico menos claro
                plt.xlim(0,np.percentile(y,99))

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

            for index, row in dist_parameters.iterrows():
                print ('\nDistribution:', row[0])
                print ('Parameters:', row[1] )


                # for dist_name in dist_names:
                # Set up distribution and store distribution paraemters
                dist = getattr(scipy.stats, row[0])
                parameters = row[1]
                
                arg = parameters[:-2]
                loc = parameters[-2]
                scale = parameters[-1]
            
                time = dist.rvs(loc=loc, scale=scale, *arg, size=1)
                
                print("RANDOM: ", time)
                aux_global_time = time




            #--------------------------------------------------------#
            ## qq and pp plots

            data = y_std.copy()
            data.sort()

            # Loop through selected distributions (as previously selected)

            for distribution in dist_names:
                # Set up distribution
                dist = getattr(scipy.stats, distribution)
                print("Dist: ",dist)
                param = dist.fit(y_std)

                # Get random numbers from distribution
                norm = dist.rvs(*param[0:-2],loc=param[-2], scale=param[-1],size = size)
                norm.sort()
                #print("Norm: ",norm)
                # Create figure
                fig = plt.figure(figsize=(8,5)) 

                # qq plot
                ax1 = fig.add_subplot(121) # Grid of 2x2, this is suplot 1
                ax1.plot(norm,data,"o")
                min_value = np.floor(min(min(norm),min(data)))
                max_value = np.ceil(max(max(norm),max(data)))
                ax1.plot([min_value,max_value],[min_value,max_value],'r--')
                ax1.set_xlim(min_value,max_value)
                ax1.set_xlabel('Theoretical quantiles')
                ax1.set_ylabel('Observed quantiles')
                title = 'qq plot for ' + distribution +' distribution'
                ax1.set_title(title)

                # pp plot
                ax2 = fig.add_subplot(122)
                #print("Norm: ",norm)
                # Calculate cumulative distributions
                bins = np.percentile(norm,range(0,nbins))
                #print("Bins: ", bins)
                data_counts, bins = np.histogram(data,bins)
                norm_counts, bins = np.histogram(norm,bins)
                #print("Norm_Counts: ",norm_counts)
                #print("Data_Counts: ",data_counts)
                cum_data = np.cumsum(data_counts)
                cum_norm = np.cumsum(norm_counts)

                cum_data = cum_data / max(cum_data)
                cum_norm = cum_norm / max(cum_norm)
                #print("Cum_data: ",cum_data)
                #print("Cum_norm: ",cum_norm)
                # plot
                ax2.plot(cum_norm,cum_data,"o")
                min_value = np.floor(min(min(cum_norm),min(cum_data)))
                max_value = np.ceil(max(max(cum_norm),max(cum_data)))
                ax2.plot([min_value,max_value],[min_value,max_value],'r--')
                ax2.set_xlim(min_value,max_value)
                ax2.set_xlabel('Theoretical cumulative distribution')
                ax2.set_ylabel('Observed cumulative distribution')
                title = 'pp plot for ' + distribution +' distribution'
                ax2.set_title(title)
                
                # Display plot    
                plt.tight_layout(pad=4)
                plt.show()
                
                cdf = cum_data
                plt.plot(cdf)
                plt.title('cumulative distribution')
                plt.show()
                return(aux_global_time)
        if ecdf:
            # USAR INVERSE

            #y_df = np.cumsum(y_df)
            for i in range(len(y)):
                cdf.append(i/len(y))
            cdf = y
            
        
    if WGNet_Input == "Trace":

    #     See all continuous distributions available in scipy.stats
    #     continuous_dist = [d for d in dir(stats) if isinstance(getattr(stats, d), stats.rv_continuous)]
    #     print(continuous_dist)

    #     Precisa encontrar o código para detalhar as distribuições


    #     Number of samples
        n = np.linspace(0,1,1000)
    #     Parameter 1
        p1 = 0
    #     Parameter 2
        p2 = 1
    #     Parameter n
    #     pn = 0

    #     Vector cdf to storage random numbers = DISTRIBUIÇÃO.rvs(n, p1, p2, pn)
        
    
        cdf = np.array(stats.norm.cdf(n,p1,p2))
    

        ax = sns.distplot(cdf, hist=False, kde_kws=dict(cumulative=True))
        ax.show()


# Lendo arquivo .pcap
os.system("sudo chmod 777 fifth.pcap")
os.system("termshark -r fifth.pcap -T fields -E separator=/t  -e ip.len > scratch/size.txt")
os.system("termshark -r fifth.pcap -T fields -E separator=/t -e frame.time_delta_displayed > scratch/time.txt")
os.system("chmod 777 scratch/size.txt")
os.system("chmod 777 scratch/time.txt")
# Abrindo gerador de carga de trabalho
wgwnet()

# Inicializando NS3
# Configuração de nós da rede
nodes = ns.network.NodeContainer()
nodes.Create(2)

# Configuração de conexão ponta a ponta
pointToPoint = ns.point_to_point.PointToPointHelper()
pointToPoint.SetDeviceAttribute("DataRate", ns.core.StringValue("5Mbps"))
pointToPoint.SetChannelAttribute("Delay", ns.core.StringValue("2000ms"))

devices = pointToPoint.Install(nodes)

stack = ns.internet.InternetStackHelper()
stack.Install(nodes)

# Definindo endereços dos nós
address = ns.internet.Ipv4AddressHelper()
address.SetBase(ns.network.Ipv4Address("10.1.1.0"),
                ns.network.Ipv4Mask("255.255.255.0"))

interfaces = address.Assign(devices)

source = ns.network.Socket.CreateSocket(
    nodes.Get(0),
    ns.core.TypeId.LookupByName("ns3::UdpSocketFactory")
)


sink = ns.network.Socket.CreateSocket(
    nodes.Get(1),
    ns.core.TypeId.LookupByName("ns3::UdpSocketFactory")
)


nPackets = 10
packetsSent = 0
def send_packet(socket, packetsSent):
    
    print("sending", ns.core.Simulator.Now())
    socket.Send(ns.network.Packet(500))
    packetsSent += 1

    if (packetsSent < nPackets):
        schedule ()

def rcv_packet(socket):
    print("received", ns.core.Simulator.Now())
port = 4477
# SINK
sink.SetRecvCallback(rcv_packet)

sink = ns.applications.PacketSinkHelper ("ns3::TcpSocketFactory", ns.network.InetSocketAddress (ns.network.Ipv4Address.GetAny (), port))
sinkApps = sink.Install (nodes.Get (1))
sinkApps.Start (ns.core.Seconds (0.0))
sinkApps.Stop (ns.core.Seconds (10.0))

sink_address = ns.network.InetSocketAddress(interfaces.GetAddress(1), port)
any_address = ns.network.InetSocketAddress(
    ns.network.Ipv4Address.GetAny(), port
)

sink.Bind(any_address)

source.Connect(sink_address)
def schedule():
    ns.core.Simulator.Schedule(


        ns.core.Seconds(aux_global_time), send_packet, source,
    )
# 
# Now, do the actual simulation.
# 
print ("Run Simulation.")
ns.core.Simulator.Stop (ns.core.Seconds (10.0))
ns.core.Simulator.Run ()
ns.core.Simulator.Destroy ()
print ("Done.")
