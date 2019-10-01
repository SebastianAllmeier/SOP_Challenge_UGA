# sop to something parser

import numpy as np

def parser(data_path, show_comments=False):
    """

    :param data: - string -  data path e.g. 'Data/course_benchmark_instances/ESC07.sop'
    :return: as numpy array parsed data

    parser method parses sop !!and sol!!  files to a 2 or 1 dimensional numpy array

    NOTE: only .sop files as given in the course_benchmark_instance.zip file will work

    TODO: include detection of sop, sol files and add skript for sol files
    """

    # initial console output
    if show_comments:
        print("Parsing data from: '{0}'".format(data_path))

    # read data
    with open(data_path) as f:
        read_data = f.read()

    # split rows (first row which contains dimension information will still be in first
    # entry of the list)
    row_strings = read_data.split('\t\n')

    # separate dimension and first row and save / replace them
    dimension, row_strings[0] = row_strings[0].split('\n')

    #convert dimension to integer
    dimension = int(dimension)

    # create empty np array with matching output size
    output = np.zeros(shape=(dimension, dimension))

    # fill output array with values
    for i in range(dimension):
        output[i, :] = np.fromstring(row_strings[i], dtype=int, sep='\t')

    # just some string output
    if show_comments:
        print("Data was parsed into a ({0},{1}) matrix.".format(*output.shape))

    return output


if __name__ == "__main__":
    arcs = parser('Data/course_benchmark_instances/ESC07.sop', True)
    print("DONE")
