"""
测试镜头数据编辑器的变量设置功能
测试set_cell_as_variable和其他变量设置方法的功能
"""
import os
import sys
import time
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入必要的模块
from zosapi_autoopt.zosapi_core import ZOSAPIManager
from zosapi_autoopt.zosapi_lde import create_lens_design_manager

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_test():
    """运行测试用例"""
    logger.info("开始变量设置测试...")
    
    # 连接到Zemax
    logger.info("连接到Zemax OpticStudio...")
    zos_manager = ZOSAPIManager()
    if not zos_manager.connect():
        logger.error("无法连接到Zemax OpticStudio")
        return False
    
    logger.info("创建新系统...")
    zos_manager.new_file()
    
    # 创建镜头设计管理器
    logger.info("创建镜头设计管理器...")
    lde = create_lens_design_manager(zos_manager)
    
    # 测试创建一个简单的镜头系统
    logger.info("创建一个简单的双高斯镜头系统...")
    
    try:
        # 获取系统信息，检查已有的面数量
        system_info = lde.get_system_info()
        logger.info(f"当前系统已有 {system_info['surfaces']} 个面")
        
        # 检查初始光阑面位置
        initial_stop = -1
        for i in range(system_info['surfaces']):
            surface = lde.get_surface(i)
            if surface and hasattr(surface, 'IsStop') and surface.IsStop:
                initial_stop = i
                logger.info(f"初始光阑面位于位置: {initial_stop}")
                break
        
        if initial_stop == -1:
            logger.warning("未找到初始光阑面位置")
        
        # 修改物面厚度
        lde.set_thickness(0, 100.0)
        
        # 第一组元件 - 在已有的系统之间插入
        # 注意：默认系统有 0: OBJECT, 1: STOP, 2: IMAGE
        lde.insert_surface(1)  # 插入到光阑面位置，原光阑面变为2，像面变为3
        lde.set_radius(1, 20.0)
        lde.set_thickness(1, 5.0)
        lde.set_material(1, "N-BK7")
        
        lde.insert_surface(2)  # 插入到像面位置，原像面变为3
        lde.set_radius(2, -15.0)
        lde.set_thickness(2, 2.0)
        
        # 第二组元件
        lde.insert_surface(3)  # 插入到像面位置，原像面变为4
        lde.set_radius(3, 15.0)
        lde.set_thickness(3, 4.0)
        lde.set_material(3, "N-SF5")
        
        lde.insert_surface(4)  # 插入到像面位置，原像面变为5
        lde.set_radius(4, 100.0)
        lde.set_thickness(4, 10.0)
        
        # 光阑面 - 原先的光阑面被移到了位置2，我们可以设置一个新的光阑面
        lde.insert_surface(5)  # 插入到像面位置，原像面变为6
        lde.set_thickness(5, 10.0)
        logger.info("设置光阑面...")
        
        # 使用综合方法设置光阑面
        result = lde.set_stop_surface(5)
        logger.info(f"使用set_stop设置光阑面结果: {'成功' if result else '失败'}")
        
        # 验证光阑面是否已正确设置
        is_stop_set = False
        system_info = lde.get_system_info()
        
        if system_info['stop_surface'] != -1:
            logger.info(f"验证: 光阑面已设置在位置 {system_info['stop_surface']}")
            is_stop_set = (system_info['stop_surface'] == 5)
            if not is_stop_set:
                logger.warning(f"光阑面未设在期望位置5，而是在位置 {system_info['stop_surface']}")
        else:
            # 手动检查每个表面
            for i in range(1, lde.get_system_info()['surfaces'] + 1):
                surface = lde.get_surface(i)
                if surface and hasattr(surface, 'IsStop') and surface.IsStop:
                    logger.info(f"验证: 光阑面已设置在位置 {i}")
                    is_stop_set = (i == 5)
                    if not is_stop_set:
                        logger.warning(f"光阑面未设在期望位置5，而是在位置 {i}")
                    break
        
        if not is_stop_set:
            logger.warning("未能检测到任何光阑面设置")
        
        # 第三组元件
        lde.insert_surface(6)  # 插入到像面位置，原像面变为7
        lde.set_radius(6, 100.0)
        lde.set_thickness(6, 4.0)
        lde.set_material(6, "N-SF5")
        
        lde.insert_surface(7)  # 插入到像面位置，原像面变为8
        lde.set_radius(7, 15.0)
        lde.set_thickness(7, 2.0)
        
        # 第四组元件
        lde.insert_surface(8)  # 插入到像面位置，原像面变为9
        lde.set_radius(8, -15.0)
        lde.set_thickness(8, 5.0)
        lde.set_material(8, "N-BK7")
        
        lde.insert_surface(9)  # 插入到像面位置，原像面变为10
        lde.set_radius(9, -20.0)
        lde.set_thickness(9, 50.0)
        
        # 像面已经自动移到位置10
        
        logger.info("系统创建完成，开始测试变量设置功能...")
        
        
        # 测试2：使用set_variable设置变量
        logger.info("测试2：使用set_variable设置变量")
        result = lde.set_variable(3, 'radius')
        logger.info(f"使用set_variable设置变量结果: {'成功' if result else '失败'}")
        
        # 测试3：批量设置曲率半径为变量
        logger.info("测试3：批量设置曲率半径为变量")
        
        # 获取系统信息和当前光阑面位置
        current_surfaces = lde.get_system_info()['surfaces']
        stop_surface = lde.get_system_info()['stop_surface']
        
        if stop_surface != -1:
            logger.info(f"当前光阑面在位置: {stop_surface}")
            exclude_surfaces = [0, current_surfaces]  # 排除物面和像面
            if stop_surface > 0:
                exclude_surfaces.append(stop_surface)  # 排除光阑面
        else:
            logger.warning("未找到光阑面位置")
            exclude_surfaces = [0, current_surfaces]  # 只排除物面和像面
        
        result = lde.set_all_radii_as_variables(
            start_surface=1,  # 从第一个透镜面开始
            end_surface=current_surfaces-2,  # 到倒数第二个面结束
            exclude_surfaces=exclude_surfaces
        )
        logger.info(f"批量设置曲率半径变量结果: {'成功' if result else '失败'}")
        
        # 测试4：批量设置厚度为变量
        logger.info("测试4：批量设置厚度为变量")
        result = lde.set_all_thickness_as_variables(
            start_surface=1,  # 从第一个透镜面开始
            end_surface=current_surfaces-2,  # 到倒数第二个面结束
            exclude_surfaces=exclude_surfaces
        )
        logger.info(f"批量设置厚度变量结果: {'成功' if result else '失败'}")
        
        # 测试5：设置非球面并将参数设为变量
        logger.info("测试5：设置非球面并将参数设为变量")
        
        # 使用Even Aspheric表面类型，避免使用可能不存在的ZernikeSag
        try:
            # 选择一个合适的表面来设置非球面（例如第4个表面）
            aspheric_surface = 4
            lde.set_surface_type(aspheric_surface, 'aspheric')
            
            # 设置初始非球面系数
            lde.set_aspheric_coefficients(aspheric_surface, [1e-5, 1e-7, 1e-9, 1e-11])
            
            # 设置锥面系数为变量
            result = lde.set_variable(aspheric_surface, 'conic')
            logger.info(f"设置锥面系数变量结果: {'成功' if result else '失败'}")
            
            # 批量设置非球面系数为变量
            result = lde.set_all_aspheric_as_variables(
                start_surface=aspheric_surface, 
                end_surface=aspheric_surface,
                order=4  # 设置到8阶
            )
            logger.info(f"批量设置非球面系数变量结果: {'成功' if result else '失败'}")
        except Exception as e:
            logger.warning(f"非球面相关测试失败: {str(e)}")
            # 继续测试其他功能
        
        # 保存文件
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "output", "variable_test.zos")
        zos_manager.TheSystem.SaveAs(output_path)
        logger.info(f"文件已保存到: {output_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"测试过程中出现错误: {str(e)}")
        return False
    finally:
        # 释放COM对象
        try:
            zos_manager.close_file()
            zos_manager.close()
        except:
            pass

if __name__ == "__main__":
    success = run_test()
    print(f"测试结果: {'成功' if success else '失败'}")
