/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/*
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation;
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */






#include <fstream>
#include "ns3/flow-monitor-module.h"
#include "ns3/netanim-module.h"
#include "ns3/mobility-module.h"
#include <sstream>
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/random-variable-stream.h"
#include "ns3/ptr.h"
#include "ns3/double.h"
#include "ns3/integer.h"
#include "ns3/gnuplot.h"
#include <map>
#include <cmath>

// Wireshark Open
#include <string>
#include <iostream>
// #include </usr/include/pcap/pcap.h>
#include <string>

// Inverse
#include <stdio.h>     /* prinft, fprintf */
#include <math.h>      /* log */
#include <stdlib.h>    /* rand */


using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("FifthScriptExample");

// ===========================================================================
//
//         node 0                 node 1
//   +----------------+    +----------------+
//   |    ns-3 TCP    |    |    ns-3 TCP    |
//   +----------------+    +----------------+
//   |    10.1.1.1    |    |    10.1.1.2    |
//   +----------------+    +----------------+
//   | point-to-point |    | point-to-point |
//   +----------------+    +----------------+
//           |                     |
//           +---------------------+
//                5 Mbps, 2 ms
//
//
// We want to look at changes in the ns-3 TCP congestion window.  We need
// to crank up a flow and hook the CongestionWindow attribute on the socket
// of the sender.  Normally one would use an on-off application to generate a
// flow, but this has a couple of problems.  First, the socket of the on-off 
// application is not created until Application Start time, so we wouldn't be 
// able to hook the socket (now) at configuration time.  Second, even if we 
// could arrange a call after start time, the socket is not public so we 
// couldn't get at it.
//
// So, we can cook up a simple version of the on-off application that does what
// we want.  On the plus side we don't need all of the complexity of the on-off
// application.  On the minus side, we don't have a helper, so we have to get
// a little more involved in the details, but this is trivial.
//
// So first, we create a socket and do the trace connect on it; then we pass 
// this socket into the constructor of our simple application which we then 
// install in the source node.
// ===========================================================================
//


// void Inverse(int N){


// //#define N         1000000		 // number of simulations
// #define lambda    2.0		    // lambda - Exponential distribution parameter
// #define OUTFILE	  "scratch/time.txt"	// output file

  
//   FILE *out = fopen(OUTFILE,"w");
   
//   // int N = 100000;

//   double u[N];    // uniformly[0,1] distributed random number
//   double e[N];    // exponentially distributed random number
  
//   for (int i=0; i<N; i++){
//     u[i] = ((double)rand()/(double)RAND_MAX);
//     e[i] = - log(u[i])/lambda;


//     expon_inv(u);
//     burr_inv(u);
//     laplace_inv;
//     logistic_inv;
//     pareto_inv;
//    //e[i] = - log(u[i]);
//     printf("u[%i]=%f, e[%i]=%f\n", i ,u[i], i, e[i]);
//     //fprintf(out, "u[%i]=%f, e[%i]=%f\n", i ,u[i], i, e[i]);
//     fprintf(out, "%f\t%f\n", u[i], e[i]);
//   }
// fclose(out);

// hist(X, freq=F, xlab='X', main='Generating Exponential R.V.');
// curve(dexp(x, rate=2) , 0, 3, lwd=2, xlab = "", ylab = "", add = T);
// }

// double expon_inv(double u){
//     int a = 1;
//     return -a*log(1-u);
// }

// double burr_inv(double u){
//     int k = 1;
//     int c = 2;
//     return power(((power(1-u,-1/k))-1),1/c);
// }
// double laplace_inv(double u){

//     if (u.all() <= 0.5){
//         return log(2*u);

//     }else{
//         return -1*(log(2*(1-u)));
//     }
// }
// double logistic_inv(double u){
//     return log((1-u))/u;
// }

// double pareto_inv(double u){
//     int c = 1;
//     return power((1-u),-1/c);
//     }

