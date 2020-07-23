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
//

  // double size = 0;
  // int size_File = 1000;
  // double** t_Packets = create(size_File, 1);
  // double** S_Packets = create(size_File, 1);

  // double t_Pckts = 0;


// Criação das Matrizes
// double** create(int rows, int columns){
//     double** table = new double*[rows];
//     for(int i = 0; i < rows; i++) {
//         table[i] = new double[columns]; 
//         for(int j = 0; j < columns; j++){ 
//         table[i][j] = 0; 
//         }// sample set value;    
//     }
//     return table;
// }

// double** size_Packets = create(nPackets, 1);
// double** time_Packets = create(nPackets, 1);

// double size_Packets;
// double time_Packets;


int countTime = 0;
int countSize = 0;
int nPackets = 1;
bool sendSize=false;
bool sendTime=false;
double size_Packets = 0;
double time_Packets = 0;
double timeStartSimulation = 0;
double timeStopSimulation = 1000;

// Função de leitura dos dados do trace
void openTrace(int sizeFile, bool sendSize, bool sendTime, int countSize, int countTime){
  double s_Packets [sizeFile][1];
  double t_Packets [sizeFile][1];  
  // int test = 1000; 

  // if(sendSize == false && sendTime == false){
      // test = 2000;
      // Variáveis para abrir o arquivo de trace

      FILE *arqx;
      FILE *arqy;
      char Linhax[sizeFile];
      char Linhay[sizeFile];
      char *xAux;
      char *yAux;
      char *resultx;
      char *resulty;
      // Abre um arquivo TEXTO para LEITURA
      arqx = fopen("scratch/Times.txt", "rt");
      arqy = fopen("scratch/SizePackets.txt", "rt");
      if (arqx == NULL || arqy == NULL)  // Se houve erro na abertura
      {
        printf("Problemas na abertura do arquivo\n");
      }
      for(int i = 0; i<sizeFile; ++i){
          // Lê uma linha (inclusive com o '\n')
          resultx = fgets(Linhax, sizeFile, arqx);  // o 'fgets' lê até 99 caracteres ou até o '\n'
          // std::cout <<"RESULTX: " << resultx <<std::endl;
          // std::cout <<"LINHAX: " << Linhax <<std::endl;
          // std::cout <<"ARQX: " << arqx <<std::endl;
          if (resultx)  // Se foi possível ler
          xAux = Linhax;
          t_Packets[i][0] = atof(xAux);

          // Lê uma linha (inclusive com o '\n')
          resulty = fgets(Linhay, sizeFile, arqy);  // o 'fgets' lê até 99 caracteres ou até o '\n'
          if (resulty)  // Se foi possível ler
          yAux = Linhay;
          s_Packets[i][0] = atof(yAux);
          
      }
      // std::cout <<"Line: " << 0 <<std::endl;
      // std::cout <<"Size in File: " << s_Packets[0][0] <<std::endl;
      // std::cout <<"Time in File: " << t_Packets[0][0] <<std::endl;
  // }
  // if(countSize == countTime){
    if(sendSize==true){
        std::cout << " " << std::endl;
        std::cout << "Count: " << countSize <<std::endl;
        size_Packets = s_Packets[countSize][0];
        // std::cout <<"Size Count: " << countSize <<std::endl;
        // std::cout <<"Size Packet File: " << s_Packets[countSize][0] <<std::endl;
    }
      if(sendTime==true){
          time_Packets = t_Packets[countTime][0];
          // std::cout <<"Time Count: " << countTime <<std::endl;
          // std::cout <<"Time Packet File: " << t_Packets[countTime][0] <<std::endl;
      }
      if(countTime != nPackets){
          timeStopSimulation++;
      }
  // }
    
  
  // getPacket(false, false, s_Packets, t_Packets)
  //  std::cout <<"Time Packet File: " << t_Packets[1][0] <<std::endl;
  //  std::cout<< "Size Packet File: " << s_Packets[1][0] <<std::endl;
   std::cout<< " " <<std::endl;
}     

