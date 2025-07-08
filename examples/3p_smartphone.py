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
from zosapi_autoopt import ZOSPlotter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


def add_thickness_constraints(mf_editor, lde_manager, 
                            glass_min=0.3, glass_max=2, 
                            air_min=0.05, air_max=2):
    """
    根据 Zemax 最佳实践，为所有表面添加厚度约束，确保可制造性。
    
    Parameters:
    - glass_min_center: 玻璃最小中心厚度 (mm)
    - glass_min_edge: 玻璃最小边缘厚度 (mm)  
    - air_max_center: 空气最大中心厚度 (mm)
    - air_min_edge: 空气最小边缘厚度 (mm)
    """
    Op = mf_editor.Operands
    surface_count = lde_manager.get_surface_count()
    
    logging.info(f"开始为 {surface_count} 个表面添加厚度约束...")
    
    for surface_num in range(1, surface_count):
        try:
            # 获取表面信息
            surface = lde_manager.get_surface(surface_num)
            material = surface.Material
            thickness = surface.Thickness
            
            # 判断是否为玻璃表面（有材料）
            is_glass = material and material.strip() and material.upper() not in ['', 'VACUUM', 'AIR']
            logging.info(f"表面 {surface_num}: 材料={material}, 厚度={thickness:.3f}, 类型={'玻璃' if is_glass else '空气'}")
            
            if is_glass:  
                # 添加FTGT约束（玻璃表面厚度强制约束）
                mf_editor.add_operand(
                    Op.FTGT,  # Force Thickness - Greater than
                    target=glass_min,
                    weight=1,  # 高权重确保玻璃厚度约束
                    params={2: surface_num}
                )
                logging.info(f"  - 添加FTGT约束 (玻璃最小厚度: {glass_min}mm)")
                mf_editor.add_operand(
                    Op.FTLT,  # Force Thickness - Less than
                    target=glass_max,
                    weight=1,  # 高权重确保玻璃厚度约束
                    params={2: surface_num}
                )
                logging.info(f"  - 添加FTGT约束 (玻璃最大厚度: {glass_max}mm)")                
                # TODO 添加曲率约束（防止过度弯曲）
            else:
                # 添加FTLT约束（表面间距强制约束）
                mf_editor.add_operand(
                    Op.FTGT,  # Force Thickness - less than
                    target=air_min,
                    weight=1,  # 高权重确保间距约束
                    params={2: surface_num}
                )
                logging.info(f"  - 添加FTGT约束 (最小间距: {air_min}mm)")
                mf_editor.add_operand(
                    Op.FTLT,  # Force Thickness - less than
                    target=air_max,
                    weight=1,  # 高权重确保间距约束
                    params={2: surface_num}
                )
                logging.info(f"  - 添加FTLT约束 (最大间距: {air_max}mm)")                    
        except Exception as e:
            logging.warning(f"为表面 {surface_num} 添加厚度约束时出错: {str(e)}")
            continue
    
    logging.info("厚度约束添加完成！")
    
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
    output_dir = os.path.join(project_root, "output", f"3p_smartphone_{run_timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    logging.info(f"所有设计文件将保存在: {output_dir}")
    # 新建一个空文件作为起点
    zos_manager.new_file()
    
    # 初始化各个功能管理器
    sys_param_manager = SystemParameterManager(zos_manager)
    lde_manager = LensDesignManager(zos_manager)
    mf_editor = MeritFunctionEditor(zos_manager)
    Op = mf_editor.Operands
    plotter = ZOSPlotter(zos_manager)
    
    # --- 步骤 1: 输入系统参数 ---
    logging.info("--- 步骤 1: 设置系统参数 ---")
    sys_param_manager.set_aperture('entrance_pupil_diameter', 1.168, clear_aperture_margin=0.1)
    sys_param_manager.set_field_type('angle')
    sys_param_manager.clear_fields()
    def set_fields_n_angles(sys_param_manager, N=7, max_angle=35):
        """
        设置N个不同的视场位置，最大视场角为max_angle（单位：度），均匀分布。
        """
        sys_param_manager.clear_fields()
        for i in range(N):
            angle = max_angle * i / (N - 1)
            sys_param_manager.add_field(x=0, y=angle, weight=1.0)
    set_fields_n_angles(sys_param_manager, N=7, max_angle=35)
    
    sys_param_manager.set_wavelength_preset('fdc_visible')
    sys_param_manager.add_catalog("PLASTIC")
    zos_manager.save_file(os.path.join(output_dir, "Step1_System_Parameters.zos"))
    
    # --- 步骤 2: 添加平板并设为变量 ---
    logging.info("--- 步骤 2: 搭建初始几何结构 ---")
    # aperture
    lde_manager.set_stop_surface(1)
    for _ in range(8): lde_manager.insert_surface(2)
    for i in range(1, 4): 
        lde_manager.set_material(int(2*i), "PMMA")
        lde_manager.set_substitute_solve(int(2*i), 'PLASTIC')
    lde_manager.set_material(8, "H-K9L")
    lde_manager.set_thickness(8,0.6)
    lde_manager.set_thickness(9,0.1)
    
    # radius
    for i in range(2, 8): lde_manager.set_variable(i, 'radius')
    
    # thicknes
    for i in range(1, 8): lde_manager.set_variable(i, 'thickness')

    zos_manager.save_file(os.path.join(output_dir, "Step2_Initial_Geometry.zos"))
    # --- 步骤 3: 构建评价函数 ---
    logging.info("--- 步骤 3: 构建评价函数 ---")
    
    mf_editor.use_optimization_wizard('rms_spot', rings=3, # ring number
                                      glass_min_center=0.3, # min glass center
                                      glass_min_edge=0.3, # min edge thickness
                                      air_max_center=0.05, # max air center
                                      air_min_edge=0.05)
    

    mf_editor.add_operand(Op.BLNK)
    # efl
    mf_editor.add_operand(Op.EFFL, target=3.27, weight=1, params={2: 2})
    # total track length
    mf_editor.add_operand(Op.TOTR, target=4.0, weight=1) 
    # CRA, using ray aiming
    mf_editor.add_operand(Op.RAID, target=32.0, weight=0, params={2: 10, 3: 2, 5: 1.0})
    # 
    mf_editor.add_operand(Op.DIMX, target=0.03, weight=0, params={2: 0, 3: 2, 4: 0})
    #
    mf_editor.add_operand(Op.OPLT, target=32.0, weight=1, params={2: 5})
    
    mf_editor.add_operand(Op.OPLT, target=32.0, weight=1, params={2: 2})
    
    # FTLT and FTGT operands to ensure proper surface spacing and thickness control
    logging.info("添加FTLT和FTGT操作数以确保表面间距和厚度控制...")
    
    # 添加详细的厚度约束（FTLT/FTGT）
    add_thickness_constraints(mf_editor, lde_manager, 
                            glass_min=0.3, glass_max=2, 
                            air_min=0.05, air_max=2)

    
    zos_manager.save_file(os.path.join(output_dir, "Step3_Merit_Function.zos"))
    
    # --- 步骤 4: 全局优化 ---
    logging.info("--- 步骤 4: 全局优化寻找初始结构 ---")
    global_opt_dir = os.path.join(output_dir, "Global_Opt")
    mf_editor.run_global_optimization(output_folder=global_opt_dir, timeout_seconds=60, cores=50)
    logging.info("  - 全局优化完成，已加载最优结果。")
    zos_manager.save_file(os.path.join(output_dir, "Step4_Global_Optimized.zos"))
    
    
    # --- 步骤 5: 非球面优化 ---
    logging.info("--- 步骤 5: 转换为非球面并进行优化 ---")
    aspheric_surfaces = [2, 3, 4, 5, 6, 7]
    for i in aspheric_surfaces:
        lde_manager.set_surface_type(i, 'evenaspheric')
        lde_manager.set_variable(i, 'conic')
    
    logging.info("  - 正在进行初步非球面优化...")
    mf_editor.run_local_optimization(timeout_seconds=300)
    logging.info("  - 正在逐个优化高阶非球面系数...")
    for i in aspheric_surfaces:
        lde_manager.set_aspheric_variables(surface_pos=i, orders=[4])
        mf_editor.run_local_optimization(timeout_seconds=300)
        
    for i in aspheric_surfaces:
        lde_manager.set_aspheric_variables(surface_pos=i, orders=[6])
        mf_editor.run_local_optimization(timeout_seconds=300)
        
    for i in aspheric_surfaces:
        lde_manager.set_aspheric_variables(surface_pos=i, orders=[8])
        mf_editor.run_local_optimization(timeout_seconds=300)
        
    for i in aspheric_surfaces:
        lde_manager.set_aspheric_variables(surface_pos=i, orders=[10])
        mf_editor.run_local_optimization(timeout_seconds=300)

    logging.info("  - 开始长时间锤形优化...")
    lde_manager.set_all_radii_as_variables(exclude_surfaces=[0, 1, 6])
    # lde_manager.set_all_thickness_as_variables(exclude_surfaces=[0, 1, 5, 6])
    # lde_manager.set_aspheric_variables(surface_pos=3, orders=[6])
    mf_editor.run_hammer_optimization(timeout_seconds=120, cores=50)
    zos_manager.save_file(os.path.join(output_dir, "Step5_Aspheric_Optimized.zos"))
    
    # --- 步骤 6: 细节优化 ---
    logging.info("--- 步骤 6: 精细优化 ---")
    
    
    
    logging.info("  - 正在进行最后的局部和锤形优化...")
    mf_editor.run_local_optimization(timeout_seconds=600)
    mf_editor.run_hammer_optimization(timeout_seconds=120)
    
    # --- 完成 ---
    final_file_path = os.path.join(output_dir, "Final_Lens_Design.zos")
    zos_manager.save_file(final_file_path)
    logging.info(f"--- 设计流程全部完成！最终文件已保存至: {final_file_path} ---")
    if zos_manager and zos_manager.is_connected:
        zos_manager.close()
        logging.info("已断开与 Zemax 的连接。")


    # --- 步骤 7: 生成分析报告和图表 ---
    logging.info("--- 步骤 7: 生成最终分析报告和图表 (PDF) ---")
    
    # 创建PDF文件来保存所有图表
    pdf_path = os.path.join(output_dir, "Final_Analysis_Report.pdf")
    
    with PdfPages(pdf_path) as pdf:
        logging.info("  - 生成光斑图...")
        try:
            plotter.plot_spots(show_airy_disk=True, title="最终系统光斑图")
            pdf.savefig(plt.gcf(), bbox_inches='tight', dpi=300)
            plt.close()
            logging.info("    ✓ 光斑图已保存")
        except Exception as e:
            logging.error(f"    ✗ 光斑图生成失败: {e}")
            plt.close()
        
        logging.info("  - 生成MTF图...")
        try:
            plotter.plot_mtf(title="最终系统MTF")
            pdf.savefig(plt.gcf(), bbox_inches='tight', dpi=300)
            plt.close()
            logging.info("    ✓ MTF图已保存")
        except Exception as e:
            logging.error(f"    ✗ MTF图生成失败: {e}")
            plt.close()
        
        logging.info("  - 生成光线扇图...")
        try:
            plotter.plot_rayfan(title="最终系统光线扇图")
            pdf.savefig(plt.gcf(), bbox_inches='tight', dpi=300)
            plt.close()
            logging.info("    ✓ 光线扇图已保存")
        except Exception as e:
            logging.error(f"    ✗ 光线扇图生成失败: {e}")
            plt.close()
        
        logging.info("  - 生成场曲与畸变图...")
        try:
            plotter.plot_field_curvature_distortion(title="最终系统场曲与畸变")
            pdf.savefig(plt.gcf(), bbox_inches='tight', dpi=300)
            plt.close()
            logging.info("    ✓ 场曲与畸变图已保存")
        except Exception as e:
            logging.error(f"    ✗ 场曲与畸变图生成失败: {e}")
            plt.close()
        
        logging.info("  - 生成综合分析图...")
        try:
            plotter.analyze_and_plot_system(title="最终系统综合分析")
            pdf.savefig(plt.gcf(), bbox_inches='tight', dpi=300)
            plt.close()
            logging.info("    ✓ 综合分析图已保存")
        except Exception as e:
            logging.error(f"    ✗ 综合分析图生成失败: {e}")
            plt.close()
    
    logging.info(f"  - 所有图表已保存至PDF文件: {pdf_path}")



if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(f"主程序运行出错: {str(e)}")
        logging.info("厚度约束功能已集成到主程序中")