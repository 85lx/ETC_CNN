import optparse
import sys
from flow_analyser import Flow_Analyser


def main():
    parser = optparse.OptionParser()
    parser.add_option('-i','--input',action='store',dest='input',help='pcap file or interface name',default=None)
    parser.add_option('-o','--output',action='store',dest='output',help='name for output file',default=sys.stdout)
    parser.add_option('-s','--session',action='store_true',dest='session',help='analyze based on session')
    parser.add_option('-m','--map',action='store_true',dest='map',help='output flow or session using xl map')

    
    options, args = parser.parse_args()

    input_files = []
    if options.input != None:
        input_files.append(options.input)
    for x in args:
        if x.endswith('.pcap') or x.endswith('.pcapng'):
            input_files.append(x)
    
    analyser = Flow_Analyser(output=options.output, session=options.session,map=options.map)

    if len(input_files) > 0:
        analyser.extract_flow_record(input_files)
    else:
        print ('error: need a pcap/interface')
        return 1


if __name__ == '__main__':
    sys.exit(main())