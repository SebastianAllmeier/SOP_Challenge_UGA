from helper.parser import parser, filenames


if __name__ == "__main__":
    # directory paths
    sol_path = "Data/solutions/"
    sop_path = "Data/course_benchmark_instances/"

    # get filenames (files where solutions are given)
    sop_files, sol_files = filenames([sol_path, sop_path])

    # initialize array arcs and solutions
    instances = []

    # fill arrays
    for i in range(len(sop_files)-1):
        arcs = parser(sop_files[i], True)
        solution = parser(sol_files[i], True)
        instances += [(arcs, solution)]

    print("DONE")

