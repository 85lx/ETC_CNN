
from collections import OrderedDict
from binascii import hexlify, unhexlify
import dpkt
import datetime

MAX_TCP_RETRANS_BUFFER = 10
MAX_PKT_NUM = 100000
MAX_PKT_MAP_NUM = 50
DATA_LEN = 64
PADDING = b'\x00'
PADDING_INT = 0

class Tcp_analyser:

    def __init__(self,session=False):
        self.session = session
        self.pkt_map_padding = self.construct_pkt_map_padding()
        return

    def retrans_detected(self, record, seq_num, data_len):
        rc = 0
        if self.session == True and record['current_pkt_direction'] == '<':
           retrans_list = record['twin_tcp_retrans']
        else:
            retrans_list = record['tcp_retrans']
        #look for the sequence number in the stored array
        for retrans in retrans_list:
            if retrans['seq'] == seq_num:
                if retrans['len'] < data_len: 
                    print("Retransmission with new data detected! SEQ(%x), Orig LEN(%d), New LEN (%d)"  \
                        %(seq_num, retrans['len'], data_len))
                    # update length with new length
                    #retrans['len'] = data_len 
                    rc = 2
                else:
                    print("Retransmission detected! SEQ(%x), LEN(%d)" %(seq_num, data_len))
                    rc = 1
                break
        return rc


    def flow_record_process (self, record, time_stamp, ip):
        
        # IPv6 is not supported now
        # if (type(ip) != dpkt.ip.IP and type(ip) != dpkt.ip6.IP6) or type(ip.data) != dpkt.tcp.TCP:
        if type(ip) != dpkt.ip.IP or type(ip.data) != dpkt.tcp.TCP:
            return record
        #make sure we have room in the array 
        if record['pkt_num'] >= (MAX_PKT_NUM):
            return record  #no more room

        #store the sequence number and length into the retransmission buffer
        tcp = ip.data
        retrans = {}
        retrans['seq'] = tcp.seq
        retrans['len'] = len(tcp.data)
        if self.session == True and record['current_pkt_direction'] == '<':
            record['twin_tcp_retrans'].append(retrans)
            if len(record['twin_tcp_retrans'])==MAX_TCP_RETRANS_BUFFER+1:
                record['twin_tcp_retrans'].pop(0)
        else:
            record['tcp_retrans'].append(retrans)
            if len(record['tcp_retrans'])==MAX_TCP_RETRANS_BUFFER+1:
                record['tcp_retrans'].pop(0)

        # TODO: figure out the features using xl58_features for machine learning
        # ******************************************************************
        # *************************

        #*****************************************
        #store the packet infomation using xl58_flow_representation for deep learning
        record['pkt_num'] += 1
        pkt = OrderedDict({})
        if self.session == True:
            pkt['direction'] = record['current_pkt_direction']
        pkt['time_stamp'] = time_stamp
        pkt['data_len'] = len(tcp.data)
        pkt['ip_content'] = hexlify(ip.__bytes__()).decode()
        record['pkt_info'].append(pkt)

    def ip_tcp_map(self, record):
        start_time = datetime.datetime.utcfromtimestamp(record['start_time_stamp'])

        pkt_num = 0
        pkt_map_list =[]
        
        for pkt in record['pkt_info']:
            if pkt_num >= MAX_PKT_MAP_NUM:
                break
            pkt_num += 1
            pkt_map = OrderedDict({})
            if self.session == True: 
                if pkt['direction'] == '>':
                    pkt_map['direction_forward'] =  1
                    pkt_map['direction_backward'] = 0
                    init_seq = record['init_seq']
                elif pkt['direction'] == '<':
                    pkt_map['direction_forward'] =  0
                    pkt_map['direction_backward'] = 1
                    init_seq = record['init_seq_backward']
            else:
                init_seq = record['init_seq']

            pkt_time = datetime.datetime.utcfromtimestamp(pkt['time_stamp'])
            relative_time = (pkt_time - start_time).microseconds
            pkt_map['time'] = relative_time
            
            #IP_header_map
            ip = dpkt.ip.IP(unhexlify(pkt['ip_content']))
            pkt_map['ip_len'] = ip.len
            pkt_map['ip_df'] = ip.df 
            pkt_map['ip_mf'] = ip.mf
            pkt_map['ip_ttl'] = ip.ttl
            
            #TCP_header_map
            tcp = ip.data
            pkt_map['th_seq'] = tcp.seq - init_seq
            pkt_map['URG'] = (tcp.flags>>5) & 0x01
            pkt_map['PSH'] = (tcp.flags>>3) & 0x01
            #pkt_map['RST'] = (tcp.flags>>2) & 0x01
            #pkt_map['FIN'] = (tcp.flags>>0) & 0x01
            pkt_map['th_win'] = tcp.win
            pkt_map['th_urp'] = tcp.urp
            if len(tcp.data) >= DATA_LEN:
                pkt_map['data'] = hexlify(tcp.data[:DATA_LEN]).decode()
            else:
                pad_cnt = DATA_LEN - len(tcp.data)
                data_tmp = tcp.data
                while pad_cnt > 0:
                    data_tmp += PADDING
                    pad_cnt -= 1
                pkt_map['data'] = hexlify(data_tmp).decode()
            pkt_map_list.append(pkt_map)
        if (len(pkt_map_list) < MAX_PKT_MAP_NUM) and (len(pkt_map_list) > 0):
            pad_len = MAX_PKT_MAP_NUM - len(pkt_map_list)
            while pad_len > 0:
                pkt_map_list.append(self.pkt_map_padding)
                pad_len -= 1
        if (len(pkt_map_list) != MAX_PKT_MAP_NUM) and (len(pkt_map_list) != 0) :
            print('error !!!!')
        return pkt_map_list

    def construct_pkt_map_padding(self):
        pkt_map_padding = OrderedDict({})
        if self.session == True:
            pkt_map_padding['direction_forward'] =  PADDING_INT
            pkt_map_padding['direction_backward'] = PADDING_INT
        pkt_map_padding['time'] = PADDING_INT
        pkt_map_padding['ip_len'] = PADDING_INT
        pkt_map_padding['ip_df'] = PADDING_INT
        pkt_map_padding['ip_mf'] = PADDING_INT
        pkt_map_padding['ip_ttl'] = PADDING_INT
        pkt_map_padding['th_seq'] = PADDING_INT
        pkt_map_padding['URG'] = PADDING_INT
        pkt_map_padding['PSH'] = PADDING_INT
        pkt_map_padding['th_win'] = PADDING_INT
        pkt_map_padding['th_urp'] = PADDING_INT
        local_data=b''
        cnt = DATA_LEN
        while cnt > 0:
            local_data += PADDING
            cnt -= 1
        pkt_map_padding['data'] = hexlify(local_data).decode()
        return pkt_map_padding