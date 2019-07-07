import os
import sys
import dpkt
import json
import pcap
import socket
from collections import OrderedDict
from tcp_analyser import Tcp_analyser


class Flow_Analyser:

    def __init__(self, session=False, output=None, map=False):
        self.active_flow_list ={}
        self.tcp_analyser= Tcp_analyser(session)
        self.map = map
        self.session = session
        if output == None:
            self.out_file_pointer = None
        elif output == sys.stdout:
            self.out_file_pointer = sys.stdout
        else:
            self.out_file_pointer = open(output, 'w')


    def extract_flow_record(self, input_files, detailed=False):
        for input_file in input_files:
            if os.path.isfile(input_file):
                f = open(input_file, 'rb')
                if input_file.endswith('.pcap'):
                    packets = dpkt.pcap.Reader(f)
                elif input_file.endswith('.pcapng'):
                    packets = dpkt.pcapng.Reader(f)
                capture_type = 'offline'
            else:
                packets = pcap.pcap(input_file, timeout_ms=1000)
                capture_type = 'online'

            data_list = OrderedDict({})
            while True:
                if capture_type == 'offline':
                    pkts = []
                    if type(packets) == dpkt.pcap.Reader:
                        while True:
                            try:
                                pkts.append(packets.__next__())
                            except Exception as e:
                                break
                    elif type(packets) == dpkt.pcapng.Reader:
                        while True:
                            try:
                                pkts.append(packets.next())
                            except Exception as e:
                                break     
                    f.close()

                else:
                    pkts = packets.readpkts()
                for ts, buf in pkts:
                    try:
                        eth = dpkt.ethernet.Ethernet(buf)
                    except:
                        break # no data error?
                    ip = eth.data
                    # tcp flow
                    if (type(ip) != dpkt.ip.IP and type(ip) != dpkt.ip6.IP6) or type(ip.data) != dpkt.tcp.TCP:
                        continue
                    tcp = ip.data
                    data = tcp.data

                    if type(ip) == dpkt.ip.IP:
                        add_fam = socket.AF_INET
                    else:
                        add_fam = socket.AF_INET6
                    flow_key = (socket.inet_ntop(add_fam,ip.src), tcp.sport, socket.inet_ntop(add_fam,ip.dst), tcp.dport)
                    twin_flow_key = (socket.inet_ntop(add_fam,ip.dst), tcp.dport, socket.inet_ntop(add_fam,ip.src), tcp.sport)
                    seq_num = tcp.seq
                    data_len = len(data)
                    try:
                        record = data_list[flow_key]
                        if self.session == True:
                            record['current_pkt_direction'] = '>'
                    except:
                        try:
                            if self.session == True:
                                record = data_list[twin_flow_key]
                                record['current_pkt_direction'] = '<'
                                if record['init_seq_backward'] == 0:
                                    record['init_seq_backward'] = tcp.seq
                            else:
                                raise Exception
                        except:
                            flow_key_ = OrderedDict({})
                            flow_key_['source_addr'] = socket.inet_ntop(add_fam, ip.src)
                            flow_key_['dest_addr'] = socket.inet_ntop(add_fam, ip.dst)
                            flow_key_['source_port'] = tcp.sport
                            flow_key_['dest_port'] = tcp.dport
                            flow_key_['protocol'] = 'TCP'
                            #create a new flow record and init it
                            flow = OrderedDict({})
                            flow['flow_key'] = flow_key_
                            flow['tcp_retrans'] = []
                            flow['pkt_num'] = 0
                            flow['pkt_info'] = []
                            flow['start_time_stamp'] = ts
                            flow['init_seq'] = tcp.seq
                            flow['init_seq_backward'] = 0
                            #add the new record into data_
                            data_list[flow_key] = flow
                            record = data_list[flow_key]
                            if self.session == True:
                                flow['twin_tcp_retrans'] = []
                                record['current_pkt_direction'] = '>'

                    rc = self.tcp_analyser.retrans_detected(record, seq_num, data_len)
                    if rc != 0:
                        continue
                    if data_len > 0:
                        self.tcp_analyser.flow_record_process(record, ts, ip)

                if len(data_list) and self.out_file_pointer != None:
                    self.write_record(data_list)
                if capture_type == 'offline':
                    break

        if self.out_file_pointer != None and self.out_file_pointer != sys.stdout:
            self.out_file_pointer.close()

        return data_list

    def write_record(self, record_data):

        if self.map == True:
            for rec_value in record_data.values():
                pkts_map = self.tcp_analyser.ip_tcp_map(rec_value)
                if len(pkts_map) == 0:
                    continue
                self.out_file_pointer.write('%s\n' % json.dumps(pkts_map))
                self.out_file_pointer.flush() 
            return

        for rec_value in record_data.values():
            try:
                del rec_value['tcp_retrans']
                if self.session == True:
                    del rec_value['twin_tcp_retrans']
                    del rec_value['current_pkt_direction']
            except:
                pass
            self.out_file_pointer.write('%s\n' % json.dumps(rec_value))
            self.out_file_pointer.flush()