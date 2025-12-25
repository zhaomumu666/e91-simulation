import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
from qiskit.quantum_info import Statevector, random_statevector
from qiskit.visualization import plot_histogram
import random
import itertools

# ==================== Configuration Parameters ====================
N = 10000  # Number of particle pairs to simulate
np.random.seed(42)  # Fix random seed for reproducibility
# Alice's and Bob's measurement basis angles (in radians)
angles_alice = [0, np.pi/4, np.pi/2]          # a1=0°, a2=45°, a3=90°
angles_bob = [np.pi/4, np.pi/2, 3*np.pi/4]    # b1=45°, b2=90°, b3=135°

# ==================== Core Function Definitions ====================
def create_singlet_state():
    qc = QuantumCircuit(2, 2)
    qc.x(0)          
    qc.h(0)          
    qc.cx(0, 1)      
    qc.z(0)          
    qc.x(1)          
    return qc

def measure_in_basis(qc, qubit_index, angle):
    qc.ry(-2 * angle, qubit_index)

def simulate_measurement(state_vector, angle):
    rand = np.random.random()
    return 1 if rand < 0.5 else -1

def calculate_correlation(results_alice, results_bob):
    if len(results_alice) != len(results_bob):
        raise ValueError("Result lengths do not match")
    n = len(results_alice)
    if n == 0:
        return 0
    correlation = sum(a * b for a, b in zip(results_alice, results_bob))
    return correlation / n

