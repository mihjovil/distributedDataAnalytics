from mpi4py import MPI
import time

# MPI.Init()
comm = MPI.COMM_WORLD  # Initializes the MPI enviroment
rank = comm.Get_rank()  # Gets one of the workers to do something
size = comm.Get_size()  # Gets the amount of workers
name = MPI.Get_processor_name()
root = 0

dimension = 10**3
time0 = 0
time1 = 0

"""
The product of two matrix (Dot product) is the resulting matrix of the linear combinations between the 
rows of the first matrix and the columns of the second one.
In order to calculate the dot product of both matrixes, the second matrix will be, after created, shifted 
in order to make it easier to do the operations
"""
def create_structures():
    matrixA = [[0 for x in range(dimension)] for y in range(dimension)]
    matrixB = [[0 for x in range(dimension)] for y in range(dimension)]
    for i in range(dimension):
        for j in range(dimension):
            matrixA[i][j] = i + j
            matrixB[i][j] = i*j     # Creates and fills both matrixes
    couple = [matrixA,matrixB]
    return couple

def shift_matrix(matrix):           # Rotates the matrix in order to do linear combination with rows instead of columns
    new_matrix =[[0 for x in range(dimension)] for y in range(dimension)]
    for i in range(dimension):
        for j in range(dimension):
            new_matrix[j][i] = matrix[i][j]
    return new_matrix               # The new rotated matrix is returned for the product operation

def calculate_rows(rows):           # This function calculates the result of the linear combination of two rows (One position in the final result matrix)
    row1 = rows[0]
    row2 = rows[1]
    result = 0
    for r,p in zip(row1,row2):
        result+=r*p
    #print(row1,row2,result)
    return result                   # This result would be one number from the resulting matrix

if rank == root:
    matrixes = create_structures()      # The root creates the matrixes
    x1 = matrixes[0]                    # The first matrix
    x2 = matrixes[1]                    # The second matrix
    print("Starting the timer.....")
    time0 = MPI.Wtime()
    x3 = shift_matrix(x2)               # The result of rotating the second matrix, in order to do linear combinations with rows instead of clumns
    send_vector = []
    for i in range(size):               # In this loop, the first matrix is going to be divided in as many parts as ranks are.
        if i != size-1:
            # In order for the parts to be as similar as possible in size, the lenght of the matrix is divided by the amount of ranks
            pieceX1 = x1[ (len(x1)//size)*i:i * (len(x1)//size) + len(x1)//size]
            send_vector.append([pieceX1,x3])            # All ranks need the rotated matrix in order to calculate the result matrix
        else:                                               # The last rank will get whatever is left from the matrix
            pieceX1 = x1[i * (len(x1) // size):len(x1)]
            send_vector.append([pieceX1,x3])
else:
    send_vector=None                                    # only the root gets to send the matrixes

recv = comm.scatter(send_vector,root)
rowsM1 = recv[0]                            # The first element from the array is a list of rows (Piece of matrix 1)
matrix2 = recv[1]                           # The second element from the array is matrix 2 rotated
result_matrix = []
result_row = []
for i in range(len(rowsM1)):
    for j in range(len(matrix2)):
        result_row.append(calculate_rows([rowsM1[i],matrix2[j]]))       # Calculates the rows from the result matrix
    result_matrix.append(result_row)                                    # Appends the rows to create the matrix
gath = comm.gather(result_matrix,root)                                  # the root receives the pieces of the result matrix
if rank == root:
    result = []
    for i in gath:
        result.append(i)                                # Gets the final answer by joining the results from the matrix
    time1 = MPI.Wtime()
    print("The total time to do the operation was {} seconds".format(time1-time0))
