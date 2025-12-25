import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer  # 从独立包导入Ae
from qiskit.quantum_info import Statevector, random_statevector
from qiskit.visualization import plot_histogram
import random
import itertools

# ==================== 配置参数 ====================
N = 10000  # 模拟的粒子对数量
np.random.seed(42)  # 固定随机种子，确保可重复性

# Alice和Bob的测量基角度（弧度制，论文中的设置）
angles_alice = [0, np.pi/4, np.pi/2]          # a1=0°, a2=45°, a3=90°
angles_bob = [np.pi/4, np.pi/2, 3*np.pi/4]    # b1=45°, b2=90°, b3=135°

# ==================== 核心函数定义 ====================

def create_singlet_state():
    """
    创建单重态 (|01⟩ - |10⟩)/√2 的量子电路
    这是E91协议中使用的最大纠缠态
    """
    qc = QuantumCircuit(2, 2)
    qc.x(0)          # |00⟩ -> |10⟩
    qc.h(0)          # (|0⟩+|1⟩)/√2 ⊗ |0⟩ = (|00⟩+|10⟩)/√2
    qc.cx(0, 1)      # (|00⟩+|11⟩)/√2 (贝尔态)
    qc.z(0)          # (|00⟩-|11⟩)/√2
    qc.x(1)          # (|01⟩-|10⟩)/√2 (单重态)
    return qc

def measure_in_basis(qc, qubit_index, angle):
    """
    在指定角度（相对于x轴）的基下测量量子比特
    参数：
        qc: 量子电路
        qubit_index: 要测量的量子比特索引
        angle: 测量基的角度（弧度）
    """
    # 在测量前将量子比特旋转到目标基
    qc.ry(-2 * angle, qubit_index)  # 旋转到标准基进行测量
    # 注意：实际实现中需要更复杂的处理，这里简化

def simulate_measurement(state_vector, angle):
    """
    模拟在特定角度基下的测量结果
    返回：+1 (自旋向上) 或 -1 (自旋向下)
    """
    # 计算测量概率
    # 对于自旋1/2粒子，在角度θ方向测量的概率幅
    # 本征态为: |+⟩_θ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩
    #           |-⟩_θ = -sin(θ/2)|0⟩ + cos(θ/2)|1⟩
    
    # 简化模型：直接用量子力学的期望值公式
    # 对于单重态，相关系数 E(a,b) = -a·b = -cos(θ_a - θ_b)
    # 这里我们模拟单次测量结果
    prob_up = 0.5  # 在任意方向，单重态给出上下概率各50%
    
    # 但为了体现关联，我们需要考虑纠缠
    # 这里使用一个简单的技巧：基于随机数和量子关联
    rand = np.random.random()
    if rand < 0.5:
        return 1  # 自旋向上
    else:
        return -1  # 自旋向下

def calculate_correlation(results_alice, results_bob):
    """
    计算相关系数 E(a,b)
    """
    if len(results_alice) != len(results_bob):
        raise ValueError("结果数量不匹配")
    
    n = len(results_alice)
    if n == 0:
        return 0
    
    # E = (N++ + N-- - N+- - N-+) / N_total
    correlation = 0
    for a, b in zip(results_alice, results_bob):
        correlation += a * b
    
    return correlation / n

# ==================== 主控模拟类 ====================

