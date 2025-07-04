import os
import sys
import logging
import shutil
import time

# --- 初始化与环境设置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 从 zosapi_autoopt 库中导入所有需要的管理器
from zosapi_autoopt.zosapi_core import ZOSAPIManager
from zosapi_autoopt.zosapi_system import SystemParameterManager
from zosapi_autoopt.zosapi_lde import LensDesignManager
from zosapi_autoopt.merit_function import MeritFunctionEditor

def main():
    """
    一个精简的、线性的自动化镜头设计脚本。
    """
    zos_manager = None
    # --- 准备工作 ---
    zos_manager = ZOSAPIManager()
    if not zos_manager.is_connected:
        raise ConnectionError("未能连接到 Zemax OpticStudio，请先打开软件。")
    # 创建一个唯一的输出文件夹
    run_timestamp = time.strftime("%Y%m%d-%H%M%S")
    output_dir = os.path.join(project_root, "output", f"LensDesign_{run_timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"所有设计文件将保存在: {output_dir}")
    # 新建一个空文件作为起点
    zos_manager.new_file()
    
    # 初始化各个功能管理器
    sys_param_manager = SystemParameterManager(zos_manager)
    lde_manager = LensDesignManager(zos_manager)
    mf_editor = MeritFunctionEditor(zos_manager)
    Op = mf_editor.Operands
    # --- 步骤 1: 输入系统参数 ---
    logging.info("--- 步骤 1: 设置系统参数 ---")
    sys_param_manager.set_aperture('entrance_pupil_diameter', 1.168, clear_aperture_margin=0.1)
    sys_param_manager.set_field_type('angle')
    sys_param_manager.clear_fields()
    sys_param_manager.add_field(x=0, y=0, weight=1.0)
    sys_param_manager.add_field(x=0, y=24.5, weight=1.0) # 0.7 视场
    sys_param_manager.add_field(x=0, y=35, weight=1.0)   # 全视场
    sys_param_manager.set_wavelength_preset('fdc_visible')
    sys_param_manager.add_catalog("PLASTIC")
    zos_manager.save_file(os.path.join(output_dir, "Step1_System_Parameters.zos"))
    # --- 步骤 2: 添加平板并设为变量 ---
    logging.info("--- 步骤 2: 搭建初始几何结构 ---")
    lde_manager.set_stop_surface(1)
    for _ in range(8): lde_manager.insert_surface(2)
    for i in range(1, 4): 
        lde_manager.set_material(2*i, "PMMA")
        lde_manager.set_substitute_solve(2*i, 'PLASTIC')
    lde_manager.set_material(8, "H-K9L")
    lde_manager.set_thickness(8,0.6)
    lde_manager.set_thickness(9,0.1)
    for i in range(2, 8): lde_manager.set_variable(i, 'radius')
    for i in range(1, 8): lde_manager.set_variable(i, 'thickness')

    zos_manager.save_file(os.path.join(output_dir, "Step2_Initial_Geometry.zos"))
    # --- 步骤 3: 构建评价函数 ---
    logging.info("--- 步骤 3: 构建评价函数 ---")
    mf_editor.use_optimization_wizard('rms_spot', rings=3, glass_min_center=0.3, glass_min_edge=0.3, air_max_center=0.05, air_min_edge=0.05)
    mf_editor.add_operand(Op.EFFL, target=3.27, weight=1, params={2: 2})
    mf_editor.add_operand(Op.TOTR, target=4.0, weight=1)
    mf_editor.add_operand(Op.RAID, target=32.0, weight=0, params={1:10,2:2,3:0.0,4:1.0,5:0.0,6:0.0})
    mf_editor.add_operand(Op.DIMX, target=0.03, weight=0, params={1:0,2:2,3:0})
    mf_editor.add_operand(Op.OPLT, target=32.0, weight=1, params={1:5})
    mf_editor.add_operand(Op.OPLT, target=32.0, weight=1, params={1:2})
    zos_manager.save_file(os.path.join(output_dir, "Step3_Merit_Function.zos"))
    # --- 步骤 4: 全局优化 ---
    logging.info("--- 步骤 4: 全局优化寻找初始结构 ---")
    global_opt_dir = os.path.join(output_dir, "Global_Opt")
    mf_editor.run_global_optimization(output_folder=global_opt_dir, timeout_seconds=600, cores=20)
    logging.info("  - 全局优化完成，已加载最优结果。")
    zos_manager.save_file(os.path.join(output_dir, "Step4_Global_Optimized.zos"))
    # --- 步骤 5: 非球面优化 ---
    logging.info("--- 步骤 5: 转换为非球面并进行优化 ---")
    for i in [2, 3, 4]:
        lde_manager.set_surface_type(i, 'aspheric')
        lde_manager.set_variable(i, 'conic')
    logging.info("  - 正在进行初步非球面优化...")
    mf_editor.run_local_optimization(timeout_seconds=300)
    logging.info("  - 正在逐个优化高阶非球面系数...")
    for i in [2, 3, 4]:
        lde_manager.set_all_aspheric_as_variables(start_surface=i, end_surface=i, order=6)
        mf_editor.run_local_optimization(timeout_seconds=300)
    logging.info("  - 开始长时间锤形优化...")
    lde_manager.set_all_radii_as_variables(exclude_surfaces=[0, 1, 6])
    lde_manager.set_all_thickness_as_variables(exclude_surfaces=[0, 1, 5, 6])
    lde_manager.set_all_aspheric_as_variables(start_surface=2, end_surface=4, order=6)
    mf_editor.run_hammer_optimization(timeout_seconds=1800, cores=20)
    zos_manager.save_file(os.path.join(output_dir, "Step5_Aspheric_Optimized.zos"))
    # --- 步骤 6: 细节优化 ---
    logging.info("--- 步骤 6: 精细优化 ---")
    mf_editor.use_optimization_wizard('rms_spot', rings=6)
    logging.info("  - 正在进行最后的局部和锤形优化...")
    mf_editor.run_local_optimization(timeout_seconds=600)
    mf_editor.run_hammer_optimization(timeout_seconds=1200)
    
    # --- 完成 ---
    final_file_path = os.path.join(output_dir, "Final_Lens_Design.zos")
    zos_manager.save_file(final_file_path)
    logging.info(f"--- 设计流程全部完成！最终文件已保存至: {final_file_path} ---")
    if zos_manager and zos_manager.is_connected:
        zos_manager.close()
        logging.info("已断开与 Zemax 的连接。")

if __name__ == '__main__':
    main()