// Variáveis auxiliares para leitura do arquivo .txt 
  // int countTime = 0;
  // int countSize = 0;
  int nPackets = 0;
  // bool sendSize=false;
  // bool sendTime=false;
  // double size_Packets = 0;
  // double time_Packets = 0;

  // Função void para leitura dos dados do trace
  void openTrace(int sizeFile){
    // Arrays que armazenam dados de tempo e tamanho dos pacotes
    double s_Packets [sizeFile][1];
    double t_Packets [sizeFile][1];  
    // Inicio do código de leitura
    FILE *arqx;
    FILE *arqy;
    char Linhax[sizeFile];
    char Linhay[sizeFile];
    char *xAux;
    char *yAux;
    char *resultx;
    char *resulty;
    // Abre um arquivo TEXTO para LEITURA
    arqx = fopen("scratch/time.txt", "rt");
    arqy = fopen("scratch/size.txt", "rt");
    
    if (arqx == NULL || arqy == NULL)  // Se houve erro na abertura
    {
      printf("Problemas na abertura do arquivo\n");
    }
    // Loop que lê todas as linhas do arquivo .txt
    for(int i = 0; i<sizeFile; ++i){
        // Lê uma linha (inclusive com o '\n')
        resultx = fgets(Linhax, sizeFile, arqx);  // o 'fgets' lê até 99 caracteres ou até o '\n'
        if (resultx)  // Se foi possível ler
        xAux = Linhax;
        t_Packets[i][0] = atof(xAux);
        std::cout<< t_Packets[i][0] <<std::endl;
        // Lê uma linha (inclusive com o '\n')
        resulty = fgets(Linhay, sizeFile, arqy);  // o 'fgets' lê até 99 caracteres ou até o '\n'
        if (resulty)  // Se foi possível ler
        yAux = Linhay;
        s_Packets[i][0] = atof(yAux);
        std::cout<< s_Packets[i][0] <<std::endl;
        
    }
  }     



class MyApp : public Application 
{
public:

  MyApp ();
  virtual ~MyApp();

  void Setup (Ptr<Socket> socket, Address address, uint32_t nPackets);

private:
  virtual void StartApplication (void);
  virtual void StopApplication (void);

  void ScheduleTx (void);
  void SendPacket (void);

  Ptr<Socket>     m_socket;
  Address         m_peer;
  uint32_t        m_packetSize;
  uint32_t        m_nPackets;
  DataRate        m_dataRate;
  EventId         m_sendEvent;
  bool            m_running;
  uint32_t        m_packetsSent;
};

MyApp::MyApp ()
  : m_socket (0), 
    m_peer (), 
    m_packetSize (0), 
    m_nPackets (0), 
    m_dataRate (0), 
    m_sendEvent (), 
    m_running (false), 
    m_packetsSent (0)
{
}

MyApp::~MyApp()
{
  m_socket = 0;
}

void
MyApp::Setup (Ptr<Socket> socket, Address address, uint32_t nPackets)
{
  m_socket = socket;
  m_peer = address;
  // m_packetSize = packetSize;
  m_nPackets = nPackets;
  // m_dataRate = dataRate;
}

void
MyApp::StartApplication (void)
{
  m_running = true;
  m_packetsSent = 0;
  m_socket->Bind ();
  m_socket->Connect (m_peer);
  SendPacket ();
}

void 
MyApp::StopApplication (void)
{
  m_running = false;

  if (m_sendEvent.IsRunning ())
    {
      Simulator::Cancel (m_sendEvent);
    }

  if (m_socket)
    {
      m_socket->Close ();
    }
}
Ptr<UniformRandomVariable> sz = CreateObject<UniformRandomVariable> ();

