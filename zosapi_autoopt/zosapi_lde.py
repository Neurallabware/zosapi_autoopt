"""
Zemax OpticStudio 镜头数据编辑器(LDE)模块
提供光学系统镜头设计和编辑功能
Author: allin-love
Date: 2025-07-03
"""

import logging
from typing import List, Dict, Optional, Union, Any, Tuple
from .config import LOG_SETTINGS

# 配置日志
logger = logging.getLogger(__name__)


class LensDesignManager:
    """
    镜头设计管理器
    提供镜头数据编辑器(LDE)的功能封装
    """
    
    def __init__(self, zos_manager):
        """
        初始化镜头设计管理器
        
        Args:
            zos_manager: ZOSAPIManager 实例
        """
        self.zos_manager = zos_manager
        self.TheSystem = zos_manager.TheSystem
        self.ZOSAPI = zos_manager.ZOSAPI
        self.LDE = self.TheSystem.LDE
    
    # === 基本表面操作 ===
    
    def insert_surface(self, position: int) -> Any:
        """
        在指定位置插入新表面
        
        Args:
            position: 表面位置（从1开始）
            
        Returns:
            新插入的表面对象
        """
        try:
            surface = self.LDE.InsertNewSurfaceAt(position)
            logger.info(f"在位置 {position} 插入了新表面")
            return surface
        except Exception as e:
            logger.error(f"插入表面失败: {str(e)}")
            raise
    
    def delete_surface(self, position: int) -> bool:
        """
        删除指定位置的表面
        
        Args:
            position: 表面位置（从1开始）
            
        Returns:
            是否删除成功
        """
        try:
            result = self.LDE.DeleteSurfaceAt(position)
            logger.info(f"删除位置 {position} 的表面")
            return result
        except Exception as e:
            logger.error(f"删除表面失败: {str(e)}")
            raise
    
    def get_surface(self, position: int) -> Any:
        """
        获取指定位置的表面
        
        Args:
            position: 表面位置（从1开始）
            
        Returns:
            表面对象
        """
        try:
            surface = self.LDE.GetSurfaceAt(position)
            return surface
        except Exception as e:
            logger.error(f"获取表面失败: {str(e)}")
            raise
    
    def get_surface_count(self) -> int:
        """
        获取表面总数
        
        Returns:
            表面总数
        """
        try:
            count = self.LDE.NumberOfSurfaces
            return count
        except Exception as e:
            logger.error(f"获取表面总数失败: {str(e)}")
            raise
    
    def copy_surfaces(self, start_position: int, count: int, target_position: int) -> bool:
        """
        复制表面
        
        Args:
            start_position: 起始表面位置
            count: 要复制的表面数量
            target_position: 目标位置
            
        Returns:
            是否复制成功
        """
        try:
            result = self.LDE.CopySurfaces(start_position, count, target_position)
            logger.info(f"从位置 {start_position} 复制 {count} 个表面到位置 {target_position}")
            return result
        except Exception as e:
            logger.error(f"复制表面失败: {str(e)}")
            raise
    
    # === 表面参数设置 ===
    
    def set_radius(self, surface_pos: int, radius: float) -> bool:
        """
        设置表面曲率半径
        
        Args:
            surface_pos: 表面位置
            radius: 曲率半径
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            surface.Radius = radius
            logger.info(f"设置表面 {surface_pos} 的曲率半径为 {radius}")
            return True
        except Exception as e:
            logger.error(f"设置曲率半径失败: {str(e)}")
            raise
    
    def set_thickness(self, surface_pos: int, thickness: float) -> bool:
        """
        设置表面厚度
        
        Args:
            surface_pos: 表面位置
            thickness: 厚度
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            surface.Thickness = thickness
            logger.info(f"设置表面 {surface_pos} 的厚度为 {thickness}")
            return True
        except Exception as e:
            logger.error(f"设置厚度失败: {str(e)}")
            raise
    
    def set_material(self, surface_pos: int, material: str) -> bool:
        """
        设置表面材料
        
        Args:
            surface_pos: 表面位置
            material: 材料名称
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            surface.Material = material
            logger.info(f"设置表面 {surface_pos} 的材料为 {material}")
            return True
        except Exception as e:
            logger.error(f"设置材料失败: {str(e)}")
            raise
    
    def set_semi_diameter(self, surface_pos: int, semi_diameter: float) -> bool:
        """
        设置表面半口径
        
        Args:
            surface_pos: 表面位置
            semi_diameter: 半口径值
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            surface.SemiDiameter = semi_diameter
            logger.info(f"设置表面 {surface_pos} 的半口径为 {semi_diameter}")
            return True
        except Exception as e:
            logger.error(f"设置半口径失败: {str(e)}")
            raise
    
    # === 表面属性设置 ===
    
    def set_surface_type(self, surface_pos: int, surface_type: str) -> bool:
        """
        设置表面类型
        
        Args:
            surface_pos: 表面位置
            surface_type: 表面类型 (standard, conic, aspheric, toroidal 等)
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            
            # 映射表面类型 - 使用动态获取方式适应不同版本
            surface_type_mapping = {
                'standard': 'Standard',
                'conic': 'EvenAspheric',
                'aspheric': 'EvenAspheric',
                'toroidal': 'Toroidal',
                'coordinate_break': 'CoordinateBreak',
                'paraxial': 'Paraxial',
                'grid_sag': 'GridSag',
                'zernike': 'ZernikeSag'  # 某些版本可能没有此类型
            }
            
            if surface_type not in surface_type_mapping:
                raise ValueError(f"不支持的表面类型: {surface_type}")
            
            # 动态获取类型对象，如果不存在则抛出友好的错误
            try:
                type_name = surface_type_mapping[surface_type]
                type_value = getattr(self.ZOSAPI.Editors.LDE.SurfaceType, type_name)
            except AttributeError:
                # 尝试更通用的方式获取类型
                if surface_type == 'aspheric' or surface_type == 'conic':
                    # 几乎所有版本都支持EvenAspheric
                    type_value = getattr(self.ZOSAPI.Editors.LDE.SurfaceType, 'EvenAspheric')
                else:
                    raise ValueError(f"您的Zemax版本不支持表面类型: {type_name}")
            
            type_setting = surface.GetSurfaceTypeSettings(type_value)
            surface.ChangeType(type_setting)
            
            logger.info(f"设置表面 {surface_pos} 的类型为 {surface_type}")
            return True
        except Exception as e:
            logger.error(f"设置表面类型失败: {str(e)}")
            raise
    
    def set_conic(self, surface_pos: int, conic: float) -> bool:
        """
        设置表面锥面系数
        
        Args:
            surface_pos: 表面位置
            conic: 锥面系数
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            surface.Conic = conic
            logger.info(f"设置表面 {surface_pos} 的锥面系数为 {conic}")
            return True
        except Exception as e:
            logger.error(f"设置锥面系数失败: {str(e)}")
            raise
    
    def set_tilt_decenter(self, surface_pos: int, 
                         tilt_x: float = 0.0, 
                         tilt_y: float = 0.0, 
                         decenter_x: float = 0.0, 
                         decenter_y: float = 0.0,
                         tilt_before_decenter: bool = True) -> bool:
        """
        设置表面倾斜和偏心
        
        Args:
            surface_pos: 表面位置
            tilt_x: X轴倾斜角度
            tilt_y: Y轴倾斜角度
            decenter_x: X轴偏心量
            decenter_y: Y轴偏心量
            tilt_before_decenter: 是否先倾斜后偏心
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            tilt_data = surface.TiltDecenterData
            
            # 设置倾斜偏心顺序
            if tilt_before_decenter:
                tilt_data.BeforeSurfaceOrder = self.ZOSAPI.Editors.LDE.TiltDecenterOrderType.Tilt_Decenter
            else:
                tilt_data.BeforeSurfaceOrder = self.ZOSAPI.Editors.LDE.TiltDecenterOrderType.Decenter_Tilt
            
            # 设置倾斜偏心值
            tilt_data.BeforeSurfaceTiltX = tilt_x
            tilt_data.BeforeSurfaceTiltY = tilt_y
            tilt_data.BeforeSurfaceDecenterX = decenter_x
            tilt_data.BeforeSurfaceDecenterY = decenter_y
            
            logger.info(f"设置表面 {surface_pos} 的倾斜偏心参数")
            return True
        except Exception as e:
            logger.error(f"设置倾斜偏心参数失败: {str(e)}")
            raise
    
    def set_aperture(self, surface_pos: int, aperture_type: str, 
                    x_half_width: float = 0.0, 
                    y_half_width: float = 0.0) -> bool:
        """
        设置表面光阑
        
        Args:
            surface_pos: 表面位置
            aperture_type: 光阑类型 (circular, rectangular, float, none 等)
            x_half_width: X方向半宽度
            y_half_width: Y方向半宽度
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            
            # 特殊处理"none"类型，这可能是要设置为光阑面
            if aperture_type.lower() == "none":
                # 尝试直接设置IsStop属性（官方推荐方式）
                try:
                    # 先找到并清除当前光阑面
                    for i in range(1, self.get_system_info()['surfaces'] + 1):
                        try:
                            other_surface = self.get_surface(i)
                            if (other_surface and hasattr(other_surface, 'IsStop') and 
                                other_surface.IsStop and i != surface_pos):
                                other_surface.IsStop = False
                                logger.info(f"清除位置 {i} 的光阑面设置")
                        except:
                            pass
                    
                    # 设置新的光阑面
                    surface.IsStop = True
                    logger.info(f"使用IsStop=True设置表面 {surface_pos} 为光阑面")
                    
                    # 验证是否成功
                    if hasattr(surface, 'IsStop') and surface.IsStop:
                        return True
                except Exception as e:
                    logger.debug(f"使用IsStop设置光阑面失败: {str(e)}")
            
            # 正常的光阑类型处理
            aperture_data = surface.ApertureData
            
            # 映射光阑类型
            aperture_type_map = {
                'circular': self.ZOSAPI.Editors.LDE.SurfaceApertureTypes.CircularAperture,
                'rectangular': self.ZOSAPI.Editors.LDE.SurfaceApertureTypes.RectangularAperture,
                'float': self.ZOSAPI.Editors.LDE.SurfaceApertureTypes.FloatingAperture,
                'none': getattr(self.ZOSAPI.Editors.LDE.SurfaceApertureTypes, 'None')
            }
            
            if aperture_type.lower() not in aperture_type_map:
                raise ValueError(f"不支持的光阑类型: {aperture_type}")
            
            # 创建适当的光阑设置
            aperture_type_key = aperture_type.lower()
            aperture_setting = aperture_data.CreateApertureTypeSettings(aperture_type_map[aperture_type_key])
            
            # 设置光阑参数
            if aperture_type_key == 'circular':
                aperture_setting._S_CircularAperture.Radius = x_half_width
            elif aperture_type_key == 'rectangular':
                aperture_setting._S_RectangularAperture.XHalfWidth = x_half_width
                aperture_setting._S_RectangularAperture.YHalfWidth = y_half_width
            
            # 应用光阑设置
            aperture_data.ChangeApertureTypeSettings(aperture_setting)
            
            logger.info(f"设置表面 {surface_pos} 的光阑为 {aperture_type}")
            return True
            
        except Exception as e:
            logger.error(f"设置光阑失败: {str(e)}")
            raise
    
    def set_aspheric_coefficients(self, surface_pos: int, coefficients: List[float]) -> bool:
        """
        设置非球面系数
        
        Args:
            surface_pos: 表面位置
            coefficients: 非球面系数列表 [A4, A6, A8, ...]
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            
            # 检查表面类型是否为非球面 - 使用更可靠的方式
            is_aspheric = False
            try:
                # 方法1: 通过Cell获取类型
                type_cell = surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Type)
                if type_cell:
                    type_value = str(type_cell.Value).lower()
                    is_aspheric = ('aspheric' in type_value or 'even' in type_value)
            except:
                # 如果无法获取类型，假设可以设置非球面系数
                is_aspheric = True
            
            if not is_aspheric:
                logger.warning(f"表面 {surface_pos} 可能不是非球面类型，但仍将尝试设置非球面系数")
            
            # 设置非球面系数
            for i, coef in enumerate(coefficients):
                param_index = i + 1  # 参数索引从1开始
                surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Par1 + i).DoubleValue = coef
            
            logger.info(f"设置表面 {surface_pos} 的非球面系数")
            return True
        except Exception as e:
            logger.error(f"设置非球面系数失败: {str(e)}")
            raise
    
    # === 特殊操作 ===
    
    def convert_local_to_global(self, start_surface: int, end_surface: int, reference_surface: int) -> bool:
        """
        将表面从局部坐标转换为全局坐标
        
        Args:
            start_surface: 起始表面
            end_surface: 结束表面
            reference_surface: 参考表面
            
        Returns:
            是否转换成功
        """
        try:
            result = self.LDE.RunTool_ConvertLocalToGlobalCoordinates(start_surface, end_surface, reference_surface)
            logger.info(f"将表面 {start_surface} 到 {end_surface} 转换为全局坐标，参考表面: {reference_surface}")
            return result
        except Exception as e:
            logger.error(f"转换全局坐标失败: {str(e)}")
            raise
    
    def convert_global_to_local(self, start_surface: int, end_surface: int, 
                             order: str = 'forward') -> bool:
        """
        将表面从全局坐标转换为局部坐标
        
        Args:
            start_surface: 起始表面
            end_surface: 结束表面
            order: 转换顺序 ('forward' 或 'reverse')
            
        Returns:
            是否转换成功
        """
        try:
            # 映射转换顺序
            order_map = {
                'forward': self.ZOSAPI.Editors.LDE.ConversionOrder.Forward,
                'reverse': self.ZOSAPI.Editors.LDE.ConversionOrder.Reverse
            }
            
            if order not in order_map:
                raise ValueError(f"不支持的转换顺序: {order}")
                
            result = self.LDE.RunTool_ConvertGlobalToLocalCoordinates(start_surface, end_surface, order_map[order])
            logger.info(f"将表面 {start_surface} 到 {end_surface} 转换为局部坐标，顺序: {order}")
            return result
        except Exception as e:
            logger.error(f"转换局部坐标失败: {str(e)}")
            raise
    
    # === 变量与优化设置 ===
    
    def set_variable(self, surface_pos: int, param_name: str, current: float = None, status: bool = True) -> bool:
        """
        将表面参数设置为变量
        
        Args:
            surface_pos: 表面位置
            param_name: 参数名称，支持 'radius', 'thickness', 'conic' 等
            current: 当前值（可选）
            status: 变量状态，True表示启用，False表示禁用
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            
            # 参数列与变量映射
            param_column_map = {
                'radius': self.ZOSAPI.Editors.LDE.SurfaceColumn.Radius,
                'thickness': self.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness,
                'conic': self.ZOSAPI.Editors.LDE.SurfaceColumn.Conic,
                'semi_diameter': self.ZOSAPI.Editors.LDE.SurfaceColumn.SemiDiameter
            }
            
            if param_name not in param_column_map:
                raise ValueError(f"不支持的参数名称: {param_name}")
            
            # 如果提供了当前值，先设置当前值
            cell_type = param_column_map[param_name]
            cell = surface.GetCellAt(cell_type)
            if current is not None:
                cell.DoubleValue = current
                
            # 使用辅助方法设置为变量
            cell, is_var, solve_type = self.set_cell_as_variable(
                surface, 
                cell_type, 
                f"表面 {surface_pos} 的 {param_name}"
            )
            
            # 设置变量状态
            if is_var and status is not None:
                solver_data = cell.GetSolveData()
                if solver_data is not None:
                    solver_data.Status = status
                    cell.SetSolveData(solver_data)
                    solver_data.Status = status
                    cell.SetSolveData(solver_data)
            
            return is_var
            
        except Exception as e:
            logger.error(f"设置变量失败: {str(e)}")
            return False
    
    def clear_variable(self, surface_pos: int, param_name: str) -> bool:
        """
        清除变量设置
        
        Args:
            surface_pos: 表面位置
            param_name: 参数名称
            
        Returns:
            是否清除成功
        """
        try:
            surface = self.get_surface(surface_pos)
            
            # 参数列与变量映射
            param_column_map = {
                'radius': self.ZOSAPI.Editors.LDE.SurfaceColumn.Radius,
                'thickness': self.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness,
                'conic': self.ZOSAPI.Editors.LDE.SurfaceColumn.Conic,
                'semi_diameter': self.ZOSAPI.Editors.LDE.SurfaceColumn.SemiDiameter
            }
            
            if param_name not in param_column_map:
                raise ValueError(f"不支持的参数名称: {param_name}")
                
            # 获取单元格并清除变量
            cell = surface.GetCellAt(param_column_map[param_name])
            cell.ClearSolve()
            
            logger.info(f"清除表面 {surface_pos} 的 {param_name} 变量设置")
            return True
            
        except Exception as e:
            logger.error(f"清除变量失败: {str(e)}")
            return False
    
    # === 批量设置变量 ===
    
    def set_all_thickness_as_variables(self, start_surface: int = 1, end_surface: int = None, 
                                  exclude_surfaces: List[int] = None, status: bool = True) -> bool:
        """
        批量设置所有表面的厚度为变量
        
        Args:
            start_surface: 起始表面编号
            end_surface: 结束表面编号（默认为最后一个表面）
            exclude_surfaces: 排除的表面列表
            status: 变量状态，True表示启用，False表示禁用
            
        Returns:
            是否设置成功
        """
        try:
            # 尝试使用Zemax官方的工具方法
            try:
                tools = self.TheSystem.Tools
                if hasattr(tools, "SetAllThicknessesVariable"):
                    # 如果有排除表面，先清除所有变量，然后设置需要的表面
                    if exclude_surfaces and len(exclude_surfaces) > 0:
                        for i in range(start_surface, end_surface + 1):
                            if i not in exclude_surfaces:
                                surface = self.get_surface(i)
                                # 使用辅助方法设置变量
                                cell, is_var, _ = self.set_cell_as_variable(
                                    surface, 
                                    self.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness, 
                                    f"表面 {i} 的厚度"
                                )
                                # 设置变量状态
                                if is_var and status is not None:
                                    solver_data = cell.GetSolveData()
                                    if solver_data is not None:
                                        solver_data.Status = status
                                        cell.SetSolveData(solver_data)
                        return True
                    else:
                        # 没有排除表面，直接使用官方工具
                        tools.SetAllThicknessesVariable()
                        return True
            except Exception as e:
                logger.warning(f"使用官方工具设置厚度变量失败: {str(e)}")
            
            # 如果官方工具失败，则使用逐个表面设置的方法
            # 获取系统的表面数量
            surface_count = self.LDE.NumberOfSurfaces
            
            # 如果未指定结束表面，则使用最后一个表面
            if end_surface is None or end_surface > surface_count:
                end_surface = surface_count
            
            # 默认排除表面为空列表
            if exclude_surfaces is None:
                exclude_surfaces = []
            
            success = True
            
            # 遍历表面设置厚度为变量
            for i in range(start_surface, end_surface + 1):
                if i not in exclude_surfaces:
                    try:
                        result = self.set_variable(i, 'thickness', status=status)
                        success = success and result
                    except Exception as e:
                        logger.error(f"将表面 {i} 的厚度设置为变量时出错: {str(e)}")
                        success = False
            
            return success
            
        except Exception as e:
            logger.error(f"批量设置厚度变量失败: {str(e)}")
            return False
    
    def set_all_radii_as_variables(self, start_surface: int = 1, end_surface: int = None, 
                                exclude_surfaces: List[int] = None, status: bool = True) -> bool:
        """
        批量设置所有表面的曲率半径为变量
        
        Args:
            start_surface: 起始表面编号
            end_surface: 结束表面编号（默认为最后一个表面）
            exclude_surfaces: 排除的表面列表
            status: 变量状态，True表示启用，False表示禁用
            
        Returns:
            是否设置成功
        """
        try:
            # 尝试使用Zemax官方的工具方法
            try:
                tools = self.TheSystem.Tools
                if hasattr(tools, "SetAllRadiiVariable"):
                    # 如果有排除表面，先清除所有变量，然后设置需要的表面
                    if exclude_surfaces and len(exclude_surfaces) > 0:
                        tools.RemoveAllVariables()  # 清除所有变量
                        for i in range(start_surface, end_surface + 1):
                            if i not in exclude_surfaces:
                                surface = self.get_surface(i)
                                # 使用辅助方法设置变量
                                cell, is_var, _ = self.set_cell_as_variable(
                                    surface, 
                                    self.ZOSAPI.Editors.LDE.SurfaceColumn.Radius, 
                                    f"表面 {i} 的曲率半径"
                                )
                                # 设置变量状态
                                if is_var and status is not None:
                                    solver_data = cell.GetSolveData()
                                    if solver_data is not None:
                                        solver_data.Status = status
                                        cell.SetSolveData(solver_data)
                        return True
                    else:
                        # 没有排除表面，直接使用官方工具
                        tools.SetAllRadiiVariable()
                        return True
            except Exception as e:
                logger.warning(f"使用官方工具设置曲率半径变量失败: {str(e)}")
            
            # 如果官方工具失败，则使用逐个表面设置的方法
            # 获取系统的表面数量
            surface_count = self.LDE.NumberOfSurfaces
            
            # 如果未指定结束表面，则使用最后一个表面
            if end_surface is None or end_surface > surface_count:
                end_surface = surface_count
            
            # 默认排除表面为空列表
            if exclude_surfaces is None:
                exclude_surfaces = []
            
            success = True
            
            # 遍历表面设置曲率半径为变量
            for i in range(start_surface, end_surface + 1):
                if i not in exclude_surfaces:
                    try:
                        result = self.set_variable(i, 'radius', status=status)
                        success = success and result
                    except Exception as e:
                        logger.error(f"将表面 {i} 的曲率半径设置为变量时出错: {str(e)}")
                        success = False
            
            return success
            
        except Exception as e:
            logger.error(f"批量设置曲率半径变量失败: {str(e)}")
            return False
    
    def set_all_conics_as_variables(self, start_surface: int = 1, end_surface: int = None, 
                                 exclude_surfaces: List[int] = None, 
                                 status: bool = True) -> bool:
        """
        批量设置所有表面的锥面系数为变量
        
        Args:
            start_surface: 起始表面编号
            end_surface: 结束表面编号（默认为最后一个表面）
            exclude_surfaces: 排除的表面列表
            status: 变量状态，True表示启用，False表示禁用
            
        Returns:
            是否设置成功
        """
        try:
            # 获取系统的表面数量
            surface_count = self.LDE.NumberOfSurfaces
            
            # 如果未指定结束表面，则使用最后一个表面
            if end_surface is None or end_surface > surface_count:
                end_surface = surface_count
            
            # 默认排除表面为空列表
            if exclude_surfaces is None:
                exclude_surfaces = []
            
            success = True
            
            # 遍历表面设置锥面系数为变量
            for i in range(start_surface, end_surface + 1):
                if i not in exclude_surfaces:
                    try:
                        # 获取表面
                        surface = self.get_surface(i)
                        
                        # 获取当前锥面系数值
                        current_value = 0.0
                        try:
                            # 尝试直接获取锥面系数
                            current_value = surface.Conic
                        except:
                            # 如果无法直接获取锥面系数，尝试从单元格获取
                            try:
                                conic_cell = surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Conic)
                                if hasattr(conic_cell, "DoubleValue"):
                                    current_value = conic_cell.DoubleValue
                                else:
                                    try:
                                        current_value = float(conic_cell.Value)
                                    except:
                                        current_value = 0.0
                            except:
                                current_value = 0.0
                        
                        # 直接从单元格设置变量
                        try:
                            conic_cell = surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Conic)
                            
                            # 确保单元格有值
                            conic_cell.Value = str(current_value)
                            
                            # 使用辅助方法设置变量
                            cell, is_var, _ = self.set_cell_as_variable(
                                surface, 
                                self.ZOSAPI.Editors.LDE.SurfaceColumn.Conic, 
                                f"表面 {i} 的锥面系数"
                            )
                            
                            # 设置变量状态
                            if is_var and status is not None:
                                solver_data = cell.GetSolveData()
                                if solver_data is not None:
                                    solver_data.Status = status
                                    cell.SetSolveData(solver_data)
                        except Exception as e:
                            logger.error(f"设置表面 {i} 的锥面系数变量失败: {str(e)}")
                            # 尝试使用备用方法
                            try:
                                result = self.set_variable(i, 'conic', current=current_value, status=status)
                                success = success and result
                            except Exception as e2:
                                logger.error(f"备用方法设置表面 {i} 的锥面系数变量失败: {str(e2)}")
                                success = False
                    except Exception as e:
                        logger.error(f"将表面 {i} 的锥面系数设置为变量时出错: {str(e)}")
                        success = False
            
            return success
            
        except Exception as e:
            logger.error(f"批量设置锥面系数变量失败: {str(e)}")
            return False
    
    def set_all_aspheric_as_variables(self, start_surface: int = 1, end_surface: int = None, 
                                   exclude_surfaces: List[int] = None, order: int = 4,
                                   status: bool = True) -> bool:
        """
        批量设置所有表面的非球面各阶系数为变量
        
        Args:
            start_surface: 起始表面编号
            end_surface: 结束表面编号（默认为最后一个表面）
            exclude_surfaces: 排除的表面列表
            order: 设置到第几阶系数（2为4阶，3为6阶，4为8阶，5为10阶...）
            status: 变量状态，True表示启用，False表示禁用
            
        Returns:
            是否设置成功
        """
        try:
            # 获取系统的表面数量
            surface_count = self.LDE.NumberOfSurfaces
            
            # 如果未指定结束表面，则使用最后一个表面
            if end_surface is None or end_surface > surface_count:
                end_surface = surface_count
            
            # 默认排除表面为空列表
            if exclude_surfaces is None:
                exclude_surfaces = []
            
            success = True
            
            # 遍历表面设置非球面系数为变量
            for i in range(start_surface, end_surface + 1):
                if i not in exclude_surfaces:
                    try:
                        # 获取表面
                        surface = self.get_surface(i)
                        
                        # 尝试识别是否为非球面表面
                        is_aspheric = False
                        
                        # 方法1: 通过表面类型判断
                        try:
                            if hasattr(surface, "SurfaceType"):
                                surface_type = str(surface.SurfaceType).lower()
                                is_aspheric = ('aspheric' in surface_type or 'even' in surface_type)
                        except:
                            pass
                        
                        # 方法2: 通过单元格类型判断
                        if not is_aspheric:
                            try:
                                type_cell = surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Type)
                                if type_cell:
                                    type_value = str(type_cell.Value).lower()
                                    is_aspheric = ('aspheric' in type_value or 'even' in type_value)
                            except:
                                pass
                        
                        # 方法3: 检查是否有非零非球面系数
                        if not is_aspheric:
                            try:
                                # 检查前几个非球面系数
                                for j in range(4):
                                    param_cell = surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Par1 + j)
                                    if param_cell:
                                        try:
                                            param_value = param_cell.DoubleValue
                                        except:
                                            try:
                                                param_value = float(param_cell.Value)
                                            except:
                                                param_value = 0.0
                                                
                                        if abs(param_value) > 1e-16:
                                            is_aspheric = True
                                            break
                            except:
                                pass
                        
                        # 如果不是非球面表面，可以跳过或尝试设置为非球面
                        if not is_aspheric:
                            logger.warning(f"表面 {i} 可能不是非球面表面，但仍将尝试设置非球面系数")
                            try:
                                # 尝试将表面设置为非球面类型
                                self.set_surface_type(i, 'aspheric')
                            except:
                                logger.warning(f"无法将表面 {i} 设置为非球面类型，但仍将尝试设置非球面系数")
                        
                        # 设置各阶非球面系数为变量
                        for j in range(order):
                            try:
                                # 获取当前系数单元格
                                param_cell = surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Par1 + j)
                                
                                # 获取当前值
                                current_value = 0.0
                                try:
                                    if hasattr(param_cell, "DoubleValue"):
                                        current_value = param_cell.DoubleValue
                                    else:
                                        try:
                                            current_value = float(param_cell.Value)
                                        except:
                                            current_value = 0.0
                                except:
                                    current_value = 0.0
                                
                                # 确保单元格有值
                                param_cell.Value = str(current_value)
                                
                                # 使用辅助方法设置变量
                                cell, is_var, _ = self.set_cell_as_variable(
                                    surface, 
                                    self.ZOSAPI.Editors.LDE.SurfaceColumn.Par1 + j, 
                                    f"表面 {i} 的非球面{(j+1)*2+2}阶系数"
                                )
                                
                                # 设置变量状态
                                if is_var and status is not None:
                                    solver_data = cell.GetSolveData()
                                    if solver_data is not None:
                                        solver_data.Status = status
                                        cell.SetSolveData(solver_data)
                            except Exception as e:
                                logger.error(f"将表面 {i} 的非球面{(j+1)*2+2}阶系数设置为变量时出错: {str(e)}")
                                success = False
                    except Exception as e:
                        logger.error(f"处理表面 {i} 的非球面系数时出错: {str(e)}")
                        success = False
            
            return success
            
        except Exception as e:
            logger.error(f"批量设置非球面系数变量失败: {str(e)}")
            return False
    

    def set_surface_parameters(self, surface_pos: int, **kwargs) -> bool:
        """
        设置表面的多个参数
        
        Args:
            surface_pos: 表面位置（从0开始）
            **kwargs: 参数名和值的字典，支持的参数包括:
                - radius: 曲率半径
                - thickness: 厚度
                - material: 材料
                - conic: 锥面系数
                - semi_diameter: 半口径
                - comment: 注释
                
        Returns:
            是否设置成功
        """
        try:
            # 参数设置映射
            param_setters = {
                'radius': self.set_radius,
                'thickness': self.set_thickness,
                'material': self.set_material,
                'conic': self.set_conic,
                'semi_diameter': self.set_semi_diameter,
                'comment': self.set_comment
            }
            
            success = True
            
            # 设置各个参数
            for param_name, param_value in kwargs.items():
                if param_name in param_setters and param_value is not None:
                    setter_func = param_setters[param_name]
                    result = setter_func(surface_pos, param_value)
                    success = success and result
                else:
                    logger.warning(f"未知或空参数: {param_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"设置表面参数失败: {str(e)}")
            return False

    def set_comment(self, surface_pos: int, comment: str) -> bool:
        """
        设置表面注释
        
        Args:
            surface_pos: 表面位置
            comment: 注释文本
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            cell = surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Comment)
            cell.Value = comment
            logger.info(f"设置表面 {surface_pos} 的注释为: {comment}")
            return True
        except Exception as e:
            logger.error(f"设置表面注释失败: {str(e)}")
            return False

    def set_cell_as_variable(self, surface, column_type, description="") -> tuple:
        """
        将表面的单元格设置为变量
        
        Args:
            surface: 表面对象
            column_type: 列类型（SurfaceColumn枚举值）
            description: 变量描述
            
        Returns:
            (cell, is_variable, solve_type): 单元格对象、是否成功设置为变量、求解器类型
        """
        try:
            # 获取单元格
            cell = surface.GetCellAt(column_type)
            
            # 设置为变量 - 尝试使用最通用的方法
            try:
                # 方法1: 直接调用MakeSolveVariable（官方推荐方式）
                cell.MakeSolveVariable()
                solver_data = cell.GetSolveData()
                solve_type = solver_data.Type if solver_data else None
                
                logger.info(f"成功将{description}设置为变量")
                return cell, True, solve_type
            except Exception as e1:
                logger.debug(f"使用MakeSolveVariable设置变量失败: {str(e1)}")
                
                # 尝试其他方式
                try:
                    # 方法2: 使用SetSolveData设置Variable类型
                    solver_data = cell.GetSolveData()
                    if solver_data is None:
                        # 创建一个新的求解数据
                        solver_data = cell.CreateSolveData()
                    
                    # 设置为变量类型(通常变量类型为1)
                    solver_data.Type = 1
                    cell.SetSolveData(solver_data)
                    
                    logger.info(f"使用SetSolveData成功将{description}设置为变量")
                    return cell, True, 1
                except Exception as e2:
                    logger.debug(f"使用SetSolveData设置变量失败: {str(e2)}")
                    
                    # 最后的尝试
                    try:
                        # 方法3: 使用特定的API设置
                        cell.MakeVariable()
                        logger.info(f"使用MakeVariable成功将{description}设置为变量")
                        return cell, True, None
                    except Exception as e3:
                        logger.error(f"所有设置变量方法都失败: {str(e3)}")
                        return cell, False, None
        except Exception as e:
            logger.error(f"设置单元格变量时出错: {str(e)}")
            return None, False, None
            
    def get_system_info(self) -> dict:
        """
        获取系统基本信息
        
        Returns:
            dict: 包含表面数量、光阑面位置等信息的字典
        """
        try:
            info = {}
            info['surfaces'] = self.LDE.NumberOfSurfaces
            
            # 查找光阑面位置
            stop_surface = -1
            for i in range(1, info['surfaces'] + 1):
                try:
                    surface = self.get_surface(i)
                    if hasattr(surface, 'IsStop') and surface.IsStop:
                        stop_surface = i
                        break
                except:
                    pass
            
            info['stop_surface'] = stop_surface
            
            # 获取其他系统信息
            if hasattr(self.TheSystem, 'SystemData'):
                system_data = self.TheSystem.SystemData
                
                # 获取视场信息
                try:
                    info['fields'] = system_data.Fields.NumberOfFields
                except:
                    info['fields'] = 0
                
                # 获取波长信息
                try:
                    info['wavelengths'] = system_data.Wavelengths.NumberOfWavelengths
                except:
                    info['wavelengths'] = 0
            
            return info
        except Exception as e:
            logger.error(f"获取系统信息失败: {str(e)}")
            return {'surfaces': 0, 'stop_surface': -1, 'fields': 0, 'wavelengths': 0}
    
    def set_stop_surface(self, surface_pos: int, remove: bool = False) -> bool:
        """
        设置光阑面
        
        Args:
            surface_pos: 光阑面位置
            remove: 是否移除光阑面设置（只在surface_pos=0时有效）
            
        Returns:
            是否设置成功
        """
        try:
            # 如果是移除光阑面
            if remove or surface_pos <= 0:
                # 查找并清除当前光阑面
                for i in range(1, self.get_surface_count() + 1):
                    try:
                        surface = self.get_surface(i)
                        if hasattr(surface, 'IsStop') and surface.IsStop:
                            surface.IsStop = False
                            logger.info(f"清除位置 {i} 的光阑面设置")
                    except:
                        pass
                return True
            
            # 设置新的光阑面
            surface = self.get_surface(surface_pos)
            
            # 先清除其他表面的光阑设置
            for i in range(1, self.get_surface_count() + 1):
                if i != surface_pos:
                    try:
                        other_surface = self.get_surface(i)
                        if hasattr(other_surface, 'IsStop') and other_surface.IsStop:
                            other_surface.IsStop = False
                            logger.info(f"清除位置 {i} 的光阑面设置")
                    except:
                        pass
            
            # 设置新的光阑面
            # 方法1: 使用IsStop属性（官方推荐）
            try:
                surface.IsStop = True
                logger.info(f"使用IsStop=True设置表面 {surface_pos} 为光阑面")
                
                # 验证是否成功
                if hasattr(surface, 'IsStop') and surface.IsStop:
                    return True
            except Exception as e:
                logger.debug(f"使用IsStop设置光阑面失败: {str(e)}")
            
            # 方法2: 使用set_aperture方法的备用方案
            try:
                self.set_aperture(surface_pos, "none")
                logger.info(f"使用set_aperture('none')设置表面 {surface_pos} 为光阑面")
                return True
            except Exception as e:
                logger.error(f"设置光阑面失败: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"设置光阑面失败: {str(e)}")
            return False

# 便捷方法，创建镜头设计管理器
def create_lens_design_manager(zos_manager):
    """
    创建镜头设计管理器实例
    
    Args:
        zos_manager: ZOSAPIManager 实例
        
    Returns:
        LensDesignManager 实例
    """
    return LensDesignManager(zos_manager)
