import sys
import json
from collections import OrderedDict
import optparse

def main():
    parser = optparse.OptionParser()
    parser.add_option('-i','--input',action='store',dest='input',help='no one will help you but you',default=None)
    parser.add_option('-o','--output',action='store',dest='output',help='no one will help you but you',default=sys.stdout)
    parser.add_option('-l','--label',action='store',dest='label',help='no one will help you but you',default=None)
    outfile_pointer = sys.stdout
    options, args = parser.parse_args()
    if options.input == None:
        print ('error: need a input file')
        return
    if options.output != sys.stdout:
        out_file_pointer = open(options.output, 'a')
    if options.label != None:
        label = options.label
    else:
        print('error: need label')
        return

    with open(options.input,'r') as fd:
        lines = fd.readlines()
        for line in lines:
            metadata = json.loads(line, object_pairs_hook=OrderedDict)
            flow_list = []
            for item in metadata:
                flow_list.append(list(item.values()))
            flow_list.append(label)
            out_file_pointer.write('%s\n' % json.dumps(flow_list))
            out_file_pointer.flush()

    if outfile_pointer != sys.stdout:
        outfile_pointer.close()


if __name__ == '__main__':
    sys.exit(main())
