"""
Zemax OpticStudio Python API 使用示例
展示如何使用封装好的模块进行光学分析和优化
Author: Your Name
Date: 2025-06-29
"""

import os
import matplotlib.pyplot as plt
from zosapi_core import quick_connect
from zosapi_analysis import ZOSAnalyzer, BatchAnalyzer
from zosapi_plotting import ZOSPlotter
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_basic_analysis():
    """基础分析示例"""
    print("=" * 60)
    print("基础分析示例")
    print("=" * 60)
    
    # 方法1: 使用上下文管理器（推荐）
    with quick_connect() as zos:
        # 打开示例文件
        samples_dir = zos.get_samples_dir()
        test_file = os.path.join(samples_dir, "Sequential", "Objectives", "Double Gauss 28 degree field.zmx")
        
        if os.path.exists(test_file):
            zos.open_file(test_file)
            print(f"成功打开文件: {test_file}")
            
            # 获取系统信息
            system_info = zos.get_system_info()
            print(f"系统信息: {system_info}")
            
            # 创建分析器
            analyzer = ZOSAnalyzer(zos)
            
            # 分析点列图
            print("\n正在分析点列图...")
            spot_data = analyzer.analyze_spot_diagram(field_index=1)
            print(f"RMS 半径: {spot_data['rms_radius']:.6f} mm")
            print(f"光线数量: {spot_data['ray_count']}")
            
            # 分析 MTF
            print("\n正在分析 MTF...")
            mtf_data = analyzer.analyze_mtf(field_index=1)
            print(f"频率点数: {len(mtf_data['frequencies'])}")
            print(f"最大频率: {max(mtf_data['frequencies']):.2f} cycles/mm")
            
            zos.close_file(save=False)
        else:
            print(f"示例文件不存在: {test_file}")


def example_plotting():
    """绘图示例"""
    print("=" * 60)
    print("绘图示例")
    print("=" * 60)
    
    with quick_connect() as zos:
        # 打开示例文件
        samples_dir = zos.get_samples_dir()
        test_file = os.path.join(samples_dir, "Sequential", "Objectives", "Double Gauss 28 degree field.zmx")
        
        if os.path.exists(test_file):
            zos.open_file(test_file)
            
            # 创建分析器和绘图器
            analyzer = ZOSAnalyzer(zos)
            plotter = ZOSPlotter()
            
            # 分析和绘制点列图
            print("正在分析和绘制点列图...")
            spot_data = analyzer.analyze_spot_diagram(field_index=1)
            spot_fig = plotter.plot_spot_diagram(
                spot_data['x_coords'], 
                spot_data['y_coords'],
                title="点列图 - 视场1",
                save_path="spot_diagram.png"
            )
            
            # 分析和绘制 MTF
            print("正在分析和绘制 MTF...")
            mtf_data = analyzer.analyze_mtf(field_index=1)
            mtf_fig = plotter.plot_mtf_curve(
                mtf_data['frequencies'],
                mtf_data['mtf_sagittal'],
                title="MTF 曲线 - 弧矢方向",
                label="弧矢方向",
                save_path="mtf_curve.png"
            )
            
            # 分析和绘制波前
            print("正在分析和绘制波前...")
            try:
                wf_data = analyzer.analyze_wavefront(field_index=1, sampling=64)
                wf_fig = plotter.plot_wavefront(
                    wf_data['wavefront'],
                    wf_data['x_coords'],
                    wf_data['y_coords'],
                    mask=wf_data['mask'],
                    title="波前图 - 视场1",
                    save_path="wavefront.png"
                )
                print(f"波前 RMS: {wf_data['rms_wfe']:.6f} waves")
            except Exception as e:
                print(f"波前分析失败: {str(e)}")
            
            zos.close_file(save=False)
            print("图像已保存到当前目录")
        else:
            print(f"示例文件不存在: {test_file}")


def example_batch_analysis():
    """批量分析示例"""
    print("=" * 60)
    print("批量分析示例")
    print("=" * 60)
    
    with quick_connect() as zos:
        # 打开示例文件
        samples_dir = zos.get_samples_dir()
        test_file = os.path.join(samples_dir, "Sequential", "Objectives", "Double Gauss 28 degree field.zmx")
        
        if os.path.exists(test_file):
            zos.open_file(test_file)
            
            # 创建批量分析器
            batch_analyzer = BatchAnalyzer(zos)
            
            # 分析所有视场的点列图
            print("正在批量分析所有视场的点列图...")
            all_spots = batch_analyzer.analyze_all_fields_spots()
            
            print(f"分析了 {len(all_spots)} 个视场:")
            for i, spot in enumerate(all_spots):
                print(f"  视场 {i+1}: RMS 半径 = {spot['rms_radius']:.6f} mm")
            
            # 分析所有波长的 MTF
            print("\n正在批量分析所有波长的 MTF...")
            all_mtf = batch_analyzer.analyze_all_wavelengths_mtf()
            
            print(f"分析了 {len(all_mtf)} 个波长:")
            for i, mtf in enumerate(all_mtf):
                max_freq = max(mtf['frequencies'])
                print(f"  波长 {i+1}: 最大频率 = {max_freq:.2f} cycles/mm")
            
            zos.close_file(save=False)
        else:
            print(f"示例文件不存在: {test_file}")


