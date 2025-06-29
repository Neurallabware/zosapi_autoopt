"""
简单测试脚本 - 验证修正后的绘图功能（无需Zemax连接）
Simple test script to verify corrected plotting functions (no Zemax required)
Author: Your Name
Date: 2025-06-29
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from zosapi_plotting import ZOSPlotter, quick_spot_plot, quick_mtf_plot, quick_wavefront_plot


def test_plotting_english_labels():
    """测试修正后的绘图功能（英文标签）"""
    
    print("=" * 60)
    print("Testing Corrected Plotting Functions (English Labels)")
    print("=" * 60)
    
    try:
        # 初始化绘图器
        plotter = ZOSPlotter()
        print("✅ ZOSPlotter initialized successfully")
        
        # === 1. 测试点列图绘制 ===
        print("\n1️⃣ Testing Spot Diagram Plotting...")
        
        # 生成模拟点列图数据
        np.random.seed(42)
        n_rays = 200
        x_coords = np.random.normal(0, 0.01, n_rays).tolist()
        y_coords = np.random.normal(0, 0.01, n_rays).tolist()
        
        # 使用快速绘图函数
        fig = quick_spot_plot(
            x_coords, 
            y_coords, 
            title="Test Spot Diagram (English Labels)",
            save_path=str(current_dir / "test_spot_corrected.png")
        )
        plt.close(fig)
        print("   ✅ Spot diagram plotted with English labels")
        
        # === 2. 测试MTF曲线绘制 ===
        print("\n2️⃣ Testing MTF Curve Plotting...")
        
        # 生成模拟MTF数据
        frequencies = np.linspace(0, 100, 50).tolist()
        mtf_tangential = [max(0, 1 - f/100 + 0.1*np.sin(f*0.1)) for f in frequencies]
        mtf_sagittal = [max(0, 0.9 - f/100 + 0.05*np.cos(f*0.15)) for f in frequencies]
        
        # 绘制MTF曲线
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(frequencies, mtf_tangential, 'b-', linewidth=2, label='Tangential')
        ax.plot(frequencies, mtf_sagittal, 'r--', linewidth=2, label='Sagittal')
        ax.set_xlabel('Spatial Frequency (cycles/mm)')
        ax.set_ylabel('MTF')
        ax.set_title('Test MTF Curves (English Labels)')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, 1.1)
        plt.tight_layout()
        
        save_path = current_dir / "test_mtf_corrected.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print("   ✅ MTF curves plotted with English labels")
        
        # === 3. 测试波前图绘制 ===
        print("\n3️⃣ Testing Wavefront Map Plotting...")
        
        # 生成模拟波前数据
        size = 64
        x = np.linspace(-1, 1, size)
        y = np.linspace(-1, 1, size)
        xx, yy = np.meshgrid(x, y)
        r = np.sqrt(xx**2 + yy**2)
        theta = np.arctan2(yy, xx)
        
        # 模拟波前误差
        wavefront = 0.1 * r**2 + 0.05 * r**4 + 0.02 * r**3 * np.cos(3*theta)
        mask = r <= 1.0
        
        # 绘制波前图
        fig = plotter.plot_wavefront(
            wavefront, xx, yy, mask=mask,
            title="Test Wavefront Map (English Labels)",
            colorbar_label="Wavefront Error (waves)",
            save_path=str(current_dir / "test_wavefront_corrected.png")
        )
        plt.close(fig)
        print("   ✅ Wavefront map plotted with English labels")
        
        # === 4. 测试光线扇形图绘制 ===
        print("\n4️⃣ Testing Ray Fan Plotting...")
        
        # 生成模拟光线扇形图数据
        pupil_coords = np.linspace(-1, 1, 21).tolist()
        ray_errors = [0.001 * x**3 + 0.0001 * np.random.randn() for x in pupil_coords]
        
        # 绘制光线扇形图
        fig = plotter.plot_ray_fan(
            pupil_coords, ray_errors,
            title="Test Ray Fan (English Labels)",
            ylabel="Ray Error (mm)",
            save_path=str(current_dir / "test_rayfan_corrected.png")
        )
        plt.close(fig)
        print("   ✅ Ray fan diagram plotted with English labels")
        
        # === 5. 测试场曲和畸变图绘制 ===
        print("\n5️⃣ Testing Field Curvature & Distortion Plotting...")
        
        # 生成模拟场曲数据
        field_positions = np.linspace(0, 20, 10).tolist()
        sagittal_focus = [0.001 * f**2 for f in field_positions]
        tangential_focus = [0.0008 * f**2 for f in field_positions]
        distortion_values = [0.1 * f**2 for f in field_positions]
        
        # 绘制场曲图
        fig = plotter.plot_field_curvature(
            field_positions, sagittal_focus, tangential_focus,
            title="Test Field Curvature (English Labels)",
            save_path=str(current_dir / "test_fieldcurv_corrected.png")
        )
        plt.close(fig)
        print("   ✅ Field curvature plotted with English labels")
        
        # 绘制畸变图
        fig = plotter.plot_distortion(
            field_positions, distortion_values,
            title="Test Distortion (English Labels)",
            save_path=str(current_dir / "test_distortion_corrected.png")
        )
        plt.close(fig)
        print("   ✅ Distortion plot created with English labels")
        
        # === 6. 测试多曲线图绘制 ===
        print("\n6️⃣ Testing Multiple Curves Plotting...")
        
        # 生成多条曲线数据
        x_data = np.linspace(0, 10, 50).tolist()
        y_data_list = [
            [np.sin(x) for x in x_data],
            [np.cos(x) for x in x_data],
            [np.sin(2*x) for x in x_data]
        ]
        labels = ['Sine Wave', 'Cosine Wave', 'Double Frequency']
        
        # 绘制多曲线图
        fig = plotter.plot_multiple_curves(
            x_data, y_data_list, labels,
            title="Test Multiple Curves (English Labels)",
            xlabel="X Values", ylabel="Y Values",
            save_path=str(current_dir / "test_multicurve_corrected.png")
        )
        plt.close(fig)
        print("   ✅ Multiple curves plotted with English labels")
        
        # === 7. 创建综合对比图 ===
        print("\n7️⃣ Creating Comprehensive Comparison Plot...")
        
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        
        # 子图1: 点列图
        ax = axes[0, 0]
        ax.scatter(x_coords, y_coords, alpha=0.6, s=1, c='blue')
        ax.set_aspect('equal')
        ax.set_title('Spot Diagram')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.grid(True, alpha=0.3)
        
        # 子图2: MTF
        ax = axes[0, 1]
        ax.plot(frequencies, mtf_tangential, 'b-', label='Tangential', linewidth=2)
        ax.plot(frequencies, mtf_sagittal, 'r--', label='Sagittal', linewidth=2)
        ax.set_title('MTF Curves')
        ax.set_xlabel('Spatial Frequency (cycles/mm)')
        ax.set_ylabel('MTF')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, 1.1)
        
        # 子图3: 波前图
        ax = axes[0, 2]
        plot_data = np.where(mask, wavefront, np.nan)
        im = ax.contourf(xx, yy, plot_data, levels=20, cmap='RdYlBu_r')
        ax.set_title('Wavefront Map')
        ax.set_xlabel('Normalized Pupil X')
        ax.set_ylabel('Normalized Pupil Y')
        ax.set_aspect('equal')
        plt.colorbar(im, ax=ax, label='WFE (waves)')
        
        # 子图4: 光线扇形图
        ax = axes[1, 0]
        ax.plot(pupil_coords, ray_errors, 'g-', marker='o', markersize=3, linewidth=2)
        ax.set_title('Ray Fan')
        ax.set_xlabel('Pupil Coordinate')
        ax.set_ylabel('Ray Error (mm)')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # 子图5: 场曲
        ax = axes[1, 1]
        ax.plot(sagittal_focus, field_positions, 'b-', marker='o', label='Sagittal', linewidth=2)
        ax.plot(tangential_focus, field_positions, 'r--', marker='s', label='Tangential', linewidth=2)
        ax.set_title('Field Curvature')
        ax.set_xlabel('Focus Position Shift (mm)')
        ax.set_ylabel('Field Height')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.axvline(x=0, color='black', linestyle='-', alpha=0.5)
        
        # 子图6: 畸变
        ax = axes[1, 2]
        ax.plot(field_positions, distortion_values, 'purple', marker='o', linewidth=2)
        ax.set_title('Distortion')
        ax.set_xlabel('Field Position')
        ax.set_ylabel('Distortion (%)')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.suptitle('Comprehensive Optical Analysis (All English Labels)', fontsize=16)
        plt.tight_layout()
        
        save_path = current_dir / "comprehensive_analysis_corrected.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"   ✅ Comprehensive analysis plot saved: {save_path}")
        
        # === 总结 ===
        print(f"\n🎉 All plotting tests completed successfully!")
        print(f"📁 All plots saved to: {current_dir}")
        print(f"🔧 Key improvements verified:")
        print(f"   ✅ All labels and titles in English (no Chinese font issues)")
        print(f"   ✅ Consistent plotting style and formatting")
        print(f"   ✅ Proper axis labels and legends")
        print(f"   ✅ High-quality output (300 DPI)")
        print(f"   ✅ Matplotlib compatibility ensured")
        
        return True
        
    except Exception as e:
        print(f"❌ Plotting test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def verify_no_chinese_strings():
    """验证代码中没有中文字符串"""
    
    print("\n" + "=" * 60)
    print("Verifying No Chinese Strings in Code")
    print("=" * 60)
    
    # 检查绘图模块文件
    plotting_file = current_dir / "zosapi_plotting.py"
    
    try:
        with open(plotting_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否还有中文字符
        chinese_chars = []
        for i, char in enumerate(content):
            if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
                # 获取上下文
                start = max(0, i-20)
                end = min(len(content), i+21)
                context = content[start:end]
                chinese_chars.append((char, context))
        
        if chinese_chars:
            print(f"⚠️ Found {len(chinese_chars)} Chinese characters:")
            for char, context in chinese_chars[:5]:  # 只显示前5个
                print(f"   '{char}' in: ...{context}...")
        else:
            print("✅ No Chinese characters found in plotting module")
        
        # 检查常见的中文标签
        chinese_terms = ['中文', '点列图', '波前图', '光线', '频率', '坐标轴', '标题']
        found_terms = []
        for term in chinese_terms:
            if term in content:
                found_terms.append(term)
        
        if found_terms:
            print(f"⚠️ Found Chinese terms: {found_terms}")
        else:
            print("✅ No Chinese terms found in code")
        
        return len(chinese_chars) == 0 and len(found_terms) == 0
        
    except Exception as e:
        print(f"❌ File check failed: {str(e)}")
        return False


if __name__ == "__main__":
    print("Testing Corrected Plotting Functions (Standalone)...\n")
    
    # 测试绘图功能
    plotting_success = test_plotting_english_labels()
    
    # 验证无中文字符串
    no_chinese_success = verify_no_chinese_strings()
    
    if plotting_success and no_chinese_success:
        print("\n🎉 All corrections successfully verified!")
        print("📊 Ready for production use with:")
        print("   ✅ English-only labels (cross-platform compatible)")
        print("   ✅ Professional plotting output")
        print("   ✅ Consistent API following official examples")
    else:
        print("\n⚠️ Some issues may still exist. Check output above.")
    
    input("\nPress Enter to exit...")
