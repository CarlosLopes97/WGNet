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
#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/netanim-module.h"
#include "ns3/mobility-module.h"
#include "ns3/gnuplot.h"
#include <iostream>
#include <sstream>
#include <fstream>

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

  // Variáveis auxiliares para leitura do arquivo .txt 
  int countTime = 0;
  int countSize = 0;
  int nPackets = 0;
  bool sendSize=false;
  bool sendTime=false;
  double size_Packets = 0;
  double time_Packets = 0;

  // Função void para leitura dos dados do trace
  void openTrace(int sizeFile, bool sendSize, bool sendTime, int countSize, int countTime){
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
    arqx = fopen("../../../workload/WGNet/Parameters/Times.txt", "rt");
    arqy = fopen("../../../workload/WGNet/Parameters/SizePackets.txt", "rt");
    
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

        // Lê uma linha (inclusive com o '\n')
        resulty = fgets(Linhay, sizeFile, arqy);  // o 'fgets' lê até 99 caracteres ou até o '\n'
        if (resulty)  // Se foi possível ler
        yAux = Linhay;
        s_Packets[i][0] = atof(yAux);
        
    }
    // Condição para acessar o tamanho do pacote de nº countSize 
    if(sendSize==true){
        size_Packets = s_Packets[countSize][0];
        NS_LOG_UNCOND ("Packets Size: " << size_Packets);
        std::cout << "Size Count: " << countSize <<std::endl;
        // std::cout <<"Size Packet File: " << s_Packets[countSize][0] <<std::endl;
    }
    // Condição para acessar o tempo do pacote de nº countTime 
      if(sendTime==true){
          time_Packets = t_Packets[countTime][0];
          NS_LOG_UNCOND ("Packet Time: " << time_Packets);
          std::cout <<"Time Count: " << countTime <<std::endl;
          // std::cout <<"Time Packet File: " << t_Packets[countTime][0] <<std::endl;
      }
  }     
  // Criando Class MyApp
  class MyApp : public Application 
  {
  public:
    MyApp ();
    virtual ~MyApp();
    // Criando Steup da aplicação
    void Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets);
    // void Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate); // Código original
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
  // Instanciando Setup
  void
  MyApp::Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets){
  // MyApp::Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate) // Código original{
    m_socket = socket;
    m_peer = address;
    m_packetSize = packetSize;
    m_nPackets = nPackets;
    // m_dataRate = dataRate;
  }

  // Criando função StartApplication
  void
  MyApp::StartApplication (void){
    m_running = true;
    m_packetsSent = 0;
    m_socket->Bind ();
    m_socket->Connect (m_peer);
    SendPacket ();
  }

