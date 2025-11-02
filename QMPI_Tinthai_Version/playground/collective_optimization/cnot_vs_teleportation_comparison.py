"""
เปรียบเทียบระหว่าง CNOT Gate และ Quantum Teleportation
สำหรับการแทนที่ใน broadcast.ipynb
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import matplotlib.pyplot as plt

def create_cnot_circuit():
    """สร้าง circuit ที่ใช้ CNOT gate แบบเดิม"""
    # สร้าง registers
    epr_qubit = QuantumRegister(1, name="epr")
    target_qubit = QuantumRegister(1, name="target")
    
    circuit = QuantumCircuit(epr_qubit, target_qubit)
    
    # เตรียม EPR qubit ในสถานะ superposition
    circuit.h(epr_qubit[0])
    
    # CNOT gate (วิธีเดิม)
    circuit.cx(epr_qubit[0], target_qubit[0])
    
    return circuit

def create_teleportation_circuit():
    """สร้าง circuit ที่ใช้ quantum teleportation"""
    # สร้าง registers
    source_qubit = QuantumRegister(1, name="source")  # EPR qubit
    target_qubit = QuantumRegister(1, name="target")  # target node
    ancilla_qubit = QuantumRegister(1, name="ancilla") # ancilla สำหรับ teleportation
    classical_bits = ClassicalRegister(2, name="cbits")
    
    circuit = QuantumCircuit(source_qubit, target_qubit, ancilla_qubit, classical_bits)
    
    # เตรียม source qubit ในสถานะ superposition
    circuit.h(source_qubit[0])
    
    # Quantum Teleportation Protocol
    # Step 1: สร้าง Bell pair ระหว่าง ancilla และ target
    circuit.h(ancilla_qubit[0])
    circuit.cx(ancilla_qubit[0], target_qubit[0])
    
    # Step 2: Bell measurement ระหว่าง source และ ancilla
    circuit.cx(source_qubit[0], ancilla_qubit[0])
    circuit.h(source_qubit[0])
    
    # Step 3: วัด source และ ancilla qubits
    circuit.measure(source_qubit[0], classical_bits[0])
    circuit.measure(ancilla_qubit[0], classical_bits[1])
    
    # Step 4: Conditional operations บน target qubit
    circuit.cx(ancilla_qubit[0], target_qubit[0])  # ถ้า ancilla = 1
    circuit.cz(source_qubit[0], target_qubit[0])   # ถ้า source = 1
    
    return circuit

def compare_circuits():
    """เปรียบเทียบ circuit ทั้งสอง"""
    cnot_circuit = create_cnot_circuit()
    teleport_circuit = create_teleportation_circuit()
    
    print("=== เปรียบเทียบ CNOT vs Quantum Teleportation ===\n")
    
    print("1. CNOT Gate (วิธีเดิม):")
    print(f"   - จำนวน qubits: {cnot_circuit.num_qubits}")
    print(f"   - จำนวน classical bits: {cnot_circuit.num_clbits}")
    print(f"   - ความลึก (depth): {cnot_circuit.depth()}")
    print(f"   - จำนวน gates: {len(cnot_circuit.data)}")
    print()
    
    print("2. Quantum Teleportation (วิธีใหม่):")
    print(f"   - จำนวน qubits: {teleport_circuit.num_qubits}")
    print(f"   - จำนวน classical bits: {teleport_circuit.num_clbits}")
    print(f"   - ความลึก (depth): {teleport_circuit.depth()}")
    print(f"   - จำนวน gates: {len(teleport_circuit.data)}")
    print()
    
    print("3. ข้อดี-ข้อเสียของแต่ละวิธี:")
    print()
    print("CNOT Gate:")
    print("   ข้อดี:")
    print("   - ใช้ resource น้อย (2 qubits)")
    print("   - รวดเร็ว (1 gate operation)")
    print("   - เข้าใจง่าย")
    print("   ข้อเสีย:")
    print("   - ไม่มีความปลอดภัยแบบ quantum")
    print("   - ไม่สามารถตรวจจับการดักฟังได้")
    print()
    print("Quantum Teleportation:")
    print("   ข้อดี:")
    print("   - ความปลอดภัยสูง (quantum security)")
    print("   - ตรวจจับการดักฟังได้")
    print("   - เหมาะสำหรับ quantum network")
    print("   - รองรับ distributed quantum computing")
    print("   ข้อเสีย:")
    print("   - ใช้ resource มากกว่า (3 qubits + 2 classical bits)")
    print("   - ซับซ้อนกว่า (หลาย operations)")
    print("   - ต้องใช้ classical communication")
    
    return cnot_circuit, teleport_circuit

def show_circuits():
    """แสดง circuit diagrams"""
    cnot_circuit, teleport_circuit = compare_circuits()
    
    print("\n=== Circuit Diagrams ===\n")
    
    print("CNOT Circuit:")
    print(cnot_circuit.draw())
    print()
    
    print("Quantum Teleportation Circuit:")
    print(teleport_circuit.draw())

def practical_implementation_guide():
    """คู่มือการใช้งานจริงใน broadcast.ipynb"""
    print("\n=== คู่มือการแทนที่ใน broadcast.ipynb ===\n")
    
    print("ขั้นตอนการแทนที่:")
    print("1. เพิ่ม import สำหรับ teleportation functions")
    print("2. สร้าง ancilla qubits และ classical registers")
    print("3. แทนที่ CNOT gates ด้วย teleportation protocol")
    print()
    
    print("โค้ดที่ต้องแทนที่:")
    print("```python")
    print("# เดิม:")
    print("collective_circuit_tinthai.q.cx(node1_epr[0], node1[0])")
    print("collective_circuit_tinthai.q.cx(node2_epr[0], node2[0])")
    print("collective_circuit_tinthai.q.cx(node3_epr[0], node3[0])")
    print()
    print("# ใหม่:")
    print("# เพิ่ม ancilla qubits")
    print("ancilla1 = QuantumRegister(1, name='ancilla1')")
    print("ancilla2 = QuantumRegister(1, name='ancilla2')")
    print("ancilla3 = QuantumRegister(1, name='ancilla3')")
    print()
    print("# เพิ่ม classical registers")
    print("c1 = ClassicalRegister(2, name='c1')")
    print("c2 = ClassicalRegister(2, name='c2')")
    print("c3 = ClassicalRegister(2, name='c3')")
    print()
    print("# เพิ่ม registers ลงใน circuit")
    print("collective_circuit_tinthai.q.add_register(ancilla1)")
    print("collective_circuit_tinthai.q.add_register(ancilla2)")
    print("collective_circuit_tinthai.q.add_register(ancilla3)")
    print("collective_circuit_tinthai.q.add_register(c1)")
    print("collective_circuit_tinthai.q.add_register(c2)")
    print("collective_circuit_tinthai.q.add_register(c3)")
    print()
    print("# ทำ quantum teleportation")
    print("quantum_teleportation(collective_circuit_tinthai.q, node1_epr[0], node1[0], ancilla1[0], c1)")
    print("quantum_teleportation(collective_circuit_tinthai.q, node2_epr[0], node2[0], ancilla2[0], c2)")
    print("quantum_teleportation(collective_circuit_tinthai.q, node3_epr[0], node3[0], ancilla3[0], c3)")
    print("```")

if __name__ == "__main__":
    show_circuits()
    practical_implementation_guide()