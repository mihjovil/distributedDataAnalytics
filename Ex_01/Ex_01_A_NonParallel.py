from mpi4py import MPI
import time

# MPI.Init()
comm = MPI.COMM_WORLD  # Initializes the MPI enviroment
rank = comm.Get_rank()  # Gets one of the workers to do something
size = comm.Get_size()  # Gets the amount of workers
name = MPI.Get_processor_name()
root = 0


vectorX = [i + 1 for i in range(10**7)]  # Creates a vector of numbers
vectorY = [(j + 1) * 2 for j in range(10**7)]  # Another Vector to add

"""This Function is to do a trial when the work is done without parallel computing.
The whole operation is done by the main thread.
Creates a vectorX and a vectorY with int values, then iterating in both of them adds its values and appends
them in a vectocZ. In order not to print the whole vector, I don't see the point, only the last value is printed"""

vectorZ = []                                    #The result Vector

start_time = time.time()  # Starts a timer after constructing the vector (which takes some time)
for x, y in zip(vectorX,vectorY):
    vectorZ.append(x+y)
print("--- %s seconds ---" % (time.time() - start_time))  # Prints the time elapsed in total