def example_optimization():
    """优化示例"""
    print("=" * 60)
    print("优化示例")
    print("=" * 60)
    
    with quick_connect() as zos:
        # 打开示例文件
        samples_dir = zos.get_samples_dir()
        test_file = os.path.join(samples_dir, "Sequential", "Objectives", "Double Gauss 28 degree field.zmx")
        
        if os.path.exists(test_file):
            zos.open_file(test_file)
            
            # 创建分析器
            analyzer = ZOSAnalyzer(zos)
            
            # 优化前分析
            print("优化前分析...")
            initial_performance = analyzer.analyze_system_performance()
            
            if 'spot_diagrams' in initial_performance:
                initial_rms = initial_performance['spot_diagrams'][0]['rms_radius']
                print(f"初始 RMS 半径: {initial_rms:.6f} mm")
            
            # 快速聚焦
            print("执行快速聚焦...")
            focus_result = analyzer.quick_focus()
            print(f"快速聚焦结果: {focus_result}")
            
            # 系统优化
            print("执行系统优化...")
            try:
                opt_result = analyzer.optimize_system(max_iterations=50)
                print(f"优化结果: {opt_result}")
                
                if opt_result['success']:
                    improvement = opt_result['improvement'] * 100
                    print(f"优化改善: {improvement:.2f}%")
            except Exception as e:
                print(f"优化失败: {str(e)}")
            
            # 优化后分析
            print("优化后分析...")
            final_performance = analyzer.analyze_system_performance()
            
            if 'spot_diagrams' in final_performance:
                final_rms = final_performance['spot_diagrams'][0]['rms_radius']
                print(f"最终 RMS 半径: {final_rms:.6f} mm")
                
                if 'spot_diagrams' in initial_performance:
                    improvement = (initial_rms - final_rms) / initial_rms * 100
                    print(f"点列图改善: {improvement:.2f}%")
            
            zos.close_file(save=False)
        else:
            print(f"示例文件不存在: {test_file}")


def example_custom_analysis():
    """自定义分析示例"""
    print("=" * 60)
    print("自定义分析示例")
    print("=" * 60)
    
    with quick_connect() as zos:
        # 打开示例文件
        samples_dir = zos.get_samples_dir()
        test_file = os.path.join(samples_dir, "Sequential", "Objectives", "Double Gauss 28 degree field.zmx")
        
        if os.path.exists(test_file):
            zos.open_file(test_file)
            
            # 创建分析器和绘图器
            analyzer = ZOSAnalyzer(zos)
            plotter = ZOSPlotter()
            
            # 多视场点列图比较
            print("多视场点列图比较...")
            field_indices = [1, 2, 3]
            
            # 创建子图布局
            fig, axes = plotter.create_subplot_layout(1, 3, figsize=(15, 5))
            
            for i, field_idx in enumerate(field_indices):
                try:
                    spot_data = analyzer.analyze_spot_diagram(field_index=field_idx)
                    
                    # 在子图中绘制
                    ax = axes[i]
                    ax.scatter(spot_data['x_coords'], spot_data['y_coords'], 
                              alpha=0.6, s=1, c=plotter.colors['primary'])
                    
                    # 添加 RMS 圆
                    rms_radius = spot_data['rms_radius']
                    circle = plt.Circle((0, 0), rms_radius, fill=False, 
                                      color=plotter.colors['danger'], linestyle='--')
                    ax.add_patch(circle)
                    
                    ax.set_aspect('equal')
                    ax.grid(True, alpha=0.3)
                    ax.set_title(f'视场 {field_idx}')
                    ax.set_xlabel('X (mm)')
                    ax.set_ylabel('Y (mm)')
                    
                    # 添加统计信息
                    stats_text = f'RMS: {rms_radius:.6f} mm'
                    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                           verticalalignment='top', 
                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                    
                except Exception as e:
                    print(f"视场 {field_idx} 分析失败: {str(e)}")
            
            plt.tight_layout()
            plt.savefig("multi_field_spots.png", dpi=300, bbox_inches='tight')
            print("多视场点列图已保存为 multi_field_spots.png")
            
            # 多波长 MTF 比较
            print("多波长 MTF 比较...")
            try:
                batch_analyzer = BatchAnalyzer(zos)
                all_mtf = batch_analyzer.analyze_all_wavelengths_mtf(field_index=1)
                
                # 准备数据
                frequencies = all_mtf[0]['frequencies']
                mtf_curves = []
                labels = []
                
                for i, mtf_data in enumerate(all_mtf):
                    mtf_curves.append(mtf_data['mtf_sagittal'])
                    labels.append(f'波长 {i+1}')
                
                # 绘制多曲线图
                mtf_fig = plotter.plot_multiple_curves(
                    frequencies, mtf_curves, labels,
                    title="多波长 MTF 比较 (弧矢方向)",
                    xlabel="空间频率 (cycles/mm)",
                    ylabel="MTF",
                    save_path="multi_wavelength_mtf.png"
                )
                
                print("多波长 MTF 图已保存为 multi_wavelength_mtf.png")
                
            except Exception as e:
                print(f"多波长 MTF 分析失败: {str(e)}")
            
            zos.close_file(save=False)
        else:
            print(f"示例文件不存在: {test_file}")


def main():
    """主函数"""
    print("Zemax OpticStudio Python API 封装库使用示例")
    print("=" * 60)
    
    try:
        # 运行各个示例
        example_basic_analysis()
        example_plotting()
        example_batch_analysis()
        example_optimization()
        example_custom_analysis()
        
        print("\n" + "=" * 60)
        print("所有示例运行完成！")
        
    except Exception as e:
        logger.error(f"示例运行失败: {str(e)}")
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()
