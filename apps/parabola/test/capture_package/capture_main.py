from scapy.all import *

pkts = sniff(iface="enp0s25", count=100)


print pkts