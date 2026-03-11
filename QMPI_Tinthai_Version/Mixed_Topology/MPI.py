# This is to implement the MPI framework
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# class for doing point to point communication
class EPRsetup: 
    def __init__(self, q, srcBit, destBit, n=2) -> None:
        self.q = q
        self.srcBit = srcBit
        self.destBit = destBit

        # for easy look up for the names of quantum & classical registers to the actual register
        qregs = {}
        l = len(q.qregs)
        for i in range(l):
            qregs[q.qregs[i].name] = q.qregs[i]

            if self.findRegName(q, srcBit) == q.qregs[i].name:
                self.srcIndex = i
            if self.findRegName(q, destBit) == q.qregs[i].name:
                self.destIndex = i

        cregs = {}
        for j in q.cregs: 
            cregs[j.name] = j # the 2nd index is for recording if it's used and what result it gives
        self.qr = qregs
        self.cr = cregs

        nameSRC = self.findRegName(q,srcBit)
        nameDEST = self.findRegName(q,destBit)
        self.EPRsrcbit = self.qr[nameSRC + "_epr"][0]
        self.EPRdestbit = self.qr[nameDEST+"_epr"][0]
        self.Csrcbit = self.cr[nameSRC+"_epr_creg"][0]
        self.Cdestbit = self.cr[nameDEST+"_epr_creg"][0]
        #self.Csrcbit2 = self.cr[nameSRC+"_epr_creg"][1]
        #self.Cdestbit2 = self.cr[nameDEST+"_epr_creg"][1]


        # for the 2nd qubit for tp_comm
        if n == 2:
            self.EPRsrcbit2 = self.qr[nameSRC + "_epr"][1]
            self.EPRdestbit2 = self.qr[nameDEST+"_epr"][1]

    # find the register associated with qubit in quantumcircuit q
    # returns the name of the quantum register associated with qubit
    @staticmethod
    def findRegName(q, bit):
        #print(q.cregs)
        #print(bit)
        #print(q.find_bit(bit))
        return q.find_bit(bit)[1][0][0].name

    # this function makes an epr pair between qubits s and d. This should be an abstraction to a general EPR pair making scheme
    @staticmethod
    def makeEPRPair(q, s, d):
        q.h(s)
        q.cx(s,d) 

    # this is the "recieve part" where I think there has to be some post processing to get the measurement of the epr bit
    def recieveEPR(self, q, qbit, cbit):
        q.measure(qbit, cbit)
        #print(cbit)
        self.q.metadata[EPRsetup.findRegName(self.q,cbit)] = 1

    # implemnt MPI send function via teleportation (TP_COMM)
    # returns the instructions for a send operation
    def send(self):
        qq = QuantumCircuit()
        qq.add_bits([self.srcBit, self.EPRsrcbit, self.EPRdestbit, self.Csrcbit])
        self.makeEPRPair(qq, self.EPRsrcbit, self.EPRdestbit)
        qq.cx(self.srcBit, self.EPRsrcbit)
        self.recieveEPR(qq, self.EPRsrcbit, self.Csrcbit)
        #qq.x(self.EPRdestbit).c_if(self.Csrcbit,1)
        with qq.if_test((self.Csrcbit,1)):
            qq.x(self.EPRdestbit)
        qq.h(self.srcBit)
        self.recieveEPR(qq, self.srcBit,self.Csrcbit)

        ### This is Tinthai recommendation ###
        # We need to put barrier after measurement
        # To eliminate the wrong phase
        qq.barrier(self.srcBit, self.EPRsrcbit, self.EPRdestbit)

        #qq.z(self.EPRdestbit).c_if(self.Csrcbit2,1)
        with qq.if_test((self.Csrcbit,1)):
            qq.z(self.EPRdestbit)

        qq.reset(self.EPRsrcbit)
        qq.barrier()
        return qq.data
    
    # implemnt cnot
    def cnot(self):
        qq = QuantumCircuit()
        qq.add_bits([self.destBit, self.EPRdestbit])
        qq.cx(self.EPRdestbit, self.destBit)
        qq.barrier()
        return qq.data
    
    # implemnt swap
    def swap(self):
        qq = QuantumCircuit()
        qq.add_bits([self.destBit, self.EPRdestbit, self.srcBit])
        qq.swap(self.EPRdestbit, self.destBit)
        qq.reset([self.srcBit, self.EPRdestbit])
        qq.barrier()
        return qq.data

    #tp_comm version of unsend
    def unsend(self):
        qq = QuantumCircuit()
        qq.add_bits([self.srcBit, self.EPRdestbit, self.Cdestbit, self.EPRdestbit2, self.EPRsrcbit2])
        self.makeEPRPair(qq, self.EPRsrcbit2, self.EPRdestbit2)
        qq.swap(self.srcBit, self.EPRsrcbit2)
        qq.cx(self.EPRdestbit, self.EPRdestbit2)
        self.recieveEPR(qq, self.EPRdestbit2, self.Cdestbit)
        #qq.x(self.srcBit).c_if(self.Cdestbit,1)
        with qq.if_test((self.Cdestbit,1)):
            qq.x(self.srcBit)
        qq.h(self.EPRdestbit)
        self.recieveEPR(qq, self.EPRdestbit,self.Cdestbit)
        #qq.z(self.srcBit).c_if(self.Cdestbit2,1)
        with qq.if_test((self.Cdestbit,1)):
            qq.z(self.srcBit)

        qq.reset([self.EPRdestbit, self.EPRdestbit2, self.EPRsrcbit2])
        qq.barrier()
        return qq.data

    # implemnt MPI copy function via fanout (Cat_COMM)
    def copy(self):
        qq = QuantumCircuit()
        qq.add_bits([self.srcBit, self.EPRsrcbit, self.EPRdestbit, self.Csrcbit])
        self.makeEPRPair(qq, self.EPRsrcbit, self.EPRdestbit)
        qq.cx(self.srcBit, self.EPRsrcbit)
        self.recieveEPR(qq, self.EPRsrcbit, self.Csrcbit)
        #qq.x(self.EPRdestbit).c_if(self.Csrcbit,1)
        with qq.if_test((self.Csrcbit,1)):
            qq.x(self.EPRdestbit)
        qq.reset(self.EPRsrcbit)
        qq.barrier()
        return qq.data
    
    #cat_comm version of uncopy
    def uncopy(self):
        qq = QuantumCircuit()
        qq.add_bits([self.srcBit, self.EPRdestbit, self.Cdestbit])
        qq.h(self.EPRdestbit)
        self.recieveEPR(qq, self.EPRdestbit,self.Cdestbit)
        #qq.z(self.srcBit).c_if(self.Cdestbit,1)
        with qq.if_test((self.Cdestbit,1)):
            qq.z(self.srcBit)
        qq.reset([self.EPRdestbit])
        qq.barrier()
        return qq.data
    
    # implement control unitary between eprdest and dest qubits
    def controlU(self, gates):
        qq = QuantumCircuit()
        qq.add_bits([self.destBit, self.EPRdestbit])
        qq.compose(gates, qubits = [self.EPRdestbit, self.destBit], inplace = True)
        qq.barrier()
        return qq.data