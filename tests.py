from solver import main as solve
import os
import sys
import subprocess
from time import time

def main():
    correct = 0
    incorrect = 0
    timedout = 0
    wrong_but_initially_infeasible = 0

    #filenames = os.listdir("./data/input")
    filenames = ["vanderbei_exercise2.10.txt"]
    for filename in filenames:
        print("\nDoing {}".format(filename))
        ts = time()
        try:
            completed = subprocess.run(["python", "solver.py", "./data/input/" + filename], stdout=subprocess.PIPE, timeout=5)
        except subprocess.TimeoutExpired:
            print("\nTimeout")
            timedout += 1
            incorrect += 1
            continue
        except Exception as e:
            print(f"Filename: {filename} produced an error: {e}")
            quit()
        te = time()
        with open("./data/output/" + filename, "r") as f:
            answer = f.readlines()
            answer = [x.rstrip() for x in answer if len(x.rstrip()) > 0]
        output = completed.stdout.decode("utf-8")
        if len(output) > 1:
            output = output.split('\n')[:-1]
            output[-1] = output[-1].rstrip()
        else:
            output = []
        #print("\nSolver output:")
        #print(output)
       # print("\nCorrect answer:")
        #print(answer)
        print("Time: {:.4g}".format(te-ts))
        if output == answer:
            print("Correct.")
            correct += 1
        elif output == ["initially infeasible"]:
            print("Initially infeasible")
            incorrect += 1
            wrong_but_initially_infeasible += 1
        else: 
            print("Incorrect")
            if len(filenames) == 1:
                print(f"Output:/n{output}")
                print(f"Answer:/n{answer}")
            incorrect += 1

    print("\n\n{} correct, {} incorrect, {} initially infeasible, {} actually wrong, {} timed out".format(correct, incorrect, wrong_but_initially_infeasible, incorrect - wrong_but_initially_infeasible - timedout, timedout)) 


if __name__ == "__main__":
    main()