class MyApp : public Application 
{
public:

  MyApp ();
  virtual ~MyApp();

  void Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets);
  // void Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate);
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
MyApp::Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets)
// MyApp::Setup (Ptr<Socket> socket, Address address, uint32_t packetSize, uint32_t nPackets, DataRate dataRate)
{
  m_socket = socket;
  m_peer = address;
  m_packetSize = packetSize;
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


// double pSize(int sendp){
  
//  size = s_Packets[sendp][0];
// //  std::cout<< "Size: "<< s_Packets[sendp][0] <<std::endl;
// //  std::cout<< "SendP: "<< sendp <<std::endl;
//  std::cout<<" " << std::endl;
//  return size;
// }




void 
MyApp::SendPacket (void)
{
  sendSize=true;
  sendTime=false;

  openTrace(nPackets, sendSize, sendTime, countSize, countTime);
  countSize++;
  m_packetSize = size_Packets;

  // std::cout<<"sendpackt : "<< sendpckt <<std::endl;
  std::cout<<"Packet Size  : "<< m_packetSize << std::endl;
  // std::cout<<" " << std::endl;
  
  
  Ptr<Packet> packet = Create<Packet> (m_packetSize);
  m_socket->Send (packet);

  if (++m_packetsSent < m_nPackets)
    {
      ScheduleTx ();
    }
}



void 
MyApp::ScheduleTx (void)
{
  if (m_running)
    {
      
      sendTime = true;
      sendSize = false;

      openTrace(nPackets, sendSize, sendTime, countSize, countTime);
      countTime++;
      Time tNext = (Seconds (time_Packets));
      // Time tNext (Seconds (m_packetSize * 8 / static_cast<double> (m_dataRate.GetBitRate ())));
      
      std::cout<< "Time Simulation: "<< tNext <<std::endl;
      
      m_sendEvent = Simulator::Schedule (tNext, &MyApp::SendPacket, this);
      
    }
}

static void
CwndChange (uint32_t oldCwnd, uint32_t newCwnd)
{
  NS_LOG_UNCOND (Simulator::Now ().GetSeconds () << "\t" << newCwnd);
}

static void
RxDrop (Ptr<PcapFileWrapper> file, Ptr< const Packet> packet)
{
  NS_LOG_UNCOND ("RxDrop at " << Simulator::Now ().GetSeconds ());
  file->Write (Simulator::Now (), packet);

}

// void ThroughputMonitor (FlowMonitorHelper *fmhelper, Ptr<FlowMonitor> flowMon,Gnuplot2dDataset DataSet);
  int
  main (int argc, char *argv[])
  {


    CommandLine cmd;
    cmd.AddValue("nPackets", "Number of packets to echo", nPackets);
    cmd.Parse (argc, argv);

  // Função de abrir traces
  sendTime = false;
  sendSize = false;
  countSize = 0;
  countTime = 0;
  openTrace(nPackets, sendSize, sendTime, countSize, countTime);
  
  NodeContainer nodes;
  nodes.Create (2);

  PointToPointHelper pointToPoint;
  pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("5Mbps"));
  pointToPoint.SetChannelAttribute ("Delay", StringValue ("2ms"));

  NetDeviceContainer devices;
  devices = pointToPoint.Install (nodes);

 MobilityHelper mobilitywifiAll;
 mobilitywifiAll.SetPositionAllocator ("ns3::RandomRectanglePositionAllocator",
                                "X", StringValue ("ns3::UniformRandomVariable[Min=0.0|Max=10]"),
                                "Y", StringValue ("ns3::UniformRandomVariable[Min=0.0|Max=15]"));
mobilitywifiAll.SetMobilityModel ("ns3::ConstantPositionMobilityModel");

mobilitywifiAll.Install (nodes);

  Ptr<RateErrorModel> em = CreateObject<RateErrorModel> ();
  em->SetAttribute ("ErrorRate", DoubleValue (0.00001));
  devices.Get (1)->SetAttribute ("ReceiveErrorModel", PointerValue (em));

  InternetStackHelper stack;
  stack.Install (nodes);

  Ipv4AddressHelper address;
  address.SetBase ("10.1.1.0", "255.255.255.252");
  Ipv4InterfaceContainer interfaces = address.Assign (devices);

  uint16_t sinkPort = 8080;
  Address sinkAddress (InetSocketAddress (interfaces.GetAddress (1), sinkPort));
  PacketSinkHelper packetSinkHelper ("ns3::TcpSocketFactory", InetSocketAddress (Ipv4Address::GetAny (), sinkPort));
  ApplicationContainer sinkApps = packetSinkHelper.Install (nodes.Get (1));
  sinkApps.Start (Seconds (timeStartSimulation));
  sinkApps.Stop (Seconds (timeStopSimulation));

  Ptr<Socket> ns3TcpSocket = Socket::CreateSocket (nodes.Get (0), TcpSocketFactory::GetTypeId ());
  ns3TcpSocket->TraceConnectWithoutContext ("CongestionWindow", MakeCallback (&CwndChange));

  Ptr<MyApp> app = CreateObject<MyApp> ();
  
  // app->Setup (ns3TcpSocket, sinkAddress, 1040, 1000, DataRate ("1Mbps"));
  app->Setup (ns3TcpSocket, sinkAddress, size_Packets, nPackets);
  
  nodes.Get (0)->AddApplication (app);
  app->SetStartTime (Seconds (timeStartSimulation));
  app->SetStopTime (Seconds (timeStopSimulation));

  PcapHelper pcapHelper;
  Ptr<PcapFileWrapper> file = pcapHelper.CreateFile ("fifth.pcap", std::ios::out, PcapHelper::DLT_PPP);
  devices.Get (1)->TraceConnectWithoutContext ("PhyRxDrop", MakeBoundCallback (&RxDrop,file));


// //FLOW-MONITOR


// //-----------------FlowMonitor-THROUGHPUT----------------

//     std::string fileNameWithNoExtension = "FlowVSThroughput_Huenstein";
//     std::string graphicsFileName        = fileNameWithNoExtension + ".png";
//     std::string plotFileName            = fileNameWithNoExtension + ".plt";
//     std::string plotTitle               = "Flow vs Throughput";
//     std::string dataTitle               = "Throughput";

//     // Instantiate the plot and set its title.
//     Gnuplot gnuplot (graphicsFileName);
//     gnuplot.SetTitle (plotTitle);

//     // Make the graphics file, which the plot file will be when it
//     // is used with Gnuplot, be a PNG file.
//     gnuplot.SetTerminal ("png");

//     // Set the labels for each axis.
//     gnuplot.SetLegend ("Flow", "Throughput");

     
//    Gnuplot2dDataset dataset;
//    dataset.SetTitle (dataTitle);
//    dataset.SetStyle (Gnuplot2dDataset::LINES_POINTS);

//   //flowMonitor declaration
//   FlowMonitorHelper fmHelper;
//   Ptr<FlowMonitor> allMon = fmHelper.InstallAll();
//   // call the flow monitor function
//   ThroughputMonitor(&fmHelper, allMon, dataset); 



  FlowMonitorHelper flowmon;
  Ptr<FlowMonitor> monitor = flowmon.InstallAll ();

//Gerar animação
        AnimationInterface anim ("Animation.xml"); // Mandatory
        
        for (uint32_t i = 0; i < nodes.GetN(); ++i)
        {
          anim.UpdateNodeDescription (nodes.Get(i), "Node"); // Optional
          anim.UpdateNodeColor (nodes.Get(i), 255, 0, 0); // Coloração
        }

        anim.EnablePacketMetadata (true); // Optiona
        anim.EnableIpv4RouteTracking ("IPV4Route.xml", Seconds (0), Seconds (100), Seconds (0.25)); //Optional
        anim.EnableWifiMacCounters (Seconds (0), Seconds (100)); //Optional
        anim.EnableWifiPhyCounters (Seconds (0), Seconds (100)); //Optional

  
  Simulator::Stop (Seconds (100));
  Simulator::Run ();
  
//#####################Imprimir resultados da simulação
  monitor->CheckForLostPackets ();
  Ptr<Ipv4FlowClassifier> classifier = DynamicCast<Ipv4FlowClassifier> (flowmon.GetClassifier ());
  FlowMonitor::FlowStatsContainer stats = monitor->GetFlowStats ();

int u = 0;
double dur = 0;
double atraso1 = 0;
double atraso2 = 0;
double Jitter = 0;
  for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator i = stats.begin (); i != stats.end (); ++i){
      
      Ipv4FlowClassifier::FiveTuple t = classifier->FindFlow (i->first);
      dur = (i->second.timeLastRxPacket.GetSeconds()-i->second.timeFirstTxPacket.GetSeconds());
      if(dur > 0)
      {        
                    std::cout << "Flow " << i->first << " (" << t.sourceAddress << " -> " << t.destinationAddress << ")\n";
                    std::cout<<"Duration  : "<< dur <<std::endl;
                    std::cout<<"Tx Packets = " << i->second.txPackets<<std::endl;
                    std::cout<<"Rx Packets = " << i->second.rxPackets<<std::endl;
                    
                 
                    std::cout << "Perda de Pacotes: "<< i->second.txPackets - i->second.rxPackets<<std::endl;
                    
                    std::cout << "Vazão: " << i->second.rxBytes * 8.0 / (i->second.timeLastRxPacket.GetSeconds()-i->second.timeFirstTxPacket.GetSeconds())/1024 << " Kbps\n";

                    // std::cout << "Energia: "<< Energia[u][0] <<std::endl;

                    
                    std::cout << "Atraso: "<< ((i->second.timeLastRxPacket.GetSeconds()) - (i->second.timeLastTxPacket.GetSeconds())) <<std::endl;

                    atraso2 = i->second.timeLastRxPacket.GetSeconds()-i->second.timeLastTxPacket.GetSeconds();
                    atraso1 = i->second.timeFirstRxPacket.GetSeconds()-i->second.timeFirstTxPacket.GetSeconds();
                    Jitter = atraso2 - atraso1;
                    std::cout << "Jitter: "<< Jitter <<std::endl;
                    std::cout << " "<<std::endl;
                    u++;
      }
    }
