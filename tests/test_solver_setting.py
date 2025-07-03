"""
测试镜头数据编辑器的求解器设置功能
全面测试set_solver和set_pickup_solver方法的功能

测试内容包括:
1. 固定求解器设置 (fixed)
2. 拾取求解器设置 (pickup)
3. 边缘厚度求解器设置 (edge_thickness) - 已移除支持，仅测试兼容性接口
4. 主光线求解器设置 (chief_ray) - 已移除支持，测试不支持类型的处理
5. 边缘光线求解器设置 (marginal_ray) - 已移除支持，测试不支持类型的处理
6. 异常处理和边界情况
"""
import os
import sys
import time
import logging
from pathlib import Path

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 导入必要的模块
from zosapi_autoopt.zosapi_core import ZOSAPIManager
from zosapi_autoopt.zosapi_lde import create_lens_design_manager

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_test():
    """运行测试用例"""
    logger.info("开始求解器设置测试...")
    
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
    
    # 获取系统信息
    try:
        system_info = lde.get_system_info()
        logger.info(f"系统信息: {system_info}")
    except Exception as e:
        logger.warning(f"获取系统信息失败: {str(e)}")
    
    # 测试创建一个简单的双胶合透镜系统
    logger.info("创建一个简单的双胶合透镜系统...")
    
    try:
        # 修改物面厚度
        lde.set_thickness(0, 100.0)
        
        # 第一组元件
        lde.insert_surface(1)  # 插入第一个表面
        lde.set_radius(1, 50.0)
        lde.set_thickness(1, 5.0)
        lde.set_material(1, "N-BK7")
        
        lde.insert_surface(2)  # 插入第二个表面
        lde.set_radius(2, -30.0)
        lde.set_thickness(2, 2.0)
        lde.set_material(2, "N-SF5")
        
        lde.insert_surface(3)  # 插入第三个表面
        lde.set_radius(3, -100.0)
        lde.set_thickness(3, 50.0)
        
        # 设置光阑面
        lde.set_stop_surface(1)
        
        # 测试1：设置固定求解器
        logger.info("测试1：设置固定求解器")
        result = lde.set_solver(1, 'fixed', 'radius', target_value=45.0)
        logger.info(f"设置固定求解器结果: {'成功' if result else '失败'}")
        
        # 验证固定求解器设置
        surface = lde.get_surface(1)
        radius = surface.Radius
        logger.info(f"表面1的曲率半径: {radius}")
        if abs(radius - 45.0) < 0.001:
            logger.info("固定求解器设置成功！")
        else:
            logger.warning(f"固定求解器设置失败，期望值45.0，实际值{radius}")
        
        # 测试2：设置拾取求解器
        logger.info("测试2：设置拾取求解器")
        # 先设置参考表面的曲率半径
        lde.set_radius(3, -80.0)
        # 使用拾取求解器，从表面3拾取曲率半径到表面2，缩放因子为-0.5
        result = lde.set_pickup_solver(2, 'radius', reference_surface=3, scale_factor=-0.5)
        logger.info(f"设置拾取求解器结果: {'成功' if result else '失败'}")
        
        # 验证拾取求解器设置
        try:
            surface2 = lde.get_surface(2)
            cell = surface2.GetCellAt(lde.ZOSAPI.Editors.LDE.SurfaceColumn.Radius)
            solver_data = cell.GetSolveData()
            
            if solver_data and hasattr(solver_data, 'Type'):
                solver_type = solver_data.Type
                logger.info(f"表面2曲率半径求解器类型: {solver_type}")
                
                # 更新系统以确保值被正确计算
                try:
                    lde.update()
                    logger.info("已更新系统以应用求解器设置")
                except Exception as e:
                    logger.warning(f"更新系统失败: {str(e)}")
                
                # 通常拾取求解器类型为3，但可能因版本而异
                if solver_type == 3 or solver_type == lde.ZOSAPI.Editors.SolveType.SurfacePickup:
                    logger.info("拾取求解器设置成功！（类型验证）")
                else:
                    logger.warning(f"拾取求解器设置可能失败，求解器类型为{solver_type}")
                
                # 尝试验证参考表面和缩放因子
                reference_set = False
                scale_set = False
                
                # 检查求解器数据属性
                for attr_name in dir(solver_data):
                    if attr_name.startswith('_'):  # 跳过内部属性
                        continue
                    try:
                        if attr_name.lower() in ['pickupsurface', 'source', 'referencesurface', 'surface']:
                            value = getattr(solver_data, attr_name)
                            logger.info(f"找到参考表面属性 {attr_name}: {value}")
                            if value == 3:  # 我们期望参考表面是3
                                logger.info(f"拾取求解器参考表面设置正确: {value}（通过{attr_name}）")
                                reference_set = True
                        
                        if attr_name.lower() in ['scalefactor', 'scale', 'factor']:
                            value = getattr(solver_data, attr_name)
                            logger.info(f"找到缩放因子属性 {attr_name}: {value}")
                            if abs(value + 0.5) < 0.01:  # 我们期望缩放因子是-0.5
                                logger.info(f"拾取求解器缩放因子设置正确: {value}（通过{attr_name}）")
                                scale_set = True
                    except Exception as attr_error:
                        logger.debug(f"读取属性 {attr_name} 时出错: {str(attr_error)}")
                
                # 检查是否有 _S_SurfacePickup 属性
                if hasattr(solver_data, '_S_SurfacePickup'):
                    pickup_data = solver_data._S_SurfacePickup
                    logger.info("找到 _S_SurfacePickup 属性")
                    
                    # 检查参考表面
                    if hasattr(pickup_data, 'Surface'):
                        logger.info(f"_S_SurfacePickup.Surface: {pickup_data.Surface}")
                        if pickup_data.Surface == 3:
                            logger.info("拾取求解器参考表面设置正确 (通过 _S_SurfacePickup.Surface)")
                            reference_set = True
                    
                    # 检查缩放因子
                    if hasattr(pickup_data, 'ScaleFactor'):
                        logger.info(f"_S_SurfacePickup.ScaleFactor: {pickup_data.ScaleFactor}")
                        if abs(pickup_data.ScaleFactor + 0.5) < 0.01:
                            logger.info("拾取求解器缩放因子设置正确 (通过 _S_SurfacePickup.ScaleFactor)")
                            scale_set = True
                
                if not reference_set:
                    logger.warning("无法验证拾取求解器参考表面设置")
                
                if not scale_set:
                    logger.warning("无法验证拾取求解器缩放因子设置")
            else:
                logger.warning("无法获取求解器类型信息")
            
            # 尝试通过半径值验证（在某些版本可能需要更新系统）
            surface3 = lde.get_surface(3)
            radius2 = surface2.Radius
            radius3 = surface3.Radius
            expected_radius2 = -0.5 * radius3
            logger.info(f"表面2的曲率半径: {radius2}, 表面3的曲率半径: {radius3}")
            logger.info(f"期望的表面2曲率半径: {expected_radius2}")
            if abs(radius2 - expected_radius2) < 0.001:
                logger.info("拾取求解器设置成功！（值验证）")
            else:
                logger.warning(f"拾取求解器设置值验证失败，期望值{expected_radius2}，实际值{radius2}")
                logger.info("注意：某些求解器可能需要更新系统后才能看到效果")
        except Exception as e:
            logger.error(f"验证拾取求解器时出错: {str(e)}")
        
        # 测试3：尝试设置边缘厚度求解器（已不再支持）
        logger.info("测试3：尝试设置边缘厚度求解器（已不再支持）")
        # 设置表面1的厚度使用边缘厚度求解器，目标边缘厚度为2.0
        result = lde.set_edge_thickness_solver(1, target_thickness=2.0)
        logger.info(f"设置边缘厚度求解器结果: {'成功' if result else '失败（预期结果，因为此功能已不再支持）'}")
        
        # 验证边缘厚度求解器设置（应该失败）
        try:
            surface = lde.get_surface(1)
            cell = surface.GetCellAt(lde.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness)
            solver_data = cell.GetSolveData()
            
            if solver_data and hasattr(solver_data, 'Type'):
                solver_type = solver_data.Type
                logger.info(f"表面1厚度求解器类型: {solver_type}")
                logger.info("边缘厚度求解器已不再支持，预期此处显示的是默认求解器类型")
            else:
                logger.info("无法获取求解器类型信息，可能没有设置求解器")
        except Exception as e:
            logger.error(f"验证边缘厚度求解器时出错: {str(e)}")
        
        # 测试4：尝试设置主光线求解器（已不再支持）
        logger.info("测试4：尝试设置主光线求解器（已不再支持）")
        result = lde.set_solver(2, 'chief_ray', 'thickness', target_value=0.5)
        logger.info(f"设置主光线求解器结果: {'成功' if result else '失败（预期结果，因为此类型已不再支持）'}")
        
        # 验证主光线求解器设置（应该失败）
        try:
            surface = lde.get_surface(2)
            cell = surface.GetCellAt(lde.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness)
            solver_data = cell.GetSolveData()
            
            if solver_data and hasattr(solver_data, 'Type'):
                solver_type = solver_data.Type
                logger.info(f"表面2厚度求解器类型: {solver_type}")
                logger.info("主光线求解器已不再支持，预期显示默认求解器类型")
            else:
                logger.info("无法获取求解器类型信息，可能没有设置求解器")
        except Exception as e:
            logger.error(f"验证主光线求解器时出错: {str(e)}")
        
        # 测试5：尝试设置边缘光线求解器（已不再支持）
        logger.info("测试5：尝试设置边缘光线求解器（已不再支持）")
        result = lde.set_solver(3, 'marginal_ray', 'thickness', target_value=0.5)
        logger.info(f"设置边缘光线求解器结果: {'成功' if result else '失败（预期结果，因为此类型已不再支持）'}")
        
        # 验证边缘光线求解器设置（应该失败）
        try:
            surface = lde.get_surface(3)
            cell = surface.GetCellAt(lde.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness)
            solver_data = cell.GetSolveData()
            
            if solver_data and hasattr(solver_data, 'Type'):
                solver_type = solver_data.Type
                logger.info(f"表面3厚度求解器类型: {solver_type}")
                logger.info("边缘光线求解器已不再支持，预期显示默认求解器类型")
            else:
                logger.info("无法获取求解器类型信息，可能没有设置求解器")
        except Exception as e:
            logger.error(f"验证边缘光线求解器时出错: {str(e)}")
        
        # 测试6：异常情况处理
        logger.info("测试6：异常情况处理")
        # 测试不存在的表面
        try:
            result = lde.set_solver(100, 'fixed', 'radius', target_value=10.0)
            logger.info(f"设置不存在表面的求解器结果: {'成功' if result else '失败'}")
        except Exception as e:
            logger.info(f"设置不存在表面的求解器抛出异常: {str(e)}")
        
        # 测试不支持的参数名称
        try:
            result = lde.set_solver(1, 'fixed', 'not_exist_param', target_value=10.0)
            logger.info(f"设置不支持参数的求解器结果: {'成功' if result else '失败'}")
        except Exception as e:
            logger.info(f"设置不支持参数的求解器抛出异常: {str(e)}")
        
        # 测试不支持的求解器类型
        try:
            result = lde.set_solver(1, 'not_exist_solver', 'radius', target_value=10.0)
            logger.info(f"设置不支持求解器类型的结果: {'成功' if result else '失败'}")
        except Exception as e:
            logger.info(f"设置不支持求解器类型抛出异常: {str(e)}")
        
        # 保存文件
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "output", "solver_test.zos")
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
    start_time = time.time()
    success = run_test()
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"测试完成，耗时: {elapsed_time:.2f} 秒")
    print(f"测试结果: {'成功' if success else '失败'}")
