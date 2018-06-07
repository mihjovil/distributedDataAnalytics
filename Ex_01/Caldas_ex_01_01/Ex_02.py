from mpi4py import MPI
import time

# MPI.Init()
comm = MPI.COMM_WORLD  # Initializes the MPI enviroment
rank = comm.Get_rank()  # Gets one of the workers to do something
size = comm.Get_size()  # Gets the amount of workers
name = MPI.Get_processor_name()
root = 0
dimension = 10**4       # Dimension used for vector and matrix
time0 = 0
time1 = 0

def create_estructures():       # Creates the matrix and vector needed for the exercise

    matrix = [[0 for x in range(dimension)] for y in range(dimension)]
    for i in range(dimension):
        for j in range(dimension):
            matrix[i][j] = i+j          # Creates and fills the matrix
    vector = []
    for i in range(dimension):
        vector.append(i)                # Creates and fills the vector
    return [matrix,vector]              # return a tuple with both structures

def calculate_tuple(tupla):             # Function used to make the linear combination of a scalar and the numbers within a vector
    row = tupla[0]                      # a vector that comes in the parameters of the function
    number = tupla[1]                   # a number that comes with the parameter of the function
    result = 0
    for r in row:
        result += r*number              # linear combination of elements in the vector with number
    return result                       # the result of the linear combination

if rank == root:
    structures = create_estructures()
    matrix = structures[0]              # Here is the matrix
    vector = structures[1]              # Here is the vector
    print("Starting the timer...")
    time0 = MPI.Wtime()
    rows = []                           # a vector that will store a slice of the rows of the matrix
    numbers = []                        # a vector to store a slice of the vector's numbers
    for i in range(dimension//size):
        rows.append(matrix[i])          # adds a row from the matrix
        numbers.append(vector[i])       # adds a number from the vector
    send_matrix = matrix [dimension//size:len(matrix)]      # the rest of the matrix to send to the next rank
    send_vector = vector[dimension//size:len(vector)]       # the rest of the vector to send to the next rank
    tuple = [send_matrix,send_vector]                       # an array with the remaining matrix and vector to send only once to the next rank
    comm.send(tuple, dest = rank+1, tag = 11)               # Sends to the next rank
    result_vector = []
    for i in range(len(rows)):
        result_vector.append(calculate_tuple([rows[i],numbers[i]])) # Calls a function to calculate the product of the number with the matrix row and stores this values in an array
    comm.send(result_vector, dest = rank+1, tag=12)                 # Sends the result of the linear combinations to the next rank

else:
    tuple = comm.recv(source = rank-1, tag=11)              # Receives the remaining of matrix and vector
    matrix = tuple[0]
    vector = tuple[1]
    if rank != size-1:                                      # Checks if it is not the last rank
        rows = []
        numbers = []
        for i in range(dimension // size):
            rows.append(matrix[i])                          # Takes its share of matrix rows
            numbers.append(vector[i])
        send_matrix = matrix[dimension // size:len(matrix)] # Sends the rest to the next rank
        send_vector = vector[dimension // size:len(vector)]
        tuple = [send_matrix, send_vector]                     # An aaray to send matrix and vector at the same time
        comm.send(tuple, dest=rank + 1, tag=11)
        result_vector = []
        coming_row = comm.recv(source=rank-1,tag=12)            # Receives the previous calculations of linear combinations
        for i in range(len(rows)):
            result_vector.append(calculate_tuple([rows[i], numbers[i]]))    # Calculates its own values
        coming_row += result_vector                                         # Sums the previous and actual results
        comm.send(coming_row, dest=rank + 1, tag=12)                        # Sends the new results
    else:                                                                   # being the last one it must calculate for the remaining matrix and vector
        result_vector = []
        coming_row = comm.recv(source=rank - 1, tag=12)
        for i in range(len(matrix)):
            result_vector.append(calculate_tuple([matrix[i], vector[i]]))
        coming_row += result_vector                                             # Sums the previous and actual result
        comm.send(result_vector, dest = root, tag = 1)                      # Signals the root that the process finished
if rank == root:
    answer = comm.recv(source = size-1, tag = 1)
    print("The root received the result vector")
    time1 = MPI.Wtime()
    print("The total time to do the process was {} seconds".format(time1 - time0))