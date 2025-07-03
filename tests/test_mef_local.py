"""
ZOS-API 实战演练脚本 (最终修复版)
加载库克三片式镜头，建立评价函数，并进行局部优化。
"""
import os
import sys
import logging

# --- 初始化设置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from zosapi_autoopt.zosapi_core import ZOSAPIManager
from zosapi_autoopt.merit_function import MeritFunctionEditor
from zosapi_autoopt.zosapi_lde import LensDesignManager

def main():
    """主实战函数"""
    zos_manager = None
    try:
        # --- 步骤 1: 连接到Zemax并加载文件 ---
        logging.info("正在连接到 Zemax OpticStudio...")
        zos_manager = ZOSAPIManager()
        sample_file_path = os.path.join(zos_manager.get_samples_dir(), "Sequential", "Objectives", "Cooke 40 degree field.zos")
        logging.info(f"正在加载示例文件: {sample_file_path}")
        zos_manager.open_file(sample_file_path)
        
        # --- 步骤 2: 将关键参数设置为变量 ---
        logging.info("正在设置优化变量...")
        lde_manager = LensDesignManager(zos_manager)
        lde_manager.clear_all_variables()  # 清除现有变量设置
        for surf_index in [1, 2, 4, 5]:
            lde_manager.set_variable(surf_index, 'radius')
        for surf_index in [1, 3, 5]:
            lde_manager.set_variable(surf_index, 'thickness')
        logging.info("变量设置完成。")

        # --- 步骤 3: 建立评价函数 ---
        logging.info("正在构建评价函数...")
        mf_editor = MeritFunctionEditor(zos_manager)
        mf_editor.use_optimization_wizard('rms_spot', clear_existing=True,use_glass_constraints=False)
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

        # --- 步骤 4: 运行优化 ---
        initial_merit = mf_editor.get_current_merit_value()
        logging.info(f"优化前，初始评价函数值为: {initial_merit:.6f}")
        
        logging.info("开始运行局部优化...")
        # **关键修复**: 移除了 cycles=10 参数，使用方法默认的Automatic模式
        opt_result = mf_editor.run_local_optimization(timeout_seconds=120)
        
        # --- 步骤 5: 报告结果 ---
        if opt_result.get('success'):
            final_merit = opt_result['final_merit']
            logging.info("优化成功！")
            logging.info(f"优化后，最终评价函数值为: {final_merit:.6f}")
            logging.info(f"评价函数值改善了: {initial_merit - final_merit:.6f}")
        else:
            logging.error(f"优化失败: {opt_result.get('error')}")

        # --- 步骤 6: 保存优化后的文件 ---
        output_dir = os.path.join(project_root, "output")
        os.makedirs(output_dir, exist_ok=True)
        optimized_file_path = os.path.join(output_dir, "Cooke_Triplet_Optimized_Final.zos")
        zos_manager.save_file(optimized_file_path)
        logging.info(f"优化后的文件已保存至: {optimized_file_path}")

    except Exception as e:
        logging.error(f"实战演练中发生严重错误: {e}", exc_info=True)
    finally:
        # --- 步骤 7: 清理资源 ---
        if zos_manager:
            logging.info("正在断开与 Zemax 的连接...")
            zos_manager.close()

if __name__ == '__main__':
    main()