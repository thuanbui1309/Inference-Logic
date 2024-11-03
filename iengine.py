import sys
from truthTable import TruthTable
from forwardChaining import ForwardChaining
from backwardChaining import BackwardChaining

def main():
    if len(sys.argv) == 3:
        filename = sys.argv[1]
        method = sys.argv[2]

        if (method == "TT"):
            tt = TruthTable(filename)
            tt.run()
        elif (method == "FC"):
            FC = ForwardChaining(filename)
            FC.run()
        elif (method == "BC"):
            BC = BackwardChaining(filename)
            BC.run()
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