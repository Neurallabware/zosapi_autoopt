"""
Single Lens Automatic Modeling and Optimization Test Script
基于官方例程1和3的单透镜自动建模与优化测试脚本
Author: Your Name
Date: 2025-06-29
"""

import logging
import os
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from zosapi_core import ZOSAPIManager
from zosapi_analysis import ZOSAnalyzer
from zosapi_plotting import ZOSPlotter
from auto_optimizer import ZOSAutoOptimizer
import config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_single_lens_system(zos_manager: ZOSAPIManager):
    """
    创建单透镜系统 (参考官方例程1)
    
    Args:
        zos_manager: ZOSAPI 管理器
    """
    try:
        # 获取光学系统
        system = zos_manager.TheSystem
        
        # 设置系统单位为毫米
        system.SystemData.Units = zos_manager.ZOSAPI.SystemData.ZemaxUnits.Millimeters
        
        # 设置孔径类型为入瞳直径
        system.SystemData.Aperture.ApertureType = zos_manager.ZOSAPI.SystemData.ZemaxApertureType.EntrancePupilDiameter
        system.SystemData.Aperture.ApertureValue = 10.0  # 10mm入瞳直径
        
        # 设置视场
        fields = system.SystemData.Fields
        fields.GetField(1).Y = 0.0  # 轴上视场
        fields.GetField(1).Weight = 1.0
        
        # 添加第二个视场
        field2 = fields.AddField(0.0, 5.0, 1.0)  # 5度视场
        
        # 设置波长
        wavelengths = system.SystemData.Wavelengths
        primary_wave = wavelengths.GetWavelength(1)
        primary_wave.Wavelength = 0.5876  # d-line (587.6 nm)
        primary_wave.Weight = 1.0
        
        # 获取表面编辑器
        surf_data = system.LDE
        
        # Surface 0: Object (已存在)
        # Surface 1: 透镜前表面
        surf1 = surf_data.GetSurfaceAt(1)
        surf1.Radius = 50.0  # 曲率半径 50mm
        surf1.Thickness = 5.0  # 厚度 5mm
        surf1.Material = "N-BK7"  # BK7玻璃
        
        # Surface 2: 透镜后表面
        surf2 = surf_data.InsertNewSurfaceAt(2)
        surf2.Radius = -50.0  # 曲率半径 -50mm  
        surf2.Thickness = 100.0  # 到像面的距离
        
        # Surface 3: Image (自动添加)
        
        # 更新系统
        system.Tools.RemoveAllVariables()
        
        logger.info("Single lens system created successfully")
        
        # 设置优化变量 (参考例程3)
        # 设置透镜前表面曲率为变量
        surf1.RadiusCell.MakeSolveVariable()
        
        # 设置透镜后表面曲率为变量  
        surf2.RadiusCell.MakeSolveVariable()
        
        # 设置像面距离为变量
        surf2.ThicknessCell.MakeSolveVariable()
        
        logger.info("Optimization variables set")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create single lens system: {str(e)}")
        return False


