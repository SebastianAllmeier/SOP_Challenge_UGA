from helper.parser import parser, filenames


if __name__ == "__main__":
    sol_path = "Data/solutions/"
    sop_path = "Data/course_benchmark_instances/"

    sop_files, sol_files = filenames([sol_path, sop_path])

    arcs = []
    sols = []

    for i in range(len(sop_files)-1):
        arcs += [parser(sop_files[i], True)]
        sols += [parser(sol_files[i], True)]

    print("DONE")

