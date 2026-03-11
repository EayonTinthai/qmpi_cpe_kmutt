# this is for the MPI collective operations
import MPI
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

class CollectiveMPI:

# add a epr register with n qubits and classical register with 1 bit for doing epr pairs 
    def __addEPRregisters(self, n):
        classDict = {}
        for j in range(self.length):
                i = self.q.qregs[j]
                newEPRReg = QuantumRegister(n, name = i.name+"_epr") 
                newEPRClassreg = ClassicalRegister(1, name = i.name+"_epr_creg")
                self.q.add_register(newEPRReg)
                self.q.add_register(newEPRClassreg)
                classDict[newEPRClassreg.name] = 0
        self.q.metadata = classDict

    def __init__(self, q, leader = None, n=2) -> None:
        self.q = q # quantum circuit 
        self.leader = leader # the root quantum register (DO I NEED THIS CONCEPT?)
        self.length = len(self.q.qregs) # number of quantum nodes
        self.__addEPRregisters(n) # add a register with n qubits for each node. epr pair gets reused

    # complete teleportation (send) 
    def __completeSend(self, eprClass):
        instr = eprClass.send()
        for i in instr: 
            self.q.append(i)
        instr = eprClass.cnot()
        for i in instr: 
            self.q.append(i)
        instr = eprClass.unsend()
        for i in instr: 
            self.q.append(i)

    # complete fanout (copy)
    def __completeCopy(self, eprClass):
        instr = eprClass.copy()
        for i in instr: 
            self.q.append(i)
        instr = eprClass.cnot()
        for i in instr: 
            self.q.append(i)
        instr = eprClass.uncopy()
        for i in instr: 
            self.q.append(i)
    
    # teleportation with swap (send) 
    def __teleSwap(self, eprClass):
        instr = eprClass.send()
        for i in instr: 
            self.q.append(i)
        instr = eprClass.swap()
        for i in instr: 
            self.q.append(i)


    # implements broadcast from the leader's qubit to all qregs in q to bits specified by arr
    # brodcasts first index in arr to all other indexs in arr
    # only can broadcast one qubit at a time b/c I think there's a faster way to do 2+ qubit teleportation
    def brodcast(self, arr):
        n = len(arr)
        counter = 1
        while (counter < n):
            i = 2*counter
            for j in range(counter):
                k = j + counter
                if k >= n:
                    break
                eprClass = MPI.EPRsetup(self.q, arr[j], arr[k], 1)
                self.__completeCopy(eprClass)    
            counter += counter
        
        # greedy brodcast
        #for i in range(self.length-1):
        #    eprClass = MPI.EPRsetup(self.q, qubit, arr[i])
        #    self.__completeSend(eprClass)
            

    # implements scatter from the qubits to all qregs in arr
    # qubits is the qubits to send and arr is an array where each index has the qubit to recieve
    def scatter(self, qubits, arr):
        num = len(qubits)
        assert num == len(arr)

        for i in range(num):
            eprClass = MPI.EPRsetup(self.q, qubits[i], arr[i], n=1)
            self.__teleSwap(eprClass)

    # implements gather from all regs in arr to qubits in one register specified by qubits array
    # inverse of scatter
    def gather(self, arr, qubits):
        self.scatter(arr, qubits)

    # implements allgather for q q
    # qubits are the qubits to send where each index in the array is coming from one register
    # arrs is a 2d array where the first index is the register and the second index is the qubits to recieve the qubits
    def allGather(self, qubits, arrs):
        for i in range(len(qubits)):
            for j in range(len(arrs)):
                self.brodcast(qubits[i], arrs[j][i]) # can probably parallelize this
    
    # reduce from all qubits in arr where controlled unitary gates are applied sequentially between each qubit in arr to qubit
    def reduce(self, arr, qubit, gates):
        for i in range(len(arr)):
            # teleport qubit from array to qubit 1 
            eprClass = MPI.EPRsetup(self.q, arr[i], qubit,n=1)
            instr = eprClass.copy()
            for i in instr: 
                self.q.append(i)
            instr = eprClass.controlU(gates)
            for i in instr: 
                self.q.append(i)
            instr = eprClass.uncopy()
            for i in instr: 
                self.q.append(i)

     # reduce sequentially as go down arrs applying gates
    def sequentialReduce(self, arr, gates):
        for i in range(len(arr)-1):
            # teleport qubit from array to qubit array[i+1]
            eprClass = MPI.EPRsetup(self.q, arr[i], arr[i+1],n=1)
            instr = eprClass.copy()
            for i in instr: 
                self.q.append(i)
            instr = eprClass.controlU(gates)
            for i in instr: 
                self.q.append(i)
            instr = eprClass.uncopy()
            for i in instr: 
                self.q.append(i)

    # mpi all reduce. same as reduce except qubits has to be a list where the first index has two qubits
    # and the rest of the list has one qubit for each different quantum register to brodcast too
    def allReduce(self, arr, qubits, gates):
        self.reduce(self, arr, qubits[0], gates)
        barr = qubits[1:]
        barr.insert(0, qubits[0][0])
        self.brodcast(barr)
    
    # qubits is a 2d array are the qubits to send where the first index in the array is coming from a register
    # arrs is a 2d array where the first index is the register and the second index is the qubits to recieve the qubits
    def alltoall(self, qubits, arrs):
        for i in range(len(qubits)):
                self.scatter(qubits[i], arrs[:][i]) # can probably parallelize this

    