import matplotlib.pyplot as plt
import numpy as np
import os  # 用于自动获取桌面路径

def get_desktop_path():
    """自动获取Windows桌面路径（无需手动修改用户名）"""
    if os.name == 'nt':  # Windows系统
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    else:  # macOS/Linux（兼容其他系统）
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    return desktop

def draw_e91_setup():
    # 1. 配置保存路径（直接保存到桌面）
    desktop_path = get_desktop_path()
    save_path = os.path.join(desktop_path, "e91_setup.png")
    
    # 2. 配置画布
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_aspect('equal')
    ax.axis('off')  # 隐藏坐标轴

    # 3. 绘制纠缠源（中间上方）
    source_x, source_y = 0, 5
    # 纠缠源矩形
    ax.add_patch(plt.Rectangle((source_x-1.5, source_y-0.5), 3, 1, 
                               facecolor='#E6F3FF', edgecolor='black', linewidth=2))
    # 纠缠源标签（单态表达式）
    ax.text(source_x, source_y, "Entangled Photon Source\n$|Ψ^-⟩ = \\frac{1}{\\sqrt{2}}(|01⟩ - |10⟩)$",
            ha='center', va='center', fontsize=11, fontweight='bold')

    # 4. 绘制光子传输路径（从纠缠源到Alice/Bob）
    # 到Alice的路径（左）
    ax.arrow(source_x, source_y-0.5, -4, -1, head_width=0.2, head_length=0.3, 
             fc='black', ec='black', linewidth=1.5)
    # 到Bob的路径（右）
    ax.arrow(source_x, source_y-0.5, 4, -1, head_width=0.2, head_length=0.3, 
             fc='black', ec='black', linewidth=1.5)

    # 5. 绘制Alice的测量模块（左侧）
    alice_x, alice_y = -5, 3
    # Alice模块大矩形
    ax.add_patch(plt.Rectangle((alice_x-1.5, alice_y-1.5), 3, 3, 
                               facecolor='#D6EAF8', edgecolor='black', linewidth=2))
    # Alice标签
    ax.text(alice_x, alice_y+1, "Alice's Measurement Bases", 
            ha='center', va='center', fontsize=10, fontweight='bold')
    # 三个基的角度标注
    ax.text(alice_x, alice_y+0.5, f"$a_1 = 0^\circ$", ha='center', fontsize=10)
    ax.text(alice_x, alice_y, f"$a_2 = 45^\circ$", ha='center', fontsize=10)
    ax.text(alice_x, alice_y-0.5, f"$a_3 = 90^\circ$", ha='center', fontsize=10)
    # Alice的探测器
    ax.add_patch(plt.Rectangle((alice_x-1, alice_y-2.5), 2, 0.8, 
                               facecolor='#FADBD8', edgecolor='black', linewidth=1.5))
    ax.text(alice_x, alice_y-2.1, "Detectors", ha='center', fontsize=9)

    # 6. 绘制Bob的测量模块（右侧）
    bob_x, bob_y = 5, 3
    # Bob模块大矩形
    ax.add_patch(plt.Rectangle((bob_x-1.5, bob_y-1.5), 3, 3, 
                               facecolor='#D6EAF8', edgecolor='black', linewidth=2))
    # Bob标签
    ax.text(bob_x, bob_y+1, "Bob's Measurement Bases", 
            ha='center', va='center', fontsize=10, fontweight='bold')
    # 三个基的角度标注
    ax.text(bob_x, bob_y+0.5, f"$b_1 = 45^\circ$", ha='center', fontsize=10)
    ax.text(bob_x, bob_y, f"$b_2 = 90^\circ$", ha='center', fontsize=10)
    ax.text(bob_x, bob_y-0.5, f"$b_3 = 135^\circ$", ha='center', fontsize=10)
    # Bob的探测器
    ax.add_patch(plt.Rectangle((bob_x-1, bob_y-2.5), 2, 0.8, 
                               facecolor='#FADBD8', edgecolor='black', linewidth=1.5))
    ax.text(bob_x, bob_y-2.1, "Detectors", ha='center', fontsize=9)

    # 7. 绘制E值和S值公式（左下角）
    formula_x, formula_y = -7, 0
    # E值公式
    ax.text(formula_x, formula_y, 
            r"$E(a_i, b_j) = P_{++}(a_i, b_j) + P_{--}(a_i, b_j)$" + "\n" +
            r"$\quad\quad\quad - P_{+-}(a_i, b_j) - P_{-+}(a_i, b_j)$",
            ha='left', fontsize=11)
    # S值公式
    ax.text(formula_x, formula_y-1, 
            r"$S = E(a_1, b_1) - E(a_1, b_3) + E(a_3, b_1) + E(a_3, b_3)$",
            ha='left', fontsize=11, fontweight='bold')

    # 8. 图标题（右上角）
    ax.text(7, 5.5, "Figure 2: E91 experimental setup", 
            ha='right', fontsize=12, fontweight='bold')

    # 9. 调整布局并保存到桌面
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ E91实验装置图已成功保存到桌面！")
    print(f"📁 保存路径：{save_path}")

# 运行绘图函数（直接执行即可）
if __name__ == "__main__":
    draw_e91_setup()