//#####################Imprimir resultados da simulação
 
  // //Gnuplot ...continued
  // gnuplot.AddDataset (dataset);
  // // Open the plot file.
  // std::ofstream plotFile (plotFileName.c_str());
  // // Write the plot file.
  // gnuplot.GenerateOutput (plotFile);
  // // Close the plot file.
  // plotFile.close ();


  
  Simulator::Destroy ();
  return 0;
}

  // void ThroughputMonitor (FlowMonitorHelper *fmhelper, Ptr<FlowMonitor> flowMon,Gnuplot2dDataset DataSet)
  //   {
  //         double localThrou=0;
  //     std::map<FlowId, FlowMonitor::FlowStats> flowStats = flowMon->GetFlowStats();
  //     Ptr<Ipv4FlowClassifier> classing = DynamicCast<Ipv4FlowClassifier> (fmhelper->GetClassifier());
  //     for (std::map<FlowId, FlowMonitor::FlowStats>::const_iterator stats = flowStats.begin (); stats != flowStats.end (); ++stats)
  //     {
  //                       if(stats->first == 1){//IFFFFFFFFFFFFFFFFFFFFFFF
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
  //   }//IFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF  
  // }
  //       Simulator::Schedule(Seconds(1),&ThroughputMonitor, fmhelper, flowMon,DataSet);
  //    //if(flowToXml)
  //       {
  //   flowMon->SerializeToXmlFile ("FlowMonitor.xml", true, true);
  //       }

  //   }

  