// Criando função StopApplication
  void 
  MyApp::StopApplication (void){
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

// Criando função SendPacket onde se define o tamanho dos pacotes
  void 
  MyApp::SendPacket (void){
    // Variáveis auxiliares para possibilitar o acesso do tamanho do pacote no arquivo .txt
    sendSize=true;
    sendTime=false;
    
    // chamada da função que lê os arquivos .txt
    openTrace(nPackets, sendSize, sendTime, countSize, countTime);
    
    // contador para controle do ID dos pacotes
    countSize++;
    
    // Tamanho do pacote obtido do .txt
    m_packetSize = size_Packets;
    // std::cout<<"Packet Size  : "<< m_packetSize << std::endl;
    
    // Criando o ponteiro Packet com o tamanho m_packetSize
    Ptr<Packet> packet = Create<Packet> (m_packetSize);
    m_socket->Send (packet);

    // Método para execução da chamada do ScheduleTx
    if (++m_packetsSent < m_nPackets)
      {
        ScheduleTx ();
      }
  }

  // Criando função ScheduleTx
  void 
  MyApp::ScheduleTx (void){
    // Condição que acessível enquanto o simulador está executando
    if (m_running){
        // Variáveis auxiliares para possibilitar o acesso ao tempo de cada pacote no arquivo .txt
        sendTime = true;
        sendSize = false;
        
        // chamada da função que lê os arquivos .txt
        openTrace(nPackets, sendSize, sendTime, countSize, countTime);
        
        // contador para controle do ID dos pacotes
        countTime++;
        // Criando variável tNext que obtem o tempo dos arquivos .txt em Millisegundos
        Time tNext = (MilliSeconds (time_Packets));

        // Time tNext (Seconds (m_packetSize * 8 / static_cast<double> (m_dataRate.GetBitRate ()))); // Código Original
        
        // "Schedulando" o tempo de envio do pacote e a função SendPacket (que contém o tamanho do pacote)
        // para criar um evento m_sendEvent
        m_sendEvent = Simulator::Schedule (tNext, &MyApp::SendPacket, this);
        
    }
  }
  // Criando a função void que obtem o tamanho da janela de congestionamento do TCP
  static void
  CwndChange (uint32_t oldCwnd, uint32_t newCwnd)
  {
    // Imprimindo a cada segundo o valor da nova janela
    NS_LOG_UNCOND (Simulator::Now ().GetSeconds () << "\t" << newCwnd);
  }
  
  // Criando a função void RxDrop que obtem os dados recebidos do pacote
  static void
  RxDrop (Ptr<PcapFileWrapper> file, Ptr< const Packet> packet)
  {
  // imprimindo valores obtidos a cada segundo
  NS_LOG_UNCOND ("RxDrop at " << Simulator::Now ().GetSeconds ());
  // Escrevendo informações do pacote em um arquivo .pcap
  file->Write (Simulator::Now (), packet);
  }

  // void ThroughputMonitor (FlowMonitorHelper *fmhelper, Ptr<FlowMonitor> flowMon,Gnuplot2dDataset DataSet); // Código para obter flowmonitor por função void
  // Inicio da função main
  int
  main (int argc, char *argv[])
  {
  // Criando variáveis de tempo de inicio e fim de simulação
  double timeStartSimulation = 0;
  double timeStopSimulation = 10;
  
  // Definindo o comando por linha de código
  CommandLine cmd;
  // chamada das variáveis que recebem dados do run.sh
  cmd.AddValue("nPackets", "Numero de Pacotes: ", nPackets); // Recebe o número de Pacotes por meio da quantidade de linhas do .txt
  cmd.AddValue("timeStopSimulation", "Tempo final da simulação: ", timeStopSimulation); // recebe o tempo de parada da simulação por meio da ultima linha do Time.txt
  cmd.Parse (argc, argv);

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
  app->Setup (ns3TcpSocket, sinkAddress, size_Packets, nPackets);
  // app->Setup (ns3TcpSocket, sinkAddress, 1040, 1000, DataRate ("1Mbps")); // Código Original
  // Adicionando Aplicação em app ponteiro 
  nodes.Get (0)->AddApplication (app);
  // Iniciando aplicação
  app->SetStartTime (Seconds (timeStartSimulation));
  //  Parando Aplicação
  app->SetStopTime (Seconds (timeStopSimulation));
  
  // Setando pcapHelper
  PcapHelper pcapHelper;
  // Criando arquivo pcap
  Ptr<PcapFileWrapper> file = pcapHelper.CreateFile ("../../../workload/WGNet/fifth files/fifth_Trace.pcap", std::ios::out, PcapHelper::DLT_PPP);
  // Obtendo dados do Trace de PhyRxDrop dos Devices 
  devices.Get (1)->TraceConnectWithoutContext ("PhyRxDrop", MakeBoundCallback (&RxDrop,file));

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
  AnimationInterface anim ("../../../workload/WGNet/fifth files/fifth_Animation.xml"); // Mandatory
  // Adicionando configurações em todos os nós
  for (uint32_t i = 0; i < nodes.GetN(); ++i){
    anim.UpdateNodeDescription (nodes.Get(i), "Node"); // Optional
    anim.UpdateNodeColor (nodes.Get(i), 255, 0, 0); // Coloração
  }
  anim.EnablePacketMetadata (true); // Optiona
  anim.EnableIpv4RouteTracking ("../../../workload/WGNet/fifth files/fifth_IPV4Route.xml", Seconds (timeStartSimulation), Seconds (timeStopSimulation), Seconds (5)); //Optional
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
  // Função de execuçao do Flowmonitor
  // void ThroughputMonitor (FlowMonitorHelper *fmhelper, Ptr<FlowMonitor> flowMon,Gnuplot2dDataset DataSet){
      // double localThrou=0;
      // std::map<FlowId, FlowMonitor::FlowStats> flowStats = flowMon->GetFlowStats();
      // Ptr<Ipv4FlowClassifier> classing = DynamicCast<Ipv4FlowClassifier> (fmhelper->GetClassifier());
      // for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator stats = flowStats.begin (); stats != flowStats.end (); ++stats){
      //     if(stats->first == 1){
      //       Ipv4FlowClassifier::FiveTuple fiveTuple = classing->FindFlow (stats->first);
      //       std::cout<<"Flow ID     : " << stats->first <<" ; "<< fiveTuple.sourceAddress <<" -----> "<<fiveTuple.destinationAddress<<std::endl;
      //       std::cout<<"Tx Packets = " << stats->second.txPackets<<std::endl;
      //       std::cout<<"Rx Packets = " << stats->second.rxPackets<<std::endl;
      //             std::cout<<"Duration    : "<<(stats->second.timeLastRxPacket.GetSeconds()-stats->second.timeFirstTxPacket.GetSeconds())<<std::endl;
      //       std::cout<<"Last Received Packet  : "<< stats->second.timeLastRxPacket.GetSeconds()<<" Seconds"<<std::endl;
      //       std::cout<<"Throughput: " << stats->second.rxBytes * 8.0 / (stats->second.timeLastRxPacket.GetSeconds()-stats->second.timeFirstTxPacket.GetSeconds())/1024/1024  << " Mbps"<<std::endl;
      //             localThrou=(stats->second.rxBytes * 8.0 / (stats->second.timeLastRxPacket.GetSeconds()-stats->second.timeFirstTxPacket.GetSeconds())/1024/1024);
      //       // updata gnuplot data
      //             DataSet.Add((double)Simulator::Now().GetSeconds(),(double) localThrou);
      //       std::cout<<"---------------------------------------------------------------------------"<<std::endl;
      //     }
      // }
      // Simulator::Schedule(Seconds(1),&ThroughputMonitor, fmhelper, flowMon,DataSet);
      // // Serializar informações do flowmonitor em um arquivo .xml
      // flowMon->SerializeToXmlFile ("Net_FlowMonitor.xml", true, true);
  // }