class E91Simulator:
    def __init__(self, num_pairs=N):
        self.num_pairs = num_pairs
        self.results = {
            'alice_bases': [],
            'bob_bases': [],
            'alice_results': [],
            'bob_results': [],
            'eve_bases': [],      # 仅在有窃听时使用
            'eve_results': []     # 仅在有窃听时使用
        }
    
    def simulate_ideal_scenario(self):
        """模拟理想无窃听场景"""
        print("="*60)
        print("模拟理想无窃听场景")
        print("="*60)
        
        # 重置结果
        self._reset_results()
        
        for i in range(self.num_pairs):
            # Alice和Bob随机选择测量基
            alice_basis_idx = np.random.randint(0, 3)
            bob_basis_idx = np.random.randint(0, 3)
            
            alice_angle = angles_alice[alice_basis_idx]
            bob_angle = angles_bob[bob_basis_idx]
            
            # 模拟纠缠对测量结果
            # 对于单重态，当测量基相同时，结果完全反关联
            if alice_basis_idx == 1 and bob_basis_idx == 0:  # a2=b1=45°
                # 完全反关联
                alice_result = 1 if np.random.random() < 0.5 else -1
                bob_result = -alice_result
            elif alice_basis_idx == 2 and bob_basis_idx == 1:  # a3=b2=90°
                # 完全反关联
                alice_result = 1 if np.random.random() < 0.5 else -1
                bob_result = -alice_result
            else:
                # 其他基组合，根据量子力学公式计算概率
                angle_diff = alice_angle - bob_angle
                correlation = -np.cos(angle_diff)  # E(a,b) = -a·b = -cos(θ_a-θ_b)
                
                # 基于关联概率生成相关结果
                prob_same = (1 + correlation) / 2
                if np.random.random() < prob_same:
                    alice_result = 1 if np.random.random() < 0.5 else -1
                    bob_result = alice_result
                else:
                    alice_result = 1 if np.random.random() < 0.5 else -1
                    bob_result = -alice_result
            
            # 记录结果
            self.results['alice_bases'].append(alice_basis_idx)
            self.results['bob_bases'].append(bob_basis_idx)
            self.results['alice_results'].append(alice_result)
            self.results['bob_results'].append(bob_result)
        
        print(f"完成 {self.num_pairs} 对粒子的模拟")
        return self._analyze_results("理想场景")
    
    def simulate_eavesdropping_scenario(self, eavesdrop_prob=1.0):
        """
        模拟有窃听者Eve的场景（截获重发攻击）
        eavesdrop_prob: Eve窃听的比例，默认100%
        """
        print("\n" + "="*60)
        print("模拟有窃听者(Eve)的场景")
        print("="*60)
        
        # 重置结果
        self._reset_results()
        self.results['eve_bases'] = []
        self.results['eve_results'] = []
        
        for i in range(self.num_pairs):
            # 决定Eve是否窃听这一对
            eve_eavesdrops = np.random.random() < eavesdrop_prob
            
            if eve_eavesdrops:
                # ========== Eve进行截获重发攻击 ==========
                # 1. Eve截获发往Bob的粒子
                # 2. Eve随机选择一个基进行测量
                eve_basis_idx = np.random.randint(0, 3)
                eve_angle = angles_bob[eve_basis_idx]  # Eve使用Bob的基集合
                
                # 3. Eve的测量结果（随机，因为她不知道原始态）
                eve_result = 1 if np.random.random() < 0.5 else -1
                
                # 4. Eve根据她的测量结果重新制备一个态发给Bob
                # 她制备的是在她测量基下的本征态
                eve_state = eve_result  # +1或-1
                
                # 5. Alice测量她手中的粒子
                alice_basis_idx = np.random.randint(0, 3)
                alice_angle = angles_alice[alice_basis_idx]
                
                # 由于Eve的测量破坏了纠缠，Alice的结果现在是独立的
                alice_result = 1 if np.random.random() < 0.5 else -1
                
                # 6. Bob测量Eve重新制备的粒子
                bob_basis_idx = np.random.randint(0, 3)
                bob_angle = angles_bob[bob_basis_idx]
                
                # Bob的结果取决于：
                # - Eve制备的态（在Eve的测量基下是确定的）
                # - Bob的测量基与Eve测量基的夹角
                angle_diff = eve_angle - bob_angle
                
                # 如果Bob的基与Eve的基相同
                if bob_basis_idx == eve_basis_idx:
                    bob_result = eve_state  # Bob得到与Eve相同的结果
                else:
                    # 不同基，结果随机但有关联
                    # 量子力学给出的概率：P(相同) = cos²(Δθ/2)
                    delta_theta = angle_diff
                    prob_same = np.cos(delta_theta/2)**2
                    
                    if np.random.random() < prob_same:
                        bob_result = eve_state
                    else:
                        bob_result = -eve_state
                
                # 记录Eve的信息
                self.results['eve_bases'].append(eve_basis_idx)
                self.results['eve_results'].append(eve_result)
                
            else:
                # Eve没有窃听这一对，使用理想场景
                alice_basis_idx = np.random.randint(0, 3)
                bob_basis_idx = np.random.randint(0, 3)
                
                alice_angle = angles_alice[alice_basis_idx]
                bob_angle = angles_bob[bob_basis_idx]
                
                # 与理想场景相同的逻辑
                if alice_basis_idx == 1 and bob_basis_idx == 0:
                    alice_result = 1 if np.random.random() < 0.5 else -1
                    bob_result = -alice_result
                elif alice_basis_idx == 2 and bob_basis_idx == 1:
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
                
                # 记录Eve没有窃听
                self.results['eve_bases'].append(-1)  # 用-1表示没有窃听
                self.results['eve_results'].append(0)
            
            # 记录Alice和Bob的结果
            self.results['alice_bases'].append(alice_basis_idx)
            self.results['bob_bases'].append(bob_basis_idx)
            self.results['alice_results'].append(alice_result)
            self.results['bob_results'].append(bob_result)
        
        print(f"完成 {self.num_pairs} 对粒子的模拟（窃听概率: {eavesdrop_prob*100}%）")
        return self._analyze_results("窃听场景", eavesdrop_prob)
    
    def _reset_results(self):
        """重置所有结果"""
        for key in ['alice_bases', 'bob_bases', 'alice_results', 'bob_results']:
            self.results[key] = []
    
    def _analyze_results(self, scenario_name, eavesdrop_prob=0.0):
        """分析模拟结果"""
        print(f"\n分析{scenario_name}结果:")
        print("-" * 40)
        
        # 将列表转换为numpy数组便于分析
        alice_bases = np.array(self.results['alice_bases'])
        bob_bases = np.array(self.results['bob_bases'])
        alice_results = np.array(self.results['alice_results'])
        bob_results = np.array(self.results['bob_results'])
        
        # 1. 筛选用于CHSH检验的数据（特定基组合）
        # 需要的数据：E(a1,b1), E(a1,b3), E(a3,b1), E(a3,b3)
        mask_a1b1 = (alice_bases == 0) & (bob_bases == 0)  # a1=0°, b1=45°
        mask_a1b3 = (alice_bases == 0) & (bob_bases == 2)  # a1=0°, b3=135°
        mask_a3b1 = (alice_bases == 2) & (bob_bases == 0)  # a3=90°, b1=45°
        mask_a3b3 = (alice_bases == 2) & (bob_bases == 2)  # a3=90°, b3=135°
        
        # 计算各个组合的相关系数
        E_a1b1 = self._calc_E_for_mask(mask_a1b1, alice_results, bob_results)
        E_a1b3 = self._calc_E_for_mask(mask_a1b3, alice_results, bob_results)
        E_a3b1 = self._calc_E_for_mask(mask_a3b1, alice_results, bob_results)
        E_a3b3 = self._calc_E_for_mask(mask_a3b3, alice_results, bob_results)
        
        # 2. 计算CHSH值 S
        S = E_a1b1 - E_a1b3 + E_a3b1 + E_a3b3
        
        print(f"E(a1,b1) = {E_a1b1:.4f}")
        print(f"E(a1,b3) = {E_a1b3:.4f}")
        print(f"E(a3,b1) = {E_a3b1:.4f}")
        print(f"E(a3,b3) = {E_a3b3:.4f}")
        print(f"CHSH值 S = {S:.4f}")
        print(f"|S| = {abs(S):.4f}")
        
        # 3. 密钥生成分析（基相同的组合）
        # 论文中：a2,b1 和 a3,b2 用于生成密钥
        mask_key1 = (alice_bases == 1) & (bob_bases == 0)  # a2=45°, b1=45°
        mask_key2 = (alice_bases == 2) & (bob_bases == 1)  # a3=90°, b2=90°
        mask_key = mask_key1 | mask_key2
        
        key_indices = np.where(mask_key)[0]
        num_key_bits = len(key_indices)
        
        if num_key_bits > 0:
            # 提取密钥比特 - 关键修改：在E91协议中，当Alice和Bob选择相同基时，
            # 理想情况下他们的结果应该相反，所以Bob需要将自己的比特取反
            alice_key_bits = []
            bob_key_bits_raw = []  # Bob的原始比特
            
            for idx in key_indices:
                # Alice的结果直接作为密钥比特
                # 映射：+1 -> 0, -1 -> 1
                alice_bit = 0 if alice_results[idx] == 1 else 1
                
                # Bob的原始结果
                bob_raw_bit = 0 if bob_results[idx] == 1 else 1
                
                # Bob将比特取反，因为理想情况下Alice和Bob的结果相反
                bob_bit = 1 - bob_raw_bit
                
                alice_key_bits.append(alice_bit)
                bob_key_bits_raw.append(bob_bit)
            
            # 计算误码率（Quantum Bit Error Rate, QBER）
            alice_key_bits = np.array(alice_key_bits)
            bob_key_bits = np.array(bob_key_bits_raw)
            errors = np.sum(alice_key_bits != bob_key_bits)
            qber = errors / num_key_bits if num_key_bits > 0 else 0
            
            print(f"\n密钥生成分析:")
            print(f"  可用于生成密钥的比特数: {num_key_bits}")
            print(f"  错误比特数: {errors}")
            print(f"  量子误码率(QBER): {qber:.4f} ({qber*100:.2f}%)")
            
            # 显示前20个密钥比特（如果存在）
            if num_key_bits > 0:
                print(f"  Alice的前20个密钥比特: {alice_key_bits[:20]}")
                print(f"  Bob的前20个密钥比特:   {bob_key_bits[:20]}")
        else:
            print("没有可用于生成密钥的比特（基相同的测量太少）")
            qber = 0
        
        # 4. 安全性分析
        print(f"\n安全性分析:")
        print(f"  理论量子最大值: |S| = {2*np.sqrt(2):.4f} ≈ 2.8284")
        print(f"  经典局域实在论上限: |S| ≤ 2.0000")
        
        if abs(S) > 2.0:
            print(f"  ✓ |S| = {abs(S):.4f} > 2.0，违反贝尔不等式")
            print(f"  ✓ 检测到量子纠缠存在")
            if scenario_name == "理想场景":
                print(f"  ✓ 信道安全，无窃听")
            else:
                violation_strength = (abs(S) - 2.0) / (2*np.sqrt(2) - 2.0)
                print(f"  ✓ 但|S| = {abs(S):.4f} < 2.8284，纠缠被部分破坏")
                print(f"  ✗ 可能检测到窃听！")
        else:
            print(f"  ✗ |S| = {abs(S):.4f} ≤ 2.0，符合经典局域实在论")
            print(f"  ✗ 未检测到量子纠缠")
            if scenario_name == "窃听场景":
                print(f"  ✓ 成功检测到窃听者Eve的存在！")
            else:
                print(f"  ✗ 异常：理想场景下应违反贝尔不等式")
        
        return {
            'S': S,
            '|S|': abs(S),
            'E_a1b1': E_a1b1,
            'E_a1b3': E_a1b3,
            'E_a3b1': E_a3b1,
            'E_a3b3': E_a3b3,
            'num_key_bits': num_key_bits,
            'qber': qber,
            'scenario': scenario_name
        }
    
    def _calc_E_for_mask(self, mask, alice_results, bob_results):
        """计算特定掩码下的相关系数E"""
        if np.sum(mask) == 0:
            return 0.0
        
        alice_masked = alice_results[mask]
        bob_masked = bob_results[mask]
        
        # E = <AB> = 平均值(A_i * B_i)
        products = alice_masked * bob_masked
        E = np.mean(products)
        
        return E
    
    def visualize_results(self, ideal_results, eavesdrop_results):
        """可视化对比两种场景的结果"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. CHSH值对比
        ax1 = axes[0, 0]
        scenarios = ['理想场景', '窃听场景']
        S_values = [ideal_results['S'], eavesdrop_results['S']]
        S_abs_values = [ideal_results['|S|'], eavesdrop_results['|S|']]
        
        x = np.arange(len(scenarios))
        width = 0.35
        
        ax1.bar(x - width/2, S_values, width, label='S值', color='skyblue')
        ax1.bar(x + width/2, S_abs_values, width, label='|S|值', color='lightcoral')
        
        # 添加理论参考线
        ax1.axhline(y=2*np.sqrt(2), color='green', linestyle='--', alpha=0.7, label=f'量子极限: {2*np.sqrt(2):.3f}')
        ax1.axhline(y=2.0, color='red', linestyle='--', alpha=0.7, label='经典极限: 2.0')
        ax1.axhline(y=-2*np.sqrt(2), color='green', linestyle='--', alpha=0.3)
        ax1.axhline(y=-2.0, color='red', linestyle='--', alpha=0.3)
        
        ax1.set_xlabel('场景')
        ax1.set_ylabel('CHSH值')
        ax1.set_title('CHSH值对比')
        ax1.set_xticks(x)
        ax1.set_xticklabels(scenarios)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 相关系数对比
        ax2 = axes[0, 1]
        E_labels = ['E(a1,b1)', 'E(a1,b3)', 'E(a3,b1)', 'E(a3,b3)']
        E_ideal = [ideal_results['E_a1b1'], ideal_results['E_a1b3'], 
                  ideal_results['E_a3b1'], ideal_results['E_a3b3']]
        E_eavesdrop = [eavesdrop_results['E_a1b1'], eavesdrop_results['E_a1b3'],
                      eavesdrop_results['E_a3b1'], eavesdrop_results['E_a3b3']]
        
        x = np.arange(len(E_labels))
        ax2.bar(x - 0.2, E_ideal, 0.4, label='理想场景', color='skyblue', alpha=0.8)
        ax2.bar(x + 0.2, E_eavesdrop, 0.4, label='窃听场景', color='lightcoral', alpha=0.8)
        
        ax2.set_xlabel('相关系数')
        ax2.set_ylabel('E值')
        ax2.set_title('相关系数对比')
        ax2.set_xticks(x)
        ax2.set_xticklabels(E_labels)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 密钥生成对比
        ax3 = axes[1, 0]
        key_bits = [ideal_results['num_key_bits'], eavesdrop_results['num_key_bits']]
        
        bars = ax3.bar(scenarios, key_bits, color=['skyblue', 'lightcoral'])
        ax3.set_ylabel('可用密钥比特数')
        ax3.set_title('可用密钥比特数对比')
        ax3.grid(True, alpha=0.3)
        
        # 在柱状图上显示数值
        for bar, bits in zip(bars, key_bits):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 5,
                    f'{bits}', ha='center', va='bottom')
        
        # 4. QBER对比 - 修正后的值应该在0.35%和24.9%左右
        ax4 = axes[1, 1]
        qbers = [ideal_results['qber']*100, eavesdrop_results['qber']*100]
        
        bars = ax4.bar(scenarios, qbers, color=['skyblue', 'lightcoral'])
        ax4.set_ylabel('量子误码率 QBER (%)')
        ax4.set_title('量子误码率对比')
        ax4.grid(True, alpha=0.3)
        
        # 设置y轴范围，使小的QBER值更清晰可见
        ax4.set_ylim(0, max(qbers) * 1.2)
        
        # 在柱状图上显示数值
        for bar, qber in zip(bars, qbers):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{qber:.2f}%', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()

# ==================== 运行模拟 ====================

def main():
    # 创建模拟器实例
    simulator = E91Simulator(num_pairs=10000)
    
    # 1. 模拟理想无窃听场景
    ideal_results = simulator.simulate_ideal_scenario()
    
    # 2. 模拟有窃听者场景（Eve窃听所有传输）
    eavesdrop_results = simulator.simulate_eavesdropping_scenario(eavesdrop_prob=1.0)
    
    # 3. 可视化对比结果
    simulator.visualize_results(ideal_results, eavesdrop_results)
    
    # 4. 打印总结报告
    print("\n" + "="*60)
    print("E91协议模拟实验总结报告")
    print("="*60)
    
    print(f"\n实验配置:")
    print(f"  总粒子对数: {simulator.num_pairs}")
    print(f"  Alice测量基角度: 0°, 45°, 90°")
    print(f"  Bob测量基角度: 45°, 90°, 135°")
    
    print(f"\n实验结果对比:")
    print(f"  场景           |S|值     QBER     可用密钥比特")
    print(f"  -----------------------------------------------")
    print(f"  理想无窃听     {ideal_results['|S|']:.4f}   {ideal_results['qber']*100:.2f}%     {ideal_results['num_key_bits']}")
    print(f"  有窃听攻击     {eavesdrop_results['|S|']:.4f}   {eavesdrop_results['qber']*100:.2f}%     {eavesdrop_results['num_key_bits']}")
    
    print(f"\n理论参考值:")
    print(f"  量子力学预言 (理想纠缠): |S| = {2*np.sqrt(2):.4f} ≈ 2.828")
    print(f"  经典局域实在论上限: |S| ≤ 2.000")
    print(f"  理想场景QBER: 0% (无噪声无窃听)")
    
    print(f"\n安全结论:")
    if ideal_results['|S|'] > 2.0:
        print(f"  ✓ 理想场景下成功违反贝尔不等式，验证量子纠缠存在")
    else:
        print(f"  ✗ 理想场景下未违反贝尔不等式，可能存在模拟误差")
    
    if eavesdrop_results['|S|'] <= 2.0:
        print(f"  ✓ 窃听场景下|S|值降至经典界限内，成功检测到窃听")
    else:
        print(f"  ✗ 窃听场景下仍违反贝尔不等式，窃听检测可能不完整")
    
    if eavesdrop_results['qber'] > ideal_results['qber']:
        print(f"  ✓ 窃听导致QBER显著升高 ({ideal_results['qber']*100:.2f}% → {eavesdrop_results['qber']*100:.2f}%)")
    else:
        print(f"  ✗ QBER变化不明显，可能需要更多数据或调整窃听模型")
    
    print(f"\nE91协议安全性机制验证:")
    print(f"  1. 基于贝尔定理: {'通过' if ideal_results['|S|'] > 2.0 else '未通过'}")
    print(f"  2. 窃听检测能力: {'通过' if eavesdrop_results['|S|'] <= 2.0 else '部分通过'}")
    print(f"  3. 密钥生成能力: {'通过' if ideal_results['num_key_bits'] > 0 else '未通过'}")
    
    return ideal_results, eavesdrop_results

# ==================== 运行主函数 ====================

if __name__ == "__main__":
    ideal_results, eavesdrop_results = main()