# ==================== Main Simulation Class ====================
class E91Simulator:
    def __init__(self, num_pairs=N):
        self.num_pairs = num_pairs
        self.results = {
            'alice_bases': [], 'bob_bases': [], 'alice_results': [], 'bob_results': [],
            'eve_bases': [], 'eve_results': []
        }
    
    def simulate_ideal_scenario(self):
        print("="*60)
        print("Simulating Ideal Scenario (No Eve)")
        print("="*60)
        self._reset_results()
        
        for i in range(self.num_pairs):
            alice_basis_idx = np.random.randint(0, 3)
            bob_basis_idx = np.random.randint(0, 3)
            alice_angle = angles_alice[alice_basis_idx]
            bob_angle = angles_bob[bob_basis_idx]
            
            # Perfect anticorrelation for matched bases (a2-b1, a3-b2)
            if (alice_basis_idx == 1 and bob_basis_idx == 0) or (alice_basis_idx == 2 and bob_basis_idx == 1):
                alice_result = 1 if np.random.random() < 0.5 else -1
                bob_result = -alice_result
            else:
                angle_diff = alice_angle - bob_angle
                correlation = -np.cos(angle_diff)
                prob_same = (1 + correlation) / 2
                if np.random.random() < prob_same:
                    alice_result = 1 if np.random.random() < 0.5 else -1
                    bob_result = alice_result
                else:
                    alice_result = 1 if np.random.random() < 0.5 else -1
                    bob_result = -alice_result
            
            self.results['alice_bases'].append(alice_basis_idx)
            self.results['bob_bases'].append(bob_basis_idx)
            self.results['alice_results'].append(alice_result)
            self.results['bob_results'].append(bob_result)
        
        print(f"Completed simulation for {self.num_pairs} particle pairs")
        return self._analyze_results("Ideal Scenario")
    
    def simulate_eavesdropping_scenario(self, eavesdrop_prob=1.0):
        print("\n" + "="*60)
        print("Simulating Eavesdropping Scenario (With Eve)")
        print("="*60)
        self._reset_results()
        self.results['eve_bases'] = []
        self.results['eve_results'] = []
        
        for i in range(self.num_pairs):
            eve_eavesdrops = np.random.random() < eavesdrop_prob
            
            if eve_eavesdrops:
                eve_basis_idx = np.random.randint(0, 3)
                eve_angle = angles_bob[eve_basis_idx]
                eve_result = 1 if np.random.random() < 0.5 else -1
                eve_state = eve_result
                
                alice_basis_idx = np.random.randint(0, 3)
                alice_result = 1 if np.random.random() < 0.5 else -1
                
                bob_basis_idx = np.random.randint(0, 3)
                bob_angle = angles_bob[bob_basis_idx]
                angle_diff = eve_angle - bob_angle
                
                if bob_basis_idx == eve_basis_idx:
                    bob_result = eve_state
                else:
                    delta_theta = angle_diff
                    prob_same = np.cos(delta_theta/2)**2
                    bob_result = eve_state if np.random.random() < prob_same else -eve_state
                
                self.results['eve_bases'].append(eve_basis_idx)
                self.results['eve_results'].append(eve_result)
            else:
                alice_basis_idx = np.random.randint(0, 3)
                bob_basis_idx = np.random.randint(0, 3)
                alice_angle = angles_alice[alice_basis_idx]
                bob_angle = angles_bob[bob_basis_idx]
                
                if (alice_basis_idx == 1 and bob_basis_idx == 0) or (alice_basis_idx == 2 and bob_basis_idx == 1):
                    alice_result = 1 if np.random.random() < 0.5 else -1
                    bob_result = -alice_result
                else:
                    angle_diff = alice_angle - bob_angle
                    correlation = -np.cos(angle_diff)
                    prob_same = (1 + correlation) / 2
                    if np.random.random() < prob_same:
                        alice_result = 1 if np.random.random() < 0.5 else -1
                        bob_result = alice_result
                    else:
                        alice_result = 1 if np.random.random() < 0.5 else -1
                        bob_result = -alice_result
                
                self.results['eve_bases'].append(-1)
                self.results['eve_results'].append(0)
            
            self.results['alice_bases'].append(alice_basis_idx)
            self.results['bob_bases'].append(bob_basis_idx)
            self.results['alice_results'].append(alice_result)
            self.results['bob_results'].append(bob_result)
        
        print(f"Completed simulation for {self.num_pairs} particle pairs (Eavesdrop Probability: {eavesdrop_prob*100}%)")
        return self._analyze_results("Eavesdropping Scenario", eavesdrop_prob)
    
    def _reset_results(self):
        for key in ['alice_bases', 'bob_bases', 'alice_results', 'bob_results']:
            self.results[key] = []
    
    def _analyze_results(self, scenario_name, eavesdrop_prob=0.0):
        print(f"\nAnalyzing {scenario_name} Results:")
        print("-" * 40)
        
        alice_bases = np.array(self.results['alice_bases'])
        bob_bases = np.array(self.results['bob_bases'])
        alice_results = np.array(self.results['alice_results'])
        bob_results = np.array(self.results['bob_results'])
        
        # Calculate E values for all basis combinations (including matched bases)
        mask_a1b1 = (alice_bases == 0) & (bob_bases == 0)  # a1=0°-b1=45°
        mask_a1b3 = (alice_bases == 0) & (bob_bases == 2)  # a1=0°-b3=135°
        mask_a3b1 = (alice_bases == 2) & (bob_bases == 0)  # a3=90°-b1=45°
        mask_a3b3 = (alice_bases == 2) & (bob_bases == 2)  # a3=90°-b3=135°
        mask_a2b1 = (alice_bases == 1) & (bob_bases == 0)  # a2=45°-b1=45° (Matched Basis)
        mask_a3b2 = (alice_bases == 2) & (bob_bases == 1)  # a3=90°-b2=90° (Matched Basis)
        
        # Compute all E values
        E_a1b1 = self._calc_E_for_mask(mask_a1b1, alice_results, bob_results)
        E_a1b3 = self._calc_E_for_mask(mask_a1b3, alice_results, bob_results)
        E_a3b1 = self._calc_E_for_mask(mask_a3b1, alice_results, bob_results)
        E_a3b3 = self._calc_E_for_mask(mask_a3b3, alice_results, bob_results)
        E_a2b1 = self._calc_E_for_mask(mask_a2b1, alice_results, bob_results)  # E for matched basis
        E_a3b2 = self._calc_E_for_mask(mask_a3b2, alice_results, bob_results)  # E for matched basis
        
        # Calculate CHSH value
        S = E_a1b1 - E_a1b3 + E_a3b1 + E_a3b3
        print(f"E(a1,b1) = {E_a1b1:.4f}")
        print(f"E(a1,b3) = {E_a1b3:.4f}")
        print(f"E(a3,b1) = {E_a3b1:.4f}")
        print(f"E(a3,b3) = {E_a3b3:.4f}")
        print(f"E(a2,b1) [Matched Basis] = {E_a2b1:.4f}")
        print(f"E(a3,b2) [Matched Basis] = {E_a3b2:.4f}")
        print(f"CHSH Value S = {S:.4f}")
        print(f"|S| = {abs(S):.4f}")
        
        # Key generation analysis
        mask_key = mask_a2b1 | mask_a3b2
        key_indices = np.where(mask_key)[0]
        num_key_bits = len(key_indices)
        qber = 0
        if num_key_bits > 0:
            alice_key_bits = np.array([0 if r == 1 else 1 for r in alice_results[key_indices]])
            bob_key_bits = np.array([0 if r == 1 else 1 for r in bob_results[key_indices]])
            errors = np.sum(alice_key_bits != bob_key_bits)
            qber = errors / num_key_bits
            print(f"\nKey Generation Analysis:")
            print(f"  Number of bits available for key: {num_key_bits}")
            print(f"  Quantum Bit Error Rate (QBER): {qber:.4f} ({qber*100:.2f}%)")
        
        # Security analysis
        print(f"\nSecurity Analysis:")
        print(f"  Theoretical Quantum Maximum: |S| = {2*np.sqrt(2):.4f} ≈ 2.8284")
        print(f"  Classical Local Realism Upper Bound: |S| ≤ 2.0000")
        if abs(S) > 2.0:
            print(f"  ✓ |S| = {abs(S):.4f} > 2.0, Violates Bell Inequality")
            print(f"  ✓ Quantum Entanglement Detected")
        else:
            print(f"  ✗ |S| = {abs(S):.4f} ≤ 2.0, Consistent with Classical Local Realism")
        
        return {
            'S': S, '|S|': abs(S),
            'E_a1b1': E_a1b1, 'E_a1b3': E_a1b3, 'E_a3b1': E_a3b1, 'E_a3b3': E_a3b3,
            'E_a2b1': E_a2b1, 'E_a3b2': E_a3b2,
            'num_key_bits': num_key_bits, 'qber': qber, 'scenario': scenario_name
        }
    
    def _calc_E_for_mask(self, mask, alice_results, bob_results):
        if np.sum(mask) == 0:
            return 0.0
        alice_masked = alice_results[mask]
        bob_masked = bob_results[mask]
        return np.mean(alice_masked * bob_masked)
    
    # -------------------------- Plot Correlation Coefficients (All English) --------------------------
    # 替换这一行（Windows绝对路径示例，改成你的桌面路径）
    def plot_correlation_coefficients(self, ideal_results, eavesdrop_results, save_path="C:/Users/33602/Desktop/correlation_plot.png"):
        """
        Plot correlation coefficients for different basis combinations (all English elements)
        Matches requirements: Highlight perfect anticorrelation for matched bases, quantum predictions, and Eve's attack impact
        """
        # 1. Basis combination labels (English, distinguish CHSH vs. matched bases)
        basis_labels = [
            "a1-b1 (CHSH)",
            "a1-b3 (CHSH)",
            "a3-b1 (CHSH)",
            "a3-b3 (CHSH)",
            "a2-b1 (Matched Basis)",  # Key: Perfect anticorrelation basis
            "a3-b2 (Matched Basis)"   # Key: Perfect anticorrelation basis
        ]
        
        # 2. Extract E values for both scenarios (order matches labels)
        E_ideal = [
            ideal_results['E_a1b1'],
            ideal_results['E_a1b3'],
            ideal_results['E_a3b1'],
            ideal_results['E_a3b3'],
            ideal_results['E_a2b1'],  # E for matched basis (≈-1 in ideal case)
            ideal_results['E_a3b2']   # E for matched basis (≈-1 in ideal case)
        ]
        E_eve = [
            eavesdrop_results['E_a1b1'],
            eavesdrop_results['E_a1b3'],
            eavesdrop_results['E_a3b1'],
            eavesdrop_results['E_a3b3'],
            eavesdrop_results['E_a2b1'],  # E for matched basis (deviates from -1 with Eve)
            eavesdrop_results['E_a3b2']   # E for matched basis (deviates from -1 with Eve)
        ]
        
        # 3. Create plot
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 4. Bar plot setup
        x = np.arange(len(basis_labels))
        width = 0.35  # Width of each bar
        
        # 5. Plot bars for both scenarios
        bars1 = ax.bar(x - width/2, E_ideal, width, label='Ideal Scenario (No Eve)', color='#2E86AB', alpha=0.8)
        bars2 = ax.bar(x + width/2, E_eve, width, label='Eavesdropping Scenario (With Eve)', color='#A23B72', alpha=0.8)
        
        # 6. Add reference line for perfect anticorrelation (E=-1)
        ax.axhline(y=-1.0, color='#F18F01', linestyle='--', linewidth=2, label='Perfect Anticorrelation (E=-1)')
        
        # 7. Plot labels & title (all English)
        ax.set_xlabel('Basis Combinations', fontsize=12)
        ax.set_ylabel('Correlation Coefficient E', fontsize=12)
        ax.set_title('Figure 3: Correlation Coefficients for Different Basis Combinations', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(basis_labels, rotation=15, ha='right')  # Rotate labels to avoid overlap
        ax.legend(fontsize=10)
        
        # 8. Add value labels on top of bars
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02 if height > 0 else height - 0.05,
                        f'{height:.4f}', ha='center', va='bottom' if height > 0 else 'top', fontsize=9)
        add_value_labels(bars1)
        add_value_labels(bars2)
        
        # 9. Adjust layout & save
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\nCorrelation coefficient plot saved to: {save_path}")

# ==================== Run Simulation ====================
def main():
    simulator = E91Simulator(num_pairs=10000)
    
    # 1. Run both scenarios
    ideal_results = simulator.simulate_ideal_scenario()
    eavesdrop_results = simulator.simulate_eavesdropping_scenario(eavesdrop_prob=1.0)
    
    # 2. Generate the required correlation plot (all English)
    simulator.plot_correlation_coefficients(ideal_results, eavesdrop_results)
    
    # 3. (Optional) Run original 2x2 subplot visualization
    # simulator.visualize_results(ideal_results, eavesdrop_results)
    
    # 4. Summary report
    print("\n" + "="*60)
    print("E91 Protocol Simulation Summary Report")
    print("="*60)
    # (Summary content remains, adjusted to English as needed)

# ==================== Execute Main Function ====================
if __name__ == "__main__":
    main()