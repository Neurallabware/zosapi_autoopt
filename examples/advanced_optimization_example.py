"""
示例：高级优化策略示例

本示例展示了如何使用组合优化策略来改进光学系统设计:
1. 先使用全局优化找到好的起点
2. 使用锤形优化避免局部极小值
3. 最后使用局部优化精细调整
4. 在每个步骤分析和可视化系统性能改进
"""

import os
import sys
import time
import matplotlib.pyplot as plt

# 添加项目根目录到路径，以便导入项目模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from zosapi_autoopt import (
    ZOSAPIManager, 
    MeritFunctionEditor, 
    ZOSPlotter
)
from zosapi_autoopt.config import create_output_directory

def advanced_optimization_strategy():
    """使用组合优化策略改进光学系统"""
    
    # 确保输出目录存在
    create_output_directory()
    output_dir = os.path.join('output', 'advanced_optimization')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 初始化 ZOSAPI 管理器
    zos_manager = ZOSAPIManager()
    
    try:
        # 打开示例文件 (使用 Double Gauss 作为示例)
        sample_file = r".\sample_file\Objectives\Double Gauss 28 degree field.zos"

        print(f"打开示例文件: {sample_file}")
        zos_manager.open_file(sample_file)
        
        # 保存初始系统以供比较
        initial_file = os.path.join(output_dir, 'initial_system.zos')
        zos_manager.save_file(initial_file)
        print(f"初始系统已保存至: {initial_file}")
        
        # 创建评价函数编辑器实例
        print("创建评价函数编辑器...")
        mf_editor = MeritFunctionEditor(zos_manager)
        
        # 创建绘图器实例
        plotter = ZOSPlotter(zos_manager)
        
        # 获取初始系统状态
        print("初始系统状态:")
        initial_merit = mf_editor.get_current_merit_value()
        print(f"- 当前评价函数值: {initial_merit}")
        
        # 分析和绘制初始系统性能
        print("分析初始系统性能...")
        plotter.analyze_and_plot_system(title="初始系统性能")
        plt.savefig(os.path.join(output_dir, '1_initial_system_analysis.png'))
        plt.close()
        
        # 创建自定义评价函数
        print("\n创建自定义评价函数...")
        # 清空现有评价函数
        mf_editor.clear_merit_function()
        
        # 使用波前误差优化向导
        mf_editor.use_optimization_wizard(
            wizard_type='wavefront',
            weight=1.0,
            glass_min=2.0,
            glass_max=40.0,
            air_min=0.1,
            air_max=100.0
        )
        
        # 添加各种自定义操作数
        # 控制色差
        mf_editor.add_operand(
            operand_type='LACL',  # 横向色差
            target=0.0,
            weight=0.8,
            wave=1,
            field=1
        )
        
        # 控制像差
        mf_editor.add_operand(
            operand_type='COMA',  # 彗差
            target=0.0,
            weight=0.7,
            wave=1,
            field=1
        )
        
        # 控制系统长度
        mf_editor.add_operand(
            operand_type='TOTR',  # 总长度
            target=120.0,
            weight=0.1
        )
        
        # 控制F数
        mf_editor.add_operand(
            operand_type='ISFN',  # 镜头速度 (F数)
            target=2.8,
            weight=0.5
        )
        
        # 更新评价函数
        print(f"创建评价函数完成，当前评价函数值: {mf_editor.update_merit_function()}")
        print(f"操作数数量: {mf_editor.get_operand_count()}")
        
        # 保存包含新评价函数的系统
        merit_file = os.path.join(output_dir, 'system_with_merit_function.zos')
        zos_manager.save_file(merit_file)
        
        # 优化策略1: 全局优化
        print("\n===== 第1步: 全局优化 =====")
        print("开始全局优化，寻找好的起点...")
        # 设置较少的起点以加快示例运行速度
        global_result = mf_editor.run_global_optimization(
            start_points=5,  # 减少起点数量以加快演示
            timeout=300      # 5分钟超时
        )
        
        if global_result['success']:
            print("全局优化完成:")
            print(f"- 初始评价函数值: {global_result['initial_merit']}")
            print(f"- 最终评价函数值: {global_result['final_merit']}")
            print(f"- 最佳配置: {global_result['best_configuration']}")
            
            # 保存全局优化结果
            global_file = os.path.join(output_dir, '2_global_optimized.zos')
            zos_manager.save_file(global_file)
            print(f"全局优化结果已保存至: {global_file}")
            
            # 分析全局优化后的系统
            plotter.analyze_and_plot_system(title="全局优化后的系统性能")
            plt.savefig(os.path.join(output_dir, '2_global_optimized_analysis.png'))
            plt.close()
        else:
            print(f"全局优化失败: {global_result.get('error', '未知错误')}")
        
        # 优化策略2: 锤形优化
        print("\n===== 第2步: 锤形优化 =====")
        print("开始锤形优化，避免局部极小值...")
        hammer_result = mf_editor.run_hammer_optimization(
            cycles=3,    # 锤形优化循环次数
            timeout=300  # 5分钟超时
        )
        
        if hammer_result['success']:
            print("锤形优化完成:")
            print(f"- 初始评价函数值: {hammer_result['initial_merit']}")
            print(f"- 最终评价函数值: {hammer_result['final_merit']}")
            print(f"- 运行周期: {hammer_result['cycles_run']}")
            
            # 保存锤形优化结果
            hammer_file = os.path.join(output_dir, '3_hammer_optimized.zos')
            zos_manager.save_file(hammer_file)
            print(f"锤形优化结果已保存至: {hammer_file}")
            
            # 分析锤形优化后的系统
            plotter.analyze_and_plot_system(title="锤形优化后的系统性能")
            plt.savefig(os.path.join(output_dir, '3_hammer_optimized_analysis.png'))
            plt.close()
        else:
            print(f"锤形优化失败: {hammer_result.get('error', '未知错误')}")
        
        # 优化策略3: 局部优化（精细调整）
        print("\n===== 第3步: 局部优化（精细调整）=====")
        print("开始局部优化，精细调整系统...")
        local_result = mf_editor.run_local_optimization(
            algorithm='DampedLeastSquares',
            cycles=50,    # 较多的循环次数以精细优化
            timeout=300   # 5分钟超时
        )
        
        if local_result['success']:
            print("局部优化完成:")
            print(f"- 初始评价函数值: {local_result['initial_merit']}")
            print(f"- 最终评价函数值: {local_result['final_merit']}")
            print(f"- 变化: {local_result['change']}")
            print(f"- 迭代次数: {local_result['iterations']}")
            
            # 保存局部优化结果
            final_file = os.path.join(output_dir, '4_final_optimized.zos')
            zos_manager.save_file(final_file)
            print(f"最终优化结果已保存至: {final_file}")
            
            # 分析最终优化后的系统
            plotter.analyze_and_plot_system(title="最终优化后的系统性能")
            plt.savefig(os.path.join(output_dir, '4_final_optimized_analysis.png'))
            plt.close()
            
            # 绘制单独的性能图
            print("\n生成详细性能分析图...")
            # 光斑图
            plotter.plot_spots(show_airy_disk=True, title="最终系统光斑图")
            plt.savefig(os.path.join(output_dir, '5_final_spots.png'))
            plt.close()
            
            # MTF图
            plotter.plot_mtf(title="最终系统MTF")
            plt.savefig(os.path.join(output_dir, '5_final_mtf.png'))
            plt.close()
            
            # 光线扇图
            plotter.plot_rayfan(title="最终系统光线扇图")
            plt.savefig(os.path.join(output_dir, '5_final_rayfan.png'))
            plt.close()
            
        else:
            print(f"局部优化失败: {local_result.get('error', '未知错误')}")
        
        # 总结优化结果
        print("\n===== 优化总结 =====")
        print(f"初始评价函数值: {initial_merit}")
        final_merit = mf_editor.get_current_merit_value()
        print(f"最终评价函数值: {final_merit}")
        improvement = ((initial_merit - final_merit) / initial_merit) * 100
        print(f"改进百分比: {improvement:.2f}%")
        
        print("\n组合优化策略示例完成!")
        
    except Exception as e:
        print(f"错误: {str(e)}")
    
    finally:
        # 关闭连接
        zos_manager.close()

if __name__ == "__main__":
    advanced_optimization_strategy()
