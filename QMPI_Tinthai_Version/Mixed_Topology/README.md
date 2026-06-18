# Star Topology Quantum Network - Broadcast Implementation

Implementation of two quantum broadcast methods for star topology networks using Qiskit.

## Overview

Star topology with 7 nodes:
- **Node 0 (Root)**: Central hub
- **Nodes 1-6**: Client nodes

```
    Node1
      |
Node2-Node0-Node6
    / | \
Node3 Node4 Node5
```

## Two Methods

### Method 1: Central Node as Source (CNS)
**File**: `approach1_sequential_epr.ipynb`

Root generates GHZ state and broadcasts via teleportation.

#### Steps
1. **GHZ Generation**: Root creates 7-qubit GHZ state locally
2. **Distribution**: Root keeps 1 qubit, distributes 6 to clients
3. **BSM**: Root performs Bell State Measurement on data qubit + GHZ qubit
4. **Broadcast**: Clients apply Pauli corrections (X/Z) based on BSM results

#### Quantum State
```
|GHZ⟩ = (|0000000⟩ + |1111111⟩)/√2
```

#### Classical Communication
- 2 bits (BSM results) broadcast to all clients

---

### Method 2: Central Node as Switch (CNSw)
**File**: `approach2_ghz_distribution.ipynb`

Root acts as entanglement switch, fusing EPR pairs into GHZ state.

#### Steps
1. **EPR Generation**: Each client creates EPR pair with root
2. **GHZ Fusion**: Root performs entanglement swapping on EPR halves
3. **Correction**: Clients apply Z gates based on fusion measurements
4. **BSM**: Root performs Bell State Measurement on data qubit
5. **Broadcast**: Clients apply Pauli corrections

#### Classical Communication
- 6 bits (fusion results) + 2 bits (BSM) = 8 bits total

---

## Comparison

| Feature | Method 1 (CNS) | Method 2 (CNSw) |
|---------|----------------|-----------------|
| **GHZ Creation** | At root | Distributed |
| **EPR Pairs** | No | Yes (6 pairs) |
| **Entanglement Swapping** | No | Yes |
| **Classical Bits** | 2 | 8 |
| **Circuit Depth** | Lower | Higher |
| **Scalability** | Better | Good |

## Requirements

```bash
pip install qiskit qiskit-aer matplotlib jupyter
```

## Usage

```bash
jupyter notebook approach1_sequential_epr.ipynb
jupyter notebook approach2_ghz_distribution.ipynb
```

## Circuit Architecture

Both methods use same quantum circuit with different node groups:
- **14 qubits total**
- Different qubit groups represent different nodes
- Compatible with SuperMarQ benchmarking

### Method 1 Qubits
- q0: Data qubit
- q1: Root GHZ qubit
- q2-q7: Client GHZ qubits

### Method 2 Qubits
- q0: Data qubit
- q1-q6: Root EPR halves
- q7: Ancilla for fusion
- q8-q13: Client EPR halves

## Key Differences

**Method 1**: Root is entanglement **source**
- Simpler, fewer classical bits
- Root generates all entanglement

**Method 2**: Root is entanglement **switch**
- More complex, distributed generation
- Clients participate in EPR creation
- Demonstrates entanglement swapping

## References

Based on: Analysis of Multipartite Entanglement Distribution using a CQNN

## License

Educational and research purposes.
