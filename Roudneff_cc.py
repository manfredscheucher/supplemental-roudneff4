# description: Given a database (in "txt" format) of chirotopes of uniform oriented matroids,
#              this program computes the number of complete cells of those matroids and save the
#              outcomes in a text file.
# (c) 2023 Rangel Hernández-Ortiz, Kolja Knauer, Luis Pedro Montejano and Manfred Scheucher

from Complete_cells import *
import datetime
from multiprocessing import Pool 
import math

time_start = datetime.datetime.now()

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("ifp",type=str,help="path to input file with oriented matroids")
parser.add_argument("n",type=int,help="number of elements")
parser.add_argument("r",type=int,help="rank")
parser.add_argument("--parallel",action="store_true",help="run in parallel")
parser.add_argument("--DEBUG","-D",action="store_true",help="debug mode")

args = parser.parse_args()
vargs = vars(args)
print("c\tactive args:",{x:vargs[x] for x in vargs if vargs[x] != None and vargs[x] != False})

r = args.r
n = args.n
DEBUG = args.DEBUG

elements = list(range(n)) # Create ground set
SB = support_basis(elements, r) # Create the support of all basis in reverse lexicographic order
SC = support_circuits(elements, r) # Create the support of all circuits
counter = 0

print("read input file:",args.ifp)
input_lines = list(open(args.ifp).readlines())
print("read",len(input_lines),"chirotopes")


def process_line(line):
    Chirotope = convert_chirotope(line) #Convert each chirotope in a (1,-1)-list
    Circuits = create_circuits(Chirotope, elements, r, SB, SC) #Create oriented circuits
    X = Complete(r, n, Circuits) #Compute the number of complete cells
    return X
      

print("start solving")
time_before_solving = datetime.datetime.now()

if args.parallel:
    p = Pool(20)
    output = p.map(process_line,input_lines) # run in parallel
else:
    output = list(map(process_line,input_lines)) # run single threaded

time_end = datetime.datetime.now()
print("solving time :",time_end-time_before_solving)


ofp = args.ifp + ".cells.txt"
print("write to output file:",ofp)
outfile = open(ofp,"w") # The number of complete will be saved in this file

stats = {}
# summarize stats
for counter,X in enumerate(output):
    outfile.write("{}\n".format(X)) #Save the result
    if DEBUG: print("Class {} --->".format(counter+1), X) #Print the number of complete cells
    if X not in stats: stats[X] = 0
    stats[X] += 1

# test conjecture
max_topes = 2*(math.comb(r-1,n-r+1) + math.comb(r-2,n-r) + sum(math.comb(n-1,i) for i in range(r-2)))
print("upper-bound:",max_topes) # cf. Roudneff; Montejano and Ramírez-Alfonsín
for counter,X in enumerate(output):
    if X > max_topes:
        print(80*"-")
        print("found counterexample with n =",n,"r =",r,"has more than",max_topes,"topes")
        print("Class {} --->".format(counter+1), X) #Print the number of complete cells
        print("OM as string:",input_lines[counter])
        print(80*"-")
        exit()

print("stats:",stats)
print("minimum:",min(stats),"(",stats[min(stats)],"times )")
print("maximum:",max(stats),"(",stats[max(stats)],"times )")

outfile.close()

