from mpi4py import MPI
import time

# MPI.Init()
comm = MPI.COMM_WORLD  # Initializes the MPI enviroment
rank = comm.Get_rank()  # Gets one of the workers to do something
size = comm.Get_size()  # Gets the amount of workers
name = MPI.Get_processor_name()
root = 0
time0 = 0
time1 = 0
time2 = 0


dimension = 10**7

def create_vectors():  # Function to do the process without parallel computing
    vectorX = [i + 1 for i in range(dimension)]  # Creates a vector of numbers
    vectorY = [(j + 1) * 2 for j in range(dimension)]  # Another Vector to add
    return [vectorX, vectorY];

if rank == 0:       # Only the root gets the vectors
    print("Creating the random vectors")
    vectors = create_vectors()
    X = vectors[0]      # First vector
    Y = vectors[1]      # Second vector
    print("Starting timer...")
    time0 = MPI.Wtime()                     # Starts a timer after constructing the vector (which takes some time)
    myXpice = X[0:dimension//size]                # It's gonna take a piece of the vector (slice)
    sendX = X[dimension//size : dimension]          # The rest of the vector is going to be send.
    myYpiece = Y[0:dimension//size]             # The sice of the slice is the total size of the vector divided exactly in the amount of ranks (So the pieces are similar in size)
    sendY = Y[dimension//size:dimension]        # From the last position sliced to the rest of it. It's gonna be send

    send = [sendX,sendY]                        # To send in just one connection, an array is made with both vectors
    comm.send(send, dest = rank+1, tag = 11)    # Send to the next rank
    result = []                                 # Where the results of addition will be store
    for x,y in zip(myXpice,myYpiece):
        result.append(x+y)                      # The result of adding the elements of the sliced parts one by one
    comm.send(result, dest=rank+1, tag = 12)    # Now the array containing the results is send to the next rank
else:
    data = comm.recv(source = rank-1, tag = 11) # Receives vectors from the previous rank missing for addition
    X = data[0]                                 # First vector
    Y = data[1]                                 # Second vector
    if rank != size-1:                          # Checks if it is not the last rank
        myXpice = X[0:dimension // size]        # Same as root it takes a slice for own processing
        sendX = X[dimension // size: dimension]
        myYpiece = Y[0:dimension // size]
        sendY = Y[dimension // size:dimension]

        mypieces = [myXpice,myYpiece]
        send = [sendX, sendY]
        comm.send(send, dest=rank + 1, tag=11)  # Sends the remaining of the vectors to the next rank
        result = []
        for x, y in zip(myXpice, myYpiece):
            result.append(x + y)
        previous = comm.recv(source = rank-1, tag = 12) # Receives the results from the previous rank
        previous += result                              # unifies the previous results with its own
        comm.send(previous, dest=rank + 1, tag=12)      # Sends the result vector to the next rank
    else:                                       # If it is the last rank, it has to process whatever is left from the received vectors
        result = []
        for x, y in zip(X, Y):                  # Calculates for the remaining of the original two vectors
            result.append(x + y)
        previous = comm.recv(source=rank - 1, tag=12)   # Recieves the results from all previous ranks
        previous += result                              # Joins every result into one final vector
        comm.send(previous, dest = root, tag = 11)      # Sends the result to the root so part b can begin

# Second part
if rank==root:
    print("It Already has the result vector of adding the two random ones.")
    time1 = MPI.Wtime()
    print("It took a total of {} seconds to add the two vectors".format(time1-time0))
    z = comm.recv(source=size-1, tag=11)                # Receives one vector (The result from part a)

    myzpice = z[0:dimension // size]                    # Like part a, takes a slice from the vector
    sendz = z[dimension // size: dimension]
    comm.send(sendz, dest=rank + 1, tag=11)             # Sends the remaining of the vector to the next rank

    avg1 = sum(myzpice)                                 # Calculates the sum of all elements in the slice
    comm.send(avg1, dest = rank + 1, tag=12)            # Sends the result to next rank
else:
    Z = comm.recv(source=rank - 1, tag=11)              # Receives vector from previous rank

    if rank != size - 1:                                # Checks if it is not the last rank
        myZpice = Z[0:dimension // size]                # Takes a slice of the vector
        sendZ = Z[dimension // size: dimension]
        comm.send(sendZ, dest=rank + 1, tag=11)
        avg2 = sum(myZpice)                             # Calculates the sum of all elements in the slice

        S1 = comm.recv(source = rank-1, tag=12)         # Receives the result from previous rank
        avg2 += S1                                      # Sums the received result with own

        comm.send(avg2, dest=rank + 1, tag=12)          # Sends the new total result to next rank
    else:
        S2 = comm.recv(source=rank - 1, tag=12)         # Receives the result of all previous ranks
        avg2 = sum(Z)                                   # Calculates own sum of the remaining original vector
        S2 += avg2                                      # Sums all results
        MainAVG = S2/dimension                          # Divides the sum with the lenght of the vector to get the average
        comm.send(MainAVG, dest = root, tag = 1)
if rank == root:
    answer = comm.recv(source = size-1, tag = 1)
    time2 = MPI.Wtime()
    print("It took a total of {} seconds to do the whole operation, add the vectors and find the average".format(time2 - time0))
    print("AVERAGE: {}".format(answer))  # Prints the average of the vector


"""if rank == root:
    vectors = create_vectors()  # Receives the vectors created by the root
    print("Starting time...")
    start_time = time.time()  # Starts a timer after constructing the vector (which takes some time)
    X = vectors[0]  # The first vector
    Y = vectors[1]  # The second vector
    print(X,Y)
    matrixX = []  # Creates a vector of vectors, matrix, to divide the first vector into small ones
    matrixY = []  # A matrix to divide the second vector into smaller vectors
    # It will be a vector of vectors, just not right now.
    for i in range(size):  # The number of workers, and therefore mini-vectors
        lineX = []
        lineY = []
        if i != size - 1:
            lineX = X[len(X)//size * i:len(X)//size * i + len(X) // (size)]   # A sub-vector from the original vector X
            lineY = Y[len(Y)//size * i:len(Y)//size * i + len(Y) // (size)]   # A sub-vector from the original vector Y
            matrixX.append(lineX)                                               # Appends to the vector.
            matrixY.append(lineY)                                               # It is a vector of vectors
        else:
            lineX = X[len(X)//size * i:len(X)]          # Being the last one, has to append whatever is left
            lineY = Y[len(Y)//size * i:len(Y)]          # Same here
            matrixX.append(lineX)
            matrixY.append(lineY)
else:
    matrixX = None
    matrixY = None

recv = comm.scatter(matrixX,root)               # Scatters the first vector to the other workers
receive = comm.scatter(matrixY,root)            # Now scatters the second
result = []
for r,p in zip(recv,receive):
    result.append(r+p)              # Each worker adds the sub-vectors received
gath = comm.gather(result,root)     # Each worker sends its results.
if rank == root:                    # Only the root gathers
    Z = []                          # The resulting vector
    for i in range(size):
        Z += gath[i]
    print("--- %s seconds until unifying the two vectors---" % (time.time() - start_time))  # Prints the time elapsed in total
    print(Z)
    sending_vectors = []            # The vectors to send to get the average
    for i in range(size):
        if i!= size-1:
            sending_vectors.append(Z[len(Z)//size * i:len(Z)//size * i + len(Z) // (size)])
        else:
            sending_vectors.append(Z[len(Z)//size * i:len(Z)])
else:
    sending_vectors = None

recv = comm.scatter(sending_vectors,root)               # Scatters the vector to the other workers
average = 0
for n in recv:
    average += n
gath = comm.gather(average,root)
if rank == root:
    average = 0
    for r in gath:
        average += r
    average = average/len(Z)
    print("This is the average of the vector {}".format(average))
    print("--- %s seconds for the whole process---" % (
                time.time() - start_time))  # Prints the time elapsed in total
                """