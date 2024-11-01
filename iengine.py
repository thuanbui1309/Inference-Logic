import sys
from truthTable import TruthTable

def main():
    if len(sys.argv) == 3:
        filename = sys.argv[1]
        method = sys.argv[2]

        if (method == "TT"):
            tt = TruthTable(filename)
            tt.run()
        elif (method == "FC"):
            print("Forward Chaining")
        elif (method == "BC"):
            print("Backward Chaining")
        elif (method == "RES"):
            print("Resolution")
        elif (method == "DPLL"):
            print("DPLL")
        else:
            print("Invalid method")
            sys.exit()
    else:
        print("Invalid number of arguments")
        sys.exit()

if __name__ == "__main__":
    main()