To enable port 80 forwarding at OpenWRT: OpenWrt@root:~/scripts$iptables 
-t nat -A prerouting_wan -p tcp --dport 80 -j DNAT --to 10.0.3.100:80 OpenWrt@root:~/scripts$iptables -A forwarding_wan -p tcp --dport 80 -d 10.0.3.100 -j ACCEPT

History
v2.0a
  - webserver.py send SIGUSR to reload database
  - StartRec.sh OK: ./StartRec.sh 1 "CT 1" 60 dvb.ct1.avi
  - time to string conversion fixed
