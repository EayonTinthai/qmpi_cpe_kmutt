import math
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator

# สร้าง quantum circuit สำหรับ broadcast operation โดยใช้ quantum teleportation
collective_circuit_tinthai = QuantumCircuit()

# สร้าง quantum registers สำหรับ nodes
node1 = QuantumRegister(1, name="node1")
node2 = QuantumRegister(1, name="node2") 
node3 = QuantumRegister(1, name="node3")

# สร้าง quantum registers สำหรับ EPR pairs
node1_epr = QuantumRegister(1, name="node1_epr")
node2_epr = QuantumRegister(1, name="node2_epr")
node3_epr = QuantumRegister(1, name="node3_epr")

# สร้าง classical registers สำหรับ measurement
node1_measure = ClassicalRegister(2, name="node1_measure")  # 2 bits สำหรับ teleportation
node2_measure = ClassicalRegister(2, name="node2_measure")
node3_measure = ClassicalRegister(2, name="node3_measure")

# เพิ่ม registers เข้าใน circuit
collective_circuit_tinthai.add_register(node1, node1_epr)
collective_circuit_tinthai.add_register(node2, node2_epr)
collective_circuit_tinthai.add_register(node3, node3_epr)
collective_circuit_tinthai.add_register(node1_measure, node2_measure, node3_measure)

# Initialize node1[0] ให้มีโอกาส |0⟩ ~85%
collective_circuit_tinthai.rx(math.pi/4, node1[0])

# สร้าง EPR pairs ระหว่าง EPR qubits
# EPR pair ระหว่าง node1_epr[0] และ node2_epr[0]
collective_circuit_tinthai.h(node1_epr[0])
collective_circuit_tinthai.cx(node1_epr[0], node2_epr[0])

# EPR pair ระหว่าง node1_epr[0] และ node3_epr[0] (ใช้ node2_epr[0] เป็นตัวกลาง)
collective_circuit_tinthai.h(node2_epr[0])
collective_circuit_tinthai.cx(node2_epr[0], node3_epr[0])

collective_circuit_tinthai.barrier()

# Quantum Teleportation จาก node1[0] ไป node1_epr[0]
# Bell measurement
collective_circuit_tinthai.cx(node1[0], node1_epr[0])
collective_circuit_tinthai.h(node1[0])

# Measure
collective_circuit_tinthai.measure(node1[0], node1_measure[0])
collective_circuit_tinthai.measure(node1_epr[0], node1_measure[1])

collective_circuit_tinthai.barrier()

# Apply corrections based on measurement results
# สำหรับ node2_epr[0]
with collective_circuit_tinthai.if_test((node1_measure[1], 1)):
    collective_circuit_tinthai.x(node2_epr[0])
with collective_circuit_tinthai.if_test((node1_measure[0], 1)):
    collective_circuit_tinthai.z(node2_epr[0])

# สำหรับ node3_epr[0] 
with collective_circuit_tinthai.if_test((node1_measure[1], 1)):
    collective_circuit_tinthai.x(node3_epr[0])
with collective_circuit_tinthai.if_test((node1_measure[0], 1)):
    collective_circuit_tinthai.z(node3_epr[0])

collective_circuit_tinthai.barrier()

# Teleport จาก EPR qubits ไป node qubits
# จาก node2_epr[0] ไป node2[0]
collective_circuit_tinthai.cx(node2_epr[0], node2[0])
collective_circuit_tinthai.h(node2_epr[0])
collective_circuit_tinthai.measure(node2_epr[0], node2_measure[0])

with collective_circuit_tinthai.if_test((node2_measure[0], 1)):
    collective_circuit_tinthai.z(node2[0])

# จาก node3_epr[0] ไป node3[0]  
collective_circuit_tinthai.cx(node3_epr[0], node3[0])
collective_circuit_tinthai.h(node3_epr[0])
collective_circuit_tinthai.measure(node3_epr[0], node3_measure[0])

with collective_circuit_tinthai.if_test((node3_measure[0], 1)):
    collective_circuit_tinthai.z(node3[0])

collective_circuit_tinthai.barrier()

# Final measurements สำหรับดูผลลัพธ์
final_measure = ClassicalRegister(3, name="final_measure")
collective_circuit_tinthai.add_register(final_measure)

collective_circuit_tinthai.measure(node1[0], final_measure[0])
collective_circuit_tinthai.measure(node2[0], final_measure[1])
collective_circuit_tinthai.measure(node3[0], final_measure[2])

# Function สำหรับ run และแสดงผล
def run_teleportation_broadcast():
    sim = AerSimulator()
    transpiled_circuit = transpile(collective_circuit_tinthai, sim)
    result = sim.run(transpiled_circuit, shots=1024).result()
    counts = result.get_counts()
    
    print("Quantum Teleportation Broadcast Results:")
    print("Classical registers (right→left): final_measure[3] → node3_measure[2] → node2_measure[2] → node1_measure[2]")
    print("\nCounts:")
    for bits, count in counts.items():
        print(f"{bits} : {count}")
    
    # คำนวณความน่าจะเป็นของแต่ละ node
    total = sum(counts.values())
    
    # สำหรับ final measurements (3 bits สุดท้าย)
    node1_prob_0 = sum(v for k, v in counts.items() if k.split()[-1][0] == '0') / total
    node2_prob_0 = sum(v for k, v in counts.items() if k.split()[-1][1] == '0') / total  
    node3_prob_0 = sum(v for k, v in counts.items() if k.split()[-1][2] == '0') / total
    
    print(f"\nFinal Node States:")
    print(f"Node1 P(|0⟩) = {node1_prob_0:.4f}, P(|1⟩) = {1-node1_prob_0:.4f}")
    print(f"Node2 P(|0⟩) = {node2_prob_0:.4f}, P(|1⟩) = {1-node2_prob_0:.4f}")
    print(f"Node3 P(|0⟩) = {node3_prob_0:.4f}, P(|1⟩) = {1-node3_prob_0:.4f}")

if __name__ == "__main__":
    print("Circuit depth:", collective_circuit_tinthai.depth())
    print("Number of qubits:", collective_circuit_tinthai.num_qubits)
    print("Number of classical bits:", collective_circuit_tinthai.num_clbits)
    print("\nRunning teleportation broadcast...")
    run_teleportation_broadcast()