# Quantum Teleportation Protocol สำหรับแทนที่ CNOT gates
# ใช้แทนบรรทัดเหล่านี้:
# collective_circuit_tinthai.q.cx(node1_epr[0], node1[0])
# collective_circuit_tinthai.q.cx(node2_epr[0], node2[0])
# collective_circuit_tinthai.q.cx(node3_epr[0], node3[0])

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def quantum_teleportation(circuit, source_qubit, target_qubit, ancilla_qubit, classical_bits):
    """
    Quantum Teleportation Protocol
    
    Args:
        circuit: QuantumCircuit object
        source_qubit: qubit ที่ต้องการส่ง state
        target_qubit: qubit ปลายทางที่จะรับ state
        ancilla_qubit: ancilla qubit สำหรับ Bell pair
        classical_bits: classical register สำหรับเก็บผลการวัด
    """
    
    # Step 1: สร้าง Bell pair ระหว่าง ancilla และ target
    circuit.h(ancilla_qubit)
    circuit.cx(ancilla_qubit, target_qubit)
    
    # Step 2: Bell measurement ระหว่าง source และ ancilla
    circuit.cx(source_qubit, ancilla_qubit)
    circuit.h(source_qubit)
    
    # Step 3: วัด source และ ancilla qubits
    circuit.measure(source_qubit, classical_bits[0])
    circuit.measure(ancilla_qubit, classical_bits[1])
    
    # Step 4: Conditional operations บน target qubit
    circuit.cx(ancilla_qubit, target_qubit)  # ถ้า ancilla = 1
    circuit.cz(source_qubit, target_qubit)   # ถ้า source = 1

# ตัวอย่างการใช้งานแทนที่ CNOT gates เดิม:

def replace_cnot_with_teleportation(collective_circuit_tinthai, node_epr, node, classical_reg):
    """
    แทนที่ CNOT gate ด้วย quantum teleportation
    
    Args:
        collective_circuit_tinthai: circuit หลัก
        node_epr: EPR qubit
        node: target node qubit  
        classical_reg: classical register สำหรับการวัด
    """
    
    # เพิ่ม ancilla qubit สำหรับ teleportation
    ancilla = QuantumRegister(1, name=f"ancilla_{node.register.name}")
    collective_circuit_tinthai.add_register(ancilla)
    
    # เพิ่ม classical bits สำหรับการวัด
    if classical_reg is None:
        classical_reg = ClassicalRegister(2, name=f"c_{node.register.name}")
        collective_circuit_tinthai.add_register(classical_reg)
    
    # ทำ quantum teleportation
    quantum_teleportation(
        collective_circuit_tinthai, 
        node_epr[0],      # source qubit (EPR)
        node[0],          # target qubit (node)
        ancilla[0],       # ancilla qubit
        classical_reg     # classical bits
    )

# สำหรับการแทนที่ใน broadcast.ipynb:
"""
# แทนที่บรรทัดเดิม:
# collective_circuit_tinthai.q.cx(node1_epr[0], node1[0])
# collective_circuit_tinthai.q.cx(node2_epr[0], node2[0])  
# collective_circuit_tinthai.q.cx(node3_epr[0], node3[0])

# ด้วยโค้ดใหม่:

# เพิ่ม classical registers สำหรับการวัด
c1 = ClassicalRegister(2, name="c1")
c2 = ClassicalRegister(2, name="c2")
c3 = ClassicalRegister(2, name="c3")

collective_circuit_tinthai.q.add_register(c1)
collective_circuit_tinthai.q.add_register(c2)
collective_circuit_tinthai.q.add_register(c3)

# แทนที่ CNOT ด้วย teleportation
replace_cnot_with_teleportation(collective_circuit_tinthai.q, node1_epr, node1, c1)
replace_cnot_with_teleportation(collective_circuit_tinthai.q, node2_epr, node2, c2)
replace_cnot_with_teleportation(collective_circuit_tinthai.q, node3_epr, node3, c3)
"""