import json
import random
from binascii import  hexlify,unhexlify

class Load_map:
    def __init__(self):
        return
    def load_data(self,filename):
        x_data = []
        y_data = []
        with open(filename,'r') as fd:
            lines = fd.readlines()
            random.shuffle(lines)
            for line in lines:
                x_data_item = []
                x_map = json.loads(line)
                y = x_map[-1]
                y_data.append(y)
                del x_map[-1]
                for x_item in x_map:
                    app_data = x_item[-1]
                    data_list = list(unhexlify(app_data))
                    del x_item[-1]
                    x_item.extend(data_list)
                    x_data_item.append(x_item)
                x_data.append(x_data_item)
        return x_data,y_data

#test code
#l = Load_map()
#(x,y) = l.load_data('out.json')
#print (x[0])
#print (y[0])