void 
MyApp::SendPacket (void)
{
  

  sz->SetAttribute("Min", DoubleValue (500));
  sz->SetAttribute("Max", DoubleValue(1024));
  Ptr<Packet> packet = Create<Packet> (sz->GetValue ());

  m_socket->Send (packet);
  // std::cout << "Size: " <<  sz->GetValue () << std::endl;

  if (++m_packetsSent < m_nPackets)
    {
      ScheduleTx ();
    }
}
void selectionSort(double times[], int n) {
   int i, j, min, temp;
   for (i = 0; i < n - 1; i++) {
      min = i;
      for (j = i + 1; j < n; j++)
      if (times[j] < times[min])
      min = j;
      temp = times[i];
      times[i] = times[min];
      times[min] = temp;
   }
}
  Ptr<UniformRandomVariable> tm = CreateObject<UniformRandomVariable> ();
double Times (){
  tm->SetAttribute("Min", DoubleValue (0));
  tm->SetAttribute("Max", DoubleValue(1));
  return (tm->GetValue ());
  
  }


double global_time = 0;
double aux_global_time = 0;

void 
MyApp::ScheduleTx (void)
{
  if (m_running)
    {
     
      aux_global_time = Times(); 

      global_time = global_time + aux_global_time;

      Time tNext (Seconds(global_time));
      std::cout << "Time: " << global_time << std::endl;
      // Time tNext (Seconds (m_packetSize * 8 / static_cast<double> (m_dataRate.GetBitRate ())));
      m_sendEvent = Simulator::Schedule (tNext, &MyApp::SendPacket, this);
    }
}

static void
CwndChange (uint32_t oldCwnd, uint32_t newCwnd)
{
  NS_LOG_UNCOND (Simulator::Now ().GetSeconds () << "\t" << newCwnd);
}

// static void
// RxDrop (Ptr<const Packet> p)
// {
//   NS_LOG_UNCOND ("RxDrop at " << Simulator::Now ().GetSeconds ());
// }

