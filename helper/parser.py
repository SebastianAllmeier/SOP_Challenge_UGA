# sop (and soon sol) to numpy array parser

import numpy as np

def filenames(relative_paths=None):
    """

    :param relative_paths: tuple, relative paths to sol and sop files
                            first entry -> path to .sol data, second -> path to .sop
    :return: returns array of paths to data files
    """
    names = [
        'ESC07',
        'ESC11',
        'ESC12',
        'ESC25',
        'ESC47',
        'ESC63',
        'ESC78',
        # 'kro124p.1',
        # 'kro124p.2',
        # 'kro124p.3',
        # 'kro124p.4',
        # 'R.500.1000.1',
        # 'R.500.1000.15',
        # 'R.500.1000.30',
        # 'R.500.1000.60',
        # 'R.600.1000.1',
        # 'R.600.1000.15',
        # 'R.600.1000.30',
        # 'R.600.1000.60',
        # 'R.700.1000.1',
        # 'R.700.1000.15',
        # 'R.700.1000.30',
        # 'R.700.1000.60',
        'ry48p.1',
        'ry48p.2',
        'ry48p.3',
        'ry48p.4'
    ]

    names_sol = []
    names_sop = []

    for name in names:
        if relative_paths is not None:
            names_sol += [relative_paths[0] + name + ".sol"]
            names_sop += [relative_paths[1] + name + ".sop"]
        else:
            names_sol += [name + ".sol"]
            names_sop += [name + ".sop"]

    return names_sop, names_sol

def parser(data_path, show_comments=False):
    """

    :param data: - string -  data path e.g. 'Data/course_benchmark_instances/ESC07.sop'
    :return: as numpy array parsed data

    parser method parses sop !!and sol!!  files to a 2 or 1 dimensional numpy array

    NOTE: only .sop files as given in the course_benchmark_instance.zip file will work
    """

    # get filetype
    file_type = data_path[-3:]


    # initial console output
    if show_comments:
        print("Parsing data from: '{0}'".format(data_path))

    # read data
    with open(data_path) as f:
        read_data = f.read()

    if file_type == 'sop': # separate procedure by file type
        if show_comments:
            print("Parsing {0} file".format(file_type))

        # split rows (first row which contains dimension information will still be in first
        # entry of the list)
        row_strings = read_data.split('\t\n')

        # separate dimension and first row and save / replace them
        dimension, row_strings[0] = row_strings[0].split('\n')

        # convert dimension to integer
        dimension = int(dimension)

        # create empty np array with matching output size
        output = np.zeros(shape=(dimension, dimension))

        # fill output array with values
        for i in range(dimension):
            output[i, :] = np.fromstring(row_strings[i], dtype=int, sep='\t')

        # just some string output
        if show_comments:
            print("Data was parsed into a ({0},{1}) matrix.\n".format(*output.shape))

        return output

    elif file_type == "sol":
        if show_comments:
            print("Parsing {0} file \n".format(file_type))

        # get rid of line break
        read_data = read_data[:-1]

        # values to np array
        values = np.fromstring(read_data, dtype=int, sep=' ')

        return values




if __name__ == "__main__":
    arcs = parser('../Data/course_benchmark_instances/ESC07.sop', True)
    sol = parser('../Data/solutions/ESC07.sol', True)

    print("DONE")
