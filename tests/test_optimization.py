"""
加载库克三片式镜头，并应用一个完整的、健壮的“局部-全局-锤形-局部”优化流程。
"""
import os
import sys
import logging
import time
import shutil

# --- 初始化设置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from zosapi_autoopt.zosapi_core import ZOSAPIManager
from zosapi_autoopt.merit_function import MeritFunctionEditor
from zosapi_autoopt.zosapi_lde import LensDesignManager

def main():

    # zos_manager = None
    #  创建一个唯一的、带时间戳的顶级输出目录 
    run_timestamp = time.strftime("%Y%m%d-%H%M%S")
    top_output_dir = os.path.join(project_root, "output", f"Cooke_Opt_{run_timestamp}")
    os.makedirs(top_output_dir, exist_ok=True)

    logging.info("正在连接到 Zemax OpticStudio...")
    zos_manager = ZOSAPIManager()
    
    # 将示例文件复制到我们本次运行的顶级输出目录中
    original_sample_path = os.path.join(zos_manager.get_samples_dir(), "Sequential", "Objectives", "Cooke 40 degree field.zos")
    working_file_path = os.path.join(top_output_dir, "Cooke_Start.zos")

    shutil.copy(original_sample_path, working_file_path)
    
    logging.info(f"正在加载工作文件: {working_file_path}")
    zos_manager.open_file(working_file_path)

    # 设置变量和评价函数 
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

    # 第一次局部优化 
    initial_merit = mf_editor.get_current_merit_value()
    logging.info(f"优化前，初始评价函数值为: {initial_merit:.6f}")
    local_opt_result_1 = mf_editor.run_local_optimization(timeout_seconds=60)
    if not local_opt_result_1.get('success'):
        raise RuntimeError(f"第一次局部优化失败: {local_opt_result_1.get('error')}")
    logging.info(f"第一次局部优化后评价值: {local_opt_result_1['final_merit']:.6f}")
    
    zos_manager.save_file(os.path.join(top_output_dir, "Cooke_After_Local_1.zos"))

    # 全局优化
    logging.info("="*20 + " 开始运行全局优化 " + "="*20)
    global_output_dir = os.path.join(top_output_dir, "global_optimization_results")
    
    global_opt_result = mf_editor.run_global_optimization(
        output_folder=global_output_dir,
        timeout_seconds=30,
        cores=20,
        save_top_n=10
    )
    #  锤形优化 
    logging.info("="*20 + " 开始运行锤形优化 " + "="*20)
    hammer_opt_result = mf_editor.run_hammer_optimization(timeout_seconds=30, cores=20)

    logging.info(f"锤形优化后评价值: {hammer_opt_result['final_merit']:.6f}")
    zos_manager.save_file(os.path.join(top_output_dir, "Cooke_After_Hammer.zos"))

    # 第二次局部优化 
    logging.info("="*20 + " 最终局部优化 " + "="*20)
    final_opt_result = mf_editor.run_local_optimization(timeout_seconds=120)

    # 最终结果 
    if final_opt_result.get('success'):
        final_merit = final_opt_result['final_merit']
        logging.info("="*50)
        logging.info("最终优化成功！流程总结：")
        logging.info(f"  - 初始评价值: {initial_merit:.6f} -> 最终评价值: {final_merit:.6f}")
        logging.info(f"  - 总改善量: {initial_merit - final_merit:.6f}")
        logging.info("="*50)

    # 保存最终文件
    optimized_file_path = os.path.join(top_output_dir, "Cooke_Triplet_FINA_Optimized.zos")
    zos_manager.save_file(optimized_file_path)
    logging.info(f"最终优化后的文件已保存至: {optimized_file_path}")

    if zos_manager:
        logging.info("正在断开与 Zemax 的连接...")
        zos_manager.close()

if __name__ == '__main__':
    main()