# sop to something parser

import numpy as np

with open('Data/course_benchmark_instances/ESC07.sop') as f:
    read_data = f.read()


read_data = read_data.replace('\t\n', '; ').replace('\t', ' ')

dimension, read_data = read_data.split('\n')

dimension = int(dimension)
arcs = np.asarray(read_data, dtype='int32')
np.loadtxt()



print(read_data)
def parser(data):


    return