int main (int argc, char *argv[])
  {
  // system("tshark -r fifth_Trace.pcap -T pdml > fifth_Trace.pdml");
  // system("termshark -r fifth_Trace.pcap -T fields -E separator=/t  -e ip.len > scratch/size.txt");
  // system("termshark -r fifth_Trace.pcap -T fields -E separator=/t -e frame.time_delta_displayed > scratch/time.txt");

  // // Criando variáveis de tempo de inicio e fim de simulação
  double timeStartSimulation = 0;
  double timeStopSimulation = 10;
  
  // Definindo o comando por linha de código
  CommandLine cmd;
  // chamada das variáveis que recebem dados do run.sh
  cmd.AddValue("nPackets", "Numero de Pacotes: ", nPackets); // Recebe o número de Pacotes por meio da quantidade de linhas do .txt
  cmd.AddValue("timeStopSimulation", "Tempo final da simulação: ", timeStopSimulation); // recebe o tempo de parada da simulação por meio da ultima linha do Time.txt
  cmd.Parse (argc, argv);

  openTrace(nPackets);

  // Inverse(nPackets);


  // std::cout<< "N Packets: "<< nPackets <<std::endl;
  // std::cout<< "Time Simulation: "<< timeStopSimulation <<std::endl;
  
  // Criando Nodecontainers
  NodeContainer nodes;

  // Setando a quantidade de nós da simulação
  nodes.Create (2);

  // Configurando a configuração P2P
  PointToPointHelper pointToPoint;
  pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("5Mbps"));
  pointToPoint.SetChannelAttribute ("Delay", StringValue ("2ms"));

  // Criando NetDeviceContainer entre os nós
  NetDeviceContainer devices;
  devices = pointToPoint.Install (nodes);

  // Criando mobilidade dos nós
  MobilityHelper mobility;
  // Setando configurações de mobilidade
  mobility.SetPositionAllocator ("ns3::RandomRectanglePositionAllocator",
                                  "X", StringValue ("ns3::UniformRandomVariable[Min=0.0|Max=10]"),
                                  "Y", StringValue ("ns3::UniformRandomVariable[Min=0.0|Max=15]"));
  // Set Constant position dos nos
  mobility.SetMobilityModel ("ns3::ConstantPositionMobilityModel");
  mobility.Install (nodes);
  
  // Configurando RateErrorModel 
  Ptr<RateErrorModel> em = CreateObject<RateErrorModel> ();
  em->SetAttribute ("ErrorRate", DoubleValue (0.00001));
  devices.Get (1)->SetAttribute ("ReceiveErrorModel", PointerValue (em));
  
  // Criando InternetStackHelper
  InternetStackHelper stack;
  stack.Install (nodes);

  // Configurando Ipv4 dos nos
  Ipv4AddressHelper address;
  address.SetBase ("10.1.1.0", "255.255.255.252");
  Ipv4InterfaceContainer interfaces = address.Assign (devices);

  // Configuração da aplicação sink TCP
  uint16_t sinkPort = 8080;
  // Obtendo interfaces de endereço IPV4
  Address sinkAddress (InetSocketAddress (interfaces.GetAddress (1), sinkPort));
  // Configurando packetSinkHelper
  PacketSinkHelper packetSinkHelper ("ns3::TcpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), sinkPort));
  // Instalando application Container nos nós
  ApplicationContainer sinkApps = packetSinkHelper.Install (nodes.Get (1));
  // Iniciando Aplicação
  sinkApps.Start (Seconds (timeStartSimulation));
  // Parando Aplicação
  sinkApps.Stop (Seconds(timeStopSimulation));
  
  // Configurando Socket
  Ptr<Socket> ns3TcpSocket = Socket::CreateSocket (nodes.Get (0), TcpSocketFactory::GetTypeId ());
  // Obtendo Janela de Congestionamento
  ns3TcpSocket->TraceConnectWithoutContext ("CongestionWindow", MakeCallback (&CwndChange));
  
  // Criando ponteiro de MyApp chamado app
  Ptr<MyApp> app = CreateObject<MyApp> ();
  // Configurando Setup da aplicação
  app->Setup (ns3TcpSocket, sinkAddress, nPackets);
  // app->Setup (ns3TcpSocket, sinkAddress, 1040, 1000, DataRate ("1Mbps")); // Código Original
  // Adicionando Aplicação em app ponteiro 
  nodes.Get (0)->AddApplication (app);
  // Iniciando aplicação
  app->SetStartTime (Seconds (timeStartSimulation));
  //  Parando Aplicação
  app->SetStopTime (Seconds (timeStopSimulation));
  
  // Setando pcapHelper
  // PcapHelper pcapHelper;
  // // Criando arquivo pcap
  // Ptr<PcapFileWrapper> file = pcapHelper.CreateFile ("fifth_Trace_ns3.pcap", std::ios::out, PcapHelper::DLT_RAW);

  // // Obtendo dados do Trace de PhyRxDrop dos Devices 
  // devices.Get (1)->TraceConnectWithoutContext ("PhyRxDrop", MakeBoundCallback (&RxDrop,file));

// Configuração de flowmonitor por função (Etapa Gnuplot)
// -------------------------FlowMonitor-------------------------

  // std::string fileNameWithNoExtension = "FlowVSThroughput_Huenstein";
  // std::string graphicsFileName        = fileNameWithNoExtension + ".png";
  // std::string plotFileName            = fileNameWithNoExtension + ".plt";
  // std::string plotTitle               = "Flow vs Throughput";
  // std::string dataTitle               = "Throughput";

  // // Instantiate the plot and set its title.
  // Gnuplot gnuplot (graphicsFileName);
  // gnuplot.SetTitle (plotTitle);

  // // Make the graphics file, which the plot file will be when it
  // // is used with Gnuplot, be a PNG file.
  // gnuplot.SetTerminal ("png");

  // // Set the labels for each axis.
  // gnuplot.SetLegend ("Flow", "Throughput");


  // Gnuplot2dDataset dataset;
  // dataset.SetTitle (dataTitle);
  // dataset.SetStyle (Gnuplot2dDataset::LINES_POINTS);

  // //flowMonitor declaration
  // FlowMonitorHelper fmHelper;
  // Ptr<FlowMonitor> allMon = fmHelper.InstallAll();
  // // call the flow monitor function
  // ThroughputMonitor(&fmHelper, allMon, dataset); 


  // Declarando Flowmonitor
  FlowMonitorHelper flowmon;
  // Instalando flowmonitor em todos os fluxos
  Ptr<FlowMonitor> monitor = flowmon.InstallAll ();

  //Gerar animação
  AnimationInterface anim ("../../../Documentos/Backup/workload/WGNet/fifth-random files/fifth_Animation.xml"); // Mandatory
  // Adicionando configurações em todos os nós
  for (uint32_t i = 0; i < nodes.GetN(); ++i){
    anim.UpdateNodeDescription (nodes.Get(i), "Node"); // Optional
    anim.UpdateNodeColor (nodes.Get(i), 255, 0, 0); // Coloração
  }
  anim.EnablePacketMetadata (true); // Optiona
  anim.EnableIpv4RouteTracking ("../../../Documentos/Backup/workload/WGNet/fifth-random files/fifth_IPV4Route.xml", Seconds (timeStartSimulation), Seconds (timeStopSimulation), Seconds (5)); //Optional
  anim.EnableWifiMacCounters (Seconds (timeStartSimulation), Seconds (timeStopSimulation)); //Optional
  anim.EnableWifiPhyCounters (Seconds (timeStartSimulation), Seconds (timeStopSimulation)); //Optional

  // Parando Simulação
  Simulator::Stop (Seconds(timeStopSimulation));
  // Executar Simulação
  Simulator::Run ();
  
  // Configurar FlowMonitor apenas para imprimir resultados
  monitor->CheckForLostPackets ();
  Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier> (flowmon.GetClassifier ());
  FlowMonitor::FlowStatsContainer stats = monitor->GetFlowStats ();
  
  // Criando variáveis auxiliares para obter resultados do FlowMonitor
  double dur = 0;
  double atraso1 = 0;
  double atraso2 = 0;

  // Estrutura para percorrer os fluxos varias vezes durante a simulação
  for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator i = stats.begin (); i != stats.end (); ++i){
      // Classificando fluxos pelo IPV4
      Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow (i->first);
      // 
      dur = (i->second.timeLastRxPacket.GetSeconds()-i->second.timeFirstTxPacket.GetSeconds());       
      std::cout << "Flow " << i->first << " (" << t.sourceAddress << " -> " << t.destinationAddress << ")\n";
      std::cout << "Duration  : "<< dur <<std::endl;
      std::cout << "Tx Packets = " << i->second.txPackets<<std::endl;
      std::cout << "Rx Packets = " << i->second.rxPackets<<std::endl;
      std::cout << "Perda de Pacotes: "<< i->second.txPackets - i->second.rxPackets<<std::endl;
      std::cout << "Vazão: " << i->second.rxBytes * 8.0 / (i->second.timeLastRxPacket.GetSeconds()-i->second.timeFirstTxPacket.GetSeconds())/1024 << " Kbps\n";
      std::cout << "Atraso: "<< ((i->second.timeLastRxPacket.GetSeconds()) - (i->second.timeLastTxPacket.GetSeconds())) <<std::endl;
      // Obtendo valores para o Jitter
      atraso2 = i->second.timeLastRxPacket.GetSeconds()-i->second.timeLastTxPacket.GetSeconds();
      atraso1 = i->second.timeFirstRxPacket.GetSeconds()-i->second.timeFirstTxPacket.GetSeconds();
      std::cout << "Jitter: "<< atraso2 - atraso1 <<std::endl;
      std::cout << " "<<std::endl;
  }
  // Configurando Flowmonitor por função (Gnuplot)  
  // //Gnuplot ...continued
  // gnuplot.AddDataset (dataset);
  // // Open the plot file.
  // std::ofstream plotFile (plotFileName.c_str());
  // // Write the plot file.
  // gnuplot.GenerateOutput (plotFile);
  // // Close the plot file.
  // plotFile.close ();


  // Destruindo Simulação
  Simulator::Destroy ();
  return 0;
}

