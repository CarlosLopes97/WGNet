import ns.applications
import ns.core
import ns.internet
import ns.network
import ns.point_to_point

nodes = ns.network.NodeContainer()
nodes.Create(2)

pointToPoint = ns.point_to_point.PointToPointHelper()
pointToPoint.SetDeviceAttribute("DataRate", ns.core.StringValue("5Mbps"))
pointToPoint.SetChannelAttribute("Delay", ns.core.StringValue("2000ms"))

devices = pointToPoint.Install(nodes)

stack = ns.internet.InternetStackHelper()
stack.Install(nodes)

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


def send_packet(socket):
    print("sending", ns.core.Simulator.Now())
    socket.Send(ns.network.Packet(5))


def rcv_packet(socket):
    print("received", ns.core.Simulator.Now())


sink.SetRecvCallback(rcv_packet)


sink_address = ns.network.InetSocketAddress(interfaces.GetAddress(1), 4477)
any_address = ns.network.InetSocketAddress(
    ns.network.Ipv4Address.GetAny(), 4477
)

sink.Bind(any_address)
source.Connect(sink_address)

ns.core.Simulator.Schedule(
    ns.core.Seconds(0.0), send_packet, source,
)

ns.core.Simulator.Run()
ns.core.Simulator.Destroy()