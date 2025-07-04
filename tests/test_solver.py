import os
import sys
import logging

# --- 初始化与环境设置 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入核心管理器
from zosapi_autoopt.zosapi_core import ZOSAPIManager
from zosapi_autoopt.zosapi_lde import LensDesignManager
from zosapi_autoopt.zosapi_system import SystemParameterManager

def simple_solver_test():
    """一个极其简单的脚本，用于测试和演示求解器功能。"""
    zos_manager = None
    try:
        # 1. 连接到Zemax
        zos_manager = ZOSAPIManager()
        zos_manager.new_file()
        
        # 2. 初始化管理器
        lde_manager = LensDesignManager(zos_manager)
        sys_param_manager = SystemParameterManager(zos_manager) # 需要它来添加材料库

        # 3. 搭建一个最简单的结构：一个透镜
        lde_manager.insert_surface(1) # 镜片前表面
        lde_manager.insert_surface(2) # 镜片后表面
        
        # --- 4. 功能演示 ---

        # 演示1: 设置厚度拾取
        # 将表面1的厚度设置为5mm，然后让表面2的厚度拾取表面1的厚度并取其相反数
        logging.info("--- 演示1: 设置厚度拾取 (Pickup) ---")
        lde_manager.set_thickness(1, 5.0)
        lde_manager.set_pickup_solve(surface_pos=2, param_name='thickness', from_surface=1, scale=-1.0)
        
        # 演示2: 设置F数求解
        # 将表面2的曲率半径设置为 F/10
        logging.info("--- 演示2: 设置F数 (F-Number) 求解 ---")
        lde_manager.set_f_number_solve(surface_pos=2, f_number=10.0)
        
        # 演示3: 设置材料替代求解
        # 让Zemax在SCHOTT库中为表面1自动选择材料
        logging.info("--- 演示3: 设置材料替代 (Substitute) 求解 ---")
        sys_param_manager.add_catalog("SCHOTT") # 前提：确保SCHOTT库已加载
        lde_manager.set_substitute_solve(surface_pos=1, catalog="SCHOTT")

        # 5. 保存结果文件
        output_path = os.path.join(project_root, "output", "Simple_Solver_Test.zos")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        zos_manager.save_file(output_path)
        
        logging.info(f"--- 测试完成！---")
        logging.info(f"请在Zemax中打开文件查看求解器设置: {output_path}")

    except Exception as e:
        logging.error(f"测试脚本执行失败: {e}", exc_info=True)
    finally:
        if zos_manager and zos_manager.is_connected:
            zos_manager.close()

if __name__ == '__main__':
    simple_solver_test()