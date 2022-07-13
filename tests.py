from solver import main as solve
import os
import sys
import subprocess
from time import time

def main():
    correct = 0
    incorrect = 0
    wrong_but_initially_infeasible = 0

    filenames = os.listdir("./data/input")
    for filename in filenames:
        print("\nDoing {}".format(filename))
        ts = time()
        completed = subprocess.run(["python", "solver.py", "./data/input/" + filename], stdout=subprocess.PIPE)
        te = time()
        with open("./data/output/" + filename, "r") as f:
            answer = f.readlines()
            answer = [x.rstrip() for x in answer if len(x.rstrip()) > 0]
        output = completed.stdout.decode("utf-8")
        output = output.split('\n')[:-1]
        output[-1] = output[-1].rstrip()
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
            incorrect += 1

    print("\n\n{} correct, {} incorrect, {} initially infeasible, {} actually wrong".format(correct, incorrect, wrong_but_initially_infeasible, incorrect - wrong_but_initially_infeasible)) 


if __name__ == "__main__":
    main()