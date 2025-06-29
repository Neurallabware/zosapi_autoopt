"""
自动优化脚本示例
展示如何使用封装库进行自动光学系统优化
"""

import os
import logging
from zosapi_core import quick_connect
from zosapi_analysis import ZOSAnalyzer, BatchAnalyzer
from zosapi_plotting import ZOSPlotter
import matplotlib.pyplot as plt

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AutoOptimizer:
    """自动优化器类"""
    
    def __init__(self):
        self.zos = None
        self.analyzer = None
        self.plotter = None
        self.optimization_history = []
    
    def load_system(self, file_path: str):
        """加载光学系统"""
        try:
            self.zos = quick_connect()
            self.zos.open_file(file_path)
            self.analyzer = ZOSAnalyzer(self.zos)
            self.plotter = ZOSPlotter()
            
            print(f"✓ 成功加载系统: {file_path}")
            
            # 获取系统基本信息
            system_info = self.zos.get_system_info()
            print(f"系统标题: {system_info['title']}")
            print(f"面数: {system_info['surface_count']}")
            print(f"视场数: {system_info.get('field_count', 'N/A')}")
            print(f"波长数: {system_info['wavelength_count']}")
            
            return True
            
        except Exception as e:
            logger.error(f"加载系统失败: {str(e)}")
            return False
    
    def analyze_initial_performance(self):
        """分析初始性能"""
        print("\n" + "="*50)
        print("初始性能分析")
        print("="*50)
        
        try:
            # 分析点列图（多个视场）
            print("分析点列图...")
            spot_results = []
            for field_idx in range(1, 4):  # 分析前3个视场
                try:
                    spot_data = self.analyzer.analyze_spot_diagram(field_index=field_idx)
                    spot_results.append(spot_data)
                    print(f"  视场 {field_idx}: RMS = {spot_data['rms_radius']:.6f} mm")
                except:
                    break
            
            # 分析 MTF
            print("\n分析 MTF...")
            try:
                mtf_data = self.analyzer.analyze_mtf(field_index=1)
                mtf_at_50 = self._interpolate_mtf_at_frequency(mtf_data['frequencies'], 
                                                             mtf_data['mtf_sagittal'], 50)
                print(f"  50 cycles/mm 处的 MTF: {mtf_at_50:.3f}")
            except Exception as e:
                print(f"  MTF 分析失败: {str(e)}")
                mtf_data = None
            
            # 分析场曲和畸变
            print("\n分析场曲和畸变...")
            try:
                fc_data = self.analyzer.analyze_field_curvature_distortion()
                max_distortion = max([abs(d) for d in fc_data['distortion']])
                print(f"  最大畸变: {max_distortion:.3f}%")
            except Exception as e:
                print(f"  场曲畸变分析失败: {str(e)}")
                fc_data = None
            
            # 保存初始分析结果
            initial_performance = {
                'spot_diagrams': spot_results,
                'mtf': mtf_data,
                'field_curvature_distortion': fc_data
            }
            
            return initial_performance
            
        except Exception as e:
            logger.error(f"初始性能分析失败: {str(e)}")
            return None
    
    def _interpolate_mtf_at_frequency(self, frequencies, mtf_values, target_freq):
        """在指定频率处插值 MTF 值"""
        import numpy as np
        
        if target_freq <= min(frequencies):
            return mtf_values[0]
        elif target_freq >= max(frequencies):
            return mtf_values[-1]
        else:
            return np.interp(target_freq, frequencies, mtf_values)
    
    def run_optimization_cycle(self, max_iterations=100):
        """运行优化循环"""
        print("\n" + "="*50)
        print("执行优化")
        print("="*50)
        
        try:
            # 快速聚焦
            print("执行快速聚焦...")
            focus_result = self.analyzer.quick_focus()
            print(f"快速聚焦结果: {'成功' if focus_result['success'] else '失败'}")
            
            # 记录聚焦后的性能
            post_focus_spot = self.analyzer.analyze_spot_diagram(field_index=1)
            print(f"聚焦后 RMS 半径: {post_focus_spot['rms_radius']:.6f} mm")
            
            # 系统优化
            print(f"\n执行系统优化 (最大迭代次数: {max_iterations})...")
            opt_result = self.analyzer.optimize_system(max_iterations=max_iterations)
            
            if opt_result['success']:
                improvement = opt_result['improvement'] * 100
                print(f"✓ 优化成功!")
                print(f"  初始评价函数值: {opt_result['initial_merit']:.6f}")
                print(f"  最终评价函数值: {opt_result['final_merit']:.6f}")
                print(f"  改善程度: {improvement:.2f}%")
                print(f"  实际迭代次数: {opt_result['iterations']}")
            else:
                print("✗ 优化失败")
            
            return opt_result
            
        except Exception as e:
            logger.error(f"优化失败: {str(e)}")
            return None
    
    def analyze_final_performance(self):
        """分析最终性能"""
        print("\n" + "="*50)
        print("最终性能分析")
        print("="*50)
        
        try:
            # 重新分析点列图
            print("分析优化后点列图...")
            final_spot_results = []
            for field_idx in range(1, 4):
                try:
                    spot_data = self.analyzer.analyze_spot_diagram(field_index=field_idx)
                    final_spot_results.append(spot_data)
                    print(f"  视场 {field_idx}: RMS = {spot_data['rms_radius']:.6f} mm")
                except:
                    break
            
            # 重新分析 MTF
            print("\n分析优化后 MTF...")
            try:
                final_mtf_data = self.analyzer.analyze_mtf(field_index=1)
                final_mtf_at_50 = self._interpolate_mtf_at_frequency(final_mtf_data['frequencies'], 
                                                                   final_mtf_data['mtf_sagittal'], 50)
                print(f"  50 cycles/mm 处的 MTF: {final_mtf_at_50:.3f}")
            except Exception as e:
                print(f"  MTF 分析失败: {str(e)}")
                final_mtf_data = None
            
            return {
                'spot_diagrams': final_spot_results,
                'mtf': final_mtf_data
            }
            
        except Exception as e:
            logger.error(f"最终性能分析失败: {str(e)}")
            return None
    
    def generate_comparison_plots(self, initial_performance, final_performance):
        """生成对比图表"""
        print("\n" + "="*50)
        print("生成对比图表")
        print("="*50)
        
        try:
            # 创建对比图
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('优化前后性能对比', fontsize=16)
            
            # 1. 点列图对比 (视场1)
            if (initial_performance['spot_diagrams'] and 
                final_performance['spot_diagrams']):
                
                initial_spot = initial_performance['spot_diagrams'][0]
                final_spot = final_performance['spot_diagrams'][0]
                
                # 初始点列图
                ax1 = axes[0, 0]
                ax1.scatter(initial_spot['x_coords'], initial_spot['y_coords'], 
                           alpha=0.6, s=1, c='red', label='优化前')
                ax1.set_aspect('equal')
                ax1.grid(True, alpha=0.3)
                ax1.set_title('点列图对比 - 视场1')
                ax1.set_xlabel('X (mm)')
                ax1.set_ylabel('Y (mm)')
                ax1.legend()
                
                # 最终点列图 (叠加显示)
                ax1.scatter(final_spot['x_coords'], final_spot['y_coords'], 
                           alpha=0.6, s=1, c='blue', label='优化后')
                ax1.legend()
                
                # RMS 改善对比
                ax2 = axes[0, 1]
                fields = range(1, min(len(initial_performance['spot_diagrams']) + 1, 4))
                initial_rms = [initial_performance['spot_diagrams'][i-1]['rms_radius'] 
                              for i in fields]
                final_rms = [final_performance['spot_diagrams'][i-1]['rms_radius'] 
                            for i in fields]
                
                x = list(fields)
                ax2.plot(x, initial_rms, 'ro-', label='优化前', linewidth=2, markersize=6)
                ax2.plot(x, final_rms, 'bo-', label='优化后', linewidth=2, markersize=6)
                ax2.set_xlabel('视场')
                ax2.set_ylabel('RMS 半径 (mm)')
                ax2.set_title('RMS 半径对比')
                ax2.grid(True, alpha=0.3)
                ax2.legend()
            
            # 2. MTF 对比
            if (initial_performance['mtf'] and final_performance['mtf']):
                ax3 = axes[1, 0]
                
                initial_mtf = initial_performance['mtf']
                final_mtf = final_performance['mtf']
                
                ax3.plot(initial_mtf['frequencies'], initial_mtf['mtf_sagittal'], 
                        'r-', label='优化前', linewidth=2)
                ax3.plot(final_mtf['frequencies'], final_mtf['mtf_sagittal'], 
                        'b-', label='优化后', linewidth=2)
                
                ax3.set_xlabel('空间频率 (cycles/mm)')
                ax3.set_ylabel('MTF')
                ax3.set_title('MTF 对比 (弧矢方向)')
                ax3.grid(True, alpha=0.3)
                ax3.legend()
                ax3.set_ylim(0, 1.1)
            
            # 3. 改善统计
            ax4 = axes[1, 1]
            
            # 计算改善百分比
            if (initial_performance['spot_diagrams'] and 
                final_performance['spot_diagrams']):
                
                improvements = []
                labels = []
                
                for i in range(min(len(initial_performance['spot_diagrams']), 
                                 len(final_performance['spot_diagrams']))):
                    initial_rms = initial_performance['spot_diagrams'][i]['rms_radius']
                    final_rms = final_performance['spot_diagrams'][i]['rms_radius']
                    improvement = (initial_rms - final_rms) / initial_rms * 100
                    improvements.append(improvement)
                    labels.append(f'视场 {i+1}')
                
                colors = ['green' if x > 0 else 'red' for x in improvements]
                bars = ax4.bar(labels, improvements, color=colors, alpha=0.7)
                ax4.set_ylabel('改善百分比 (%)')
                ax4.set_title('RMS 半径改善情况')
                ax4.grid(True, alpha=0.3)
                ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
                
                # 添加数值标签
                for bar, value in zip(bars, improvements):
                    height = bar.get_height()
                    ax4.text(bar.get_x() + bar.get_width()/2., height + (1 if height > 0 else -1),
                            f'{value:.1f}%', ha='center', va='bottom' if height > 0 else 'top')
            
            plt.tight_layout()
            plt.savefig('optimization_comparison.png', dpi=300, bbox_inches='tight')
            print("✓ 对比图表已保存为 optimization_comparison.png")
            
            return fig
            
        except Exception as e:
            logger.error(f"生成对比图表失败: {str(e)}")
            return None
    
    def save_optimized_system(self, output_path: str):
        """保存优化后的系统"""
        try:
            self.zos.save_file(output_path)
            print(f"✓ 优化后系统已保存为: {output_path}")
            return True
        except Exception as e:
            logger.error(f"保存系统失败: {str(e)}")
            return False
    
    def cleanup(self):
        """清理资源"""
        if self.zos:
            self.zos.disconnect()
            print("✓ 连接已断开")
    
    def run_full_optimization(self, file_path: str, output_path: str = None, 
                             max_iterations: int = 100):
        """运行完整的优化流程"""
        print("开始自动优化流程...")
        print("="*60)
        
        try:
            # 1. 加载系统
            if not self.load_system(file_path):
                return False
            
            # 2. 分析初始性能
            initial_performance = self.analyze_initial_performance()
            if not initial_performance:
                return False
            
            # 3. 执行优化
            opt_result = self.run_optimization_cycle(max_iterations)
            if not opt_result:
                return False
            
            # 4. 分析最终性能
            final_performance = self.analyze_final_performance()
            if not final_performance:
                return False
            
            # 5. 生成对比图表
            self.generate_comparison_plots(initial_performance, final_performance)
            
            # 6. 保存优化后的系统
            if output_path:
                self.save_optimized_system(output_path)
            
            print("\n" + "="*60)
            print("🎉 自动优化流程完成!")
            print("="*60)
            
            return True
            
        except Exception as e:
            logger.error(f"优化流程失败: {str(e)}")
            return False
        
        finally:
            self.cleanup()


def main():
    """主函数"""
    print("Zemax OpticStudio 自动优化工具")
    print("="*60)
    
    # 创建优化器
    optimizer = AutoOptimizer()
    
    # 测试文件路径（使用官方样本）
    try:
        with quick_connect() as zos:
            samples_dir = zos.get_samples_dir()
            test_file = os.path.join(samples_dir, "Sequential", "Objectives", 
                                   "Double Gauss 28 degree field.zmx")
            
        if os.path.exists(test_file):
            print(f"使用测试文件: {test_file}")
            
            # 运行完整优化
            success = optimizer.run_full_optimization(
                file_path=test_file,
                output_path="optimized_system.zmx",
                max_iterations=50
            )
            
            if success:
                print("\n优化成功完成！")
                print("生成的文件:")
                print("- optimization_comparison.png (对比图表)")
                print("- optimized_system.zmx (优化后的系统)")
            else:
                print("\n优化过程中出现错误。")
        
        else:
            print(f"测试文件不存在: {test_file}")
            print("请确保 OpticStudio 样本文件可用。")
    
    except Exception as e:
        print(f"程序执行失败: {str(e)}")


if __name__ == "__main__":
    main()