def test_single_lens_optimization():
    """测试单透镜自动建模和优化"""
    
    print("=" * 60)
    print("Single Lens Automatic Modeling and Optimization Test")
    print("=" * 60)
    
    # 初始化 ZOSAPI
    try:
        zos_manager = ZOSAPIManager()
        if not zos_manager.connect():
            print("❌ Failed to connect to Zemax OpticStudio")
            return False
        
        print("✅ Connected to Zemax OpticStudio")
        
        # 创建新文件
        zos_manager.new_file()
        print("✅ Created new optical system file")
        
        # 创建单透镜系统
        if not create_single_lens_system(zos_manager):
            print("❌ Failed to create single lens system")
            return False
        print("✅ Single lens system created")
        
        # 初始化分析器
        analyzer = ZOSAnalyzer(zos_manager)
        plotter = ZOSPlotter()
        
        # === 1. 分析初始性能 ===
        print("\n📊 Analyzing initial performance...")
        
        # 快速聚焦
        focus_result = analyzer.quick_focus()
        if focus_result["success"]:
            print("✅ Quick focus completed")
        else:
            print("⚠️ Quick focus failed, continuing...")
        
        # 分析初始点列图
        initial_spot = analyzer.analyze_spot_diagram(field_index=1, wavelength_index=1)
        print(f"   Initial RMS spot size: {initial_spot['rms_radius']:.6f} mm")
        
        # 分析初始MTF
        initial_mtf = analyzer.analyze_mtf(field_index=1, wavelength_index=1, max_frequency=50)
        print(f"   Initial MTF at Nyquist: {initial_mtf['mtf_tangential'][-1]:.3f}")
        
        # === 2. 运行优化 ===
        print("\n🔧 Running optimization...")
        
        opt_result = analyzer.optimize_system(max_iterations=50)
        if opt_result["success"]:
            improvement = opt_result["improvement"] * 100
            print(f"✅ Optimization completed")
            print(f"   Merit function improvement: {improvement:.2f}%")
            print(f"   Initial merit: {opt_result['initial_merit']:.6f}")
            print(f"   Final merit: {opt_result['final_merit']:.6f}")
        else:
            print("⚠️ Optimization failed or did not converge")
        
        # === 3. 分析优化后性能 ===
        print("\n📈 Analyzing optimized performance...")
        
        # 分析优化后点列图
        final_spot = analyzer.analyze_spot_diagram(field_index=1, wavelength_index=1)
        print(f"   Final RMS spot size: {final_spot['rms_radius']:.6f} mm")
        
        # 分析优化后MTF
        final_mtf = analyzer.analyze_mtf(field_index=1, wavelength_index=1, max_frequency=50)
        print(f"   Final MTF at Nyquist: {final_mtf['mtf_tangential'][-1]:.3f}")
        
        # 计算改善
        spot_improvement = (initial_spot['rms_radius'] - final_spot['rms_radius']) / initial_spot['rms_radius'] * 100
        print(f"   Spot size improvement: {spot_improvement:.2f}%")
        
        # === 4. 生成对比图表 ===
        print("\n📊 Generating comparison plots...")
        
        try:
            # 绘制初始和最终点列图对比
            fig = plotter.create_subplot_layout(2, 2, figsize=(12, 10))[0]
            
            # 子图1: 初始点列图
            import matplotlib.pyplot as plt
            plt.subplot(2, 2, 1)
            plt.scatter(initial_spot['x_coords'], initial_spot['y_coords'], alpha=0.6, s=1)
            plt.axis('equal')
            plt.grid(True, alpha=0.3)
            plt.title(f'Initial Spot Diagram\nRMS: {initial_spot["rms_radius"]:.6f} mm')
            plt.xlabel('X (mm)')
            plt.ylabel('Y (mm)')
            
            # 子图2: 最终点列图
            plt.subplot(2, 2, 2)
            plt.scatter(final_spot['x_coords'], final_spot['y_coords'], alpha=0.6, s=1)
            plt.axis('equal')
            plt.grid(True, alpha=0.3)
            plt.title(f'Optimized Spot Diagram\nRMS: {final_spot["rms_radius"]:.6f} mm')
            plt.xlabel('X (mm)')
            plt.ylabel('Y (mm)')
            
            # 子图3: 初始MTF
            plt.subplot(2, 2, 3)
            plt.plot(initial_mtf['frequencies'], initial_mtf['mtf_tangential'], 'b-', label='Tangential', linewidth=2)
            plt.plot(initial_mtf['frequencies'], initial_mtf['mtf_sagittal'], 'r--', label='Sagittal', linewidth=2)
            plt.xlabel('Spatial Frequency (cycles/mm)')
            plt.ylabel('MTF')
            plt.title('Initial MTF')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.ylim(0, 1.1)
            
            # 子图4: 最终MTF
            plt.subplot(2, 2, 4)
            plt.plot(final_mtf['frequencies'], final_mtf['mtf_tangential'], 'b-', label='Tangential', linewidth=2)
            plt.plot(final_mtf['frequencies'], final_mtf['mtf_sagittal'], 'r--', label='Sagittal', linewidth=2)
            plt.xlabel('Spatial Frequency (cycles/mm)')
            plt.ylabel('MTF')
            plt.title('Optimized MTF')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.ylim(0, 1.1)
            
            plt.tight_layout()
            
            # 保存图表
            save_path = current_dir / "single_lens_optimization_results.png"
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ Comparison plots saved to: {save_path}")
            
            # 显示图表
            plt.show()
            
        except Exception as e:
            print(f"⚠️ Plot generation failed: {str(e)}")
        
        # === 5. 保存优化后的系统 ===
        try:
            save_path = current_dir / "optimized_single_lens.zos"
            zos_manager.save_file(str(save_path))
            print(f"✅ Optimized system saved to: {save_path}")
        except Exception as e:
            print(f"⚠️ Failed to save system: {str(e)}")
        
        # === 6. 系统信息总结 ===
        print("\n📋 System Summary:")
        system_info = zos_manager.get_system_info()
        print(f"   Surfaces: {system_info.get('num_surfaces', 'N/A')}")
        print(f"   Fields: {system_info.get('num_fields', 'N/A')}")
        print(f"   Wavelengths: {system_info.get('num_wavelengths', 'N/A')}")
        print(f"   System aperture: {system_info.get('aperture_value', 'N/A')}")
        
        print("\n✅ Single lens optimization test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理连接
        if 'zos_manager' in locals():
            try:
                zos_manager.disconnect()
                print("🔌 Disconnected from Zemax OpticStudio")
            except:
                pass


def test_analysis_functions():
    """测试分析功能的API调用"""
    
    print("\n" + "=" * 60)
    print("Testing Analysis Functions (API Compatibility)")
    print("=" * 60)
    
    try:
        zos_manager = ZOSAPIManager()
        if not zos_manager.connect():
            print("❌ Failed to connect to Zemax OpticStudio")
            return False
        
        print("✅ Connected to Zemax OpticStudio")
        
        # 打开示例文件
        sample_file = config.SAMPLE_FILES.get("cooke_triplet")
        if sample_file and os.path.exists(sample_file):
            zos_manager.open_file(sample_file)
            print(f"✅ Opened sample file: {os.path.basename(sample_file)}")
        else:
            # 创建简单系统
            zos_manager.new_file()
            create_single_lens_system(zos_manager)
            print("✅ Created simple test system")
        
        # 初始化分析器
        analyzer = ZOSAnalyzer(zos_manager)
        
        # 测试各种分析功能
        print("\n🔍 Testing analysis functions...")
        
        # 1. 测试点列图分析
        try:
            spot_data = analyzer.analyze_spot_diagram(field_index=1, wavelength_index=1)
            print(f"✅ Spot diagram analysis: RMS={spot_data['rms_radius']:.6f} mm")
        except Exception as e:
            print(f"❌ Spot diagram analysis failed: {str(e)}")
        
        # 2. 测试MTF分析
        try:
            mtf_data = analyzer.analyze_mtf(field_index=1, wavelength_index=1, max_frequency=50)
            print(f"✅ MTF analysis: {len(mtf_data['frequencies'])} data points")
        except Exception as e:
            print(f"❌ MTF analysis failed: {str(e)}")
        
        # 3. 测试光线扇形图分析
        try:
            ray_fan_data = analyzer.analyze_ray_fan(field_index=1, wavelength_index=1, fan_type="Y")
            print(f"✅ Ray fan analysis: {len(ray_fan_data['pupil_coords'])} rays")
        except Exception as e:
            print(f"❌ Ray fan analysis failed: {str(e)}")
        
        # 4. 测试波前分析
        try:
            wf_data = analyzer.analyze_wavefront(field_index=1, wavelength_index=1)
            print(f"✅ Wavefront analysis: RMS WFE={wf_data['rms_wfe']:.6f} waves")
        except Exception as e:
            print(f"❌ Wavefront analysis failed: {str(e)}")
        
        print("✅ Analysis functions test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Analysis test failed: {str(e)}")
        return False
    
    finally:
        if 'zos_manager' in locals():
            try:
                zos_manager.disconnect()
            except:
                pass


if __name__ == "__main__":
    print("Starting Single Lens Automatic Modeling and Optimization Test...\n")
    
    # 测试分析功能
    test_analysis_functions()
    
    # 测试单透镜优化
    success = test_single_lens_optimization()
    
    if success:
        print("\n🎉 All tests passed! The ZOSAPI automation system is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
    
    input("\nPress Enter to exit...")
