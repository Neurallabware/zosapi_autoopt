"""
ZOS-API 实战演练脚本 (最终修复版 V2)
加载库克三片式镜头，并应用一个完整的、健壮的“局部-全局-局部”优化流程。
"""
import os
import sys
import logging
import time

# --- 初始化设置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from zosapi_autoopt.zosapi_core import ZOSAPIManager
from zosapi_autoopt.merit_function import MeritFunctionEditor
from zosapi_autoopt.zosapi_lde import LensDesignManager

# ... (前面的导入和初始化代码保持不变)

def main():
    """主实战函数 (最终修复版)"""
    zos_manager = None
    try:
        # ... (步骤1, 2, 3 保持不变)
        logging.info("正在连接到 Zemax OpticStudio...")
        zos_manager = ZOSAPIManager()
        sample_file_path = os.path.join(zos_manager.get_samples_dir(), "Sequential", "Objectives", "Cooke 40 degree field.zos")
        logging.info(f"正在加载示例文件: {sample_file_path}")
        zos_manager.open_file(sample_file_path)
        logging.info("正在设置优化变量...")
        lde_manager = LensDesignManager(zos_manager)
        lde_manager.clear_all_variables()
        for surf_index in [1, 2, 3, 5]:
            lde_manager.set_variable(surf_index, 'radius')
        for surf_index in [1, 3, 5]:
            lde_manager.set_variable(surf_index, 'thickness')
        logging.info("变量设置完成。")
        logging.info("正在构建评价函数...")
        mf_editor = MeritFunctionEditor(zos_manager)
        mf_editor.use_optimization_wizard('rms_spot', clear_existing=True, use_glass_constraints=False)
        logging.info("优化向导已成功生成评价函数。")
        op = mf_editor.Operands
        totr_operand = mf_editor.add_operand(op.TOTR)
        mf_editor.update()
        current_totr = totr_operand.Value 
        mf_editor.edit_operand(
            index=mf_editor.get_operand_count() - 1,
            target=current_totr,
            weight=1.0
        )
        logging.info(f"已手动添加TOTR操作数，目标总长: {current_totr:.4f} mm")
        
        # --- 步骤 4: 第一次局部优化 ---
        initial_merit = mf_editor.get_current_merit_value()
        logging.info(f"优化前，初始评价函数值为: {initial_merit:.6f}")
        local_opt_result_1 = mf_editor.run_local_optimization(timeout_seconds=60)
        
        if not local_opt_result_1.get('success'):
            raise RuntimeError(f"第一次局部优化失败: {local_opt_result_1.get('error')}")
        merit_after_local_1 = local_opt_result_1['final_merit']

        # --- 新增步骤 5: 全局优化 ---
        logging.info("开始运行全局优化...")
        hammer_opt_result = mf_editor.run_hammer_optimization(timeout_seconds=30)
        
        # **关键修复：在继续之前，先检查全局优化是否真的成功并找到了结果**
        if not hammer_opt_result.get('success'):
             logging.warning("全局优化执行失败，将直接保存第一次局部优化的结果。")
             zos_manager.save_file("./output/Cooke_Triplet_Local_Optimized_Only.zos")
             return

        if not hammer_opt_result.get('top_results'):
            logging.warning("全局优化未找到更优解，将继续对现有解进行精细打磨。")
        
        # --- 新增步骤 6: 第二次局部优化 ---
        logging.info("开始第二次局部优化...")
        time.sleep(1) # 增加短暂延时，确保API状态稳定
        final_opt_result = mf_editor.run_local_optimization(timeout_seconds=120)

        # --- 步骤 7: 最终报告结果 ---
        if final_opt_result.get('success'):
            final_merit = final_opt_result['final_merit']
            logging.info("="*50)
            logging.info("最终优化成功！流程总结：")
            logging.info(f"  - 初始评价值: {initial_merit:.6f} -> 最终评价值: {final_merit:.6f}")
            logging.info(f"  - 总改善量: {initial_merit - final_merit:.6f}")
            logging.info("="*50)
        else:
            logging.error(f"最终优化失败: {final_opt_result.get('error')}")

        # ... (保存和关闭的逻辑保持不变)
        # ... (save and close logic remains the same)
        output_dir = os.path.join(project_root, "output")
        os.makedirs(output_dir, exist_ok=True)
        optimized_file_path = os.path.join(output_dir, "Cooke_Triplet_Fully_Optimized.zos")
        zos_manager.save_file(optimized_file_path)
        logging.info(f"最终优化后的文件已保存至: {optimized_file_path}")

    except Exception as e:
        logging.error(f"实战演练中发生严重错误: {e}", exc_info=True)
    finally:
        if zos_manager:
            logging.info("正在断开与 Zemax 的连接...")
            zos_manager.close()
            
if __name__ == '__main__':
    main()