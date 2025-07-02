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
log_level = getattr(logging, LOG_SETTINGS.get("level", "WARNING").upper())
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
            
            # 映射表面类型
            surface_type_map = {
                'standard': self.ZOSAPI.Editors.LDE.SurfaceType.Standard,
                'conic': self.ZOSAPI.Editors.LDE.SurfaceType.EvenAspheric,
                'aspheric': self.ZOSAPI.Editors.LDE.SurfaceType.EvenAspheric,
                'toroidal': self.ZOSAPI.Editors.LDE.SurfaceType.Toroidal,
                'coordinate_break': self.ZOSAPI.Editors.LDE.SurfaceType.CoordinateBreak,
                'paraxial': self.ZOSAPI.Editors.LDE.SurfaceType.Paraxial,
                'grid_sag': self.ZOSAPI.Editors.LDE.SurfaceType.GridSag,
                'zernike': self.ZOSAPI.Editors.LDE.SurfaceType.ZernikeSag
            }
            
            if surface_type not in surface_type_map:
                raise ValueError(f"不支持的表面类型: {surface_type}")
            
            type_setting = surface.GetSurfaceTypeSettings(surface_type_map[surface_type])
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
            aperture_type: 光阑类型 (circular, rectangular, float 等)
            x_half_width: X方向半宽度
            y_half_width: Y方向半宽度
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            aperture_data = surface.ApertureData
            
            # 映射光阑类型
            aperture_type_map = {
                'circular': self.ZOSAPI.Editors.LDE.SurfaceApertureTypes.CircularAperture,
                'rectangular': self.ZOSAPI.Editors.LDE.SurfaceApertureTypes.RectangularAperture,
                'float': self.ZOSAPI.Editors.LDE.SurfaceApertureTypes.FloatingAperture,
                'none': getattr(self.ZOSAPI.Editors.LDE.SurfaceApertureTypes, 'None')
            }
            
            if aperture_type not in aperture_type_map:
                raise ValueError(f"不支持的光阑类型: {aperture_type}")
            
            aperture_setting = aperture_data.CreateApertureTypeSettings(aperture_type_map[aperture_type])
            
            # 设置光阑参数
            if aperture_type == 'circular':
                aperture_setting._S_CircularAperture.Radius = x_half_width
            elif aperture_type == 'rectangular':
                aperture_setting._S_RectangularAperture.XHalfWidth = x_half_width
                aperture_setting._S_RectangularAperture.YHalfWidth = y_half_width
            
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
            
            # 检查表面类型是否为非球面
            surface_type_name = str(surface.SurfaceType)
            if "Aspheric" not in surface_type_name and "aspheric" not in surface_type_name:
                raise ValueError(f"表面 {surface_pos} 不是非球面类型，当前类型: {surface_type_name}")
            
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
    
    def set_variable(self, surface_pos: int, param_name: str, min_value: float = None, 
                  max_value: float = None, current: float = None, status: bool = True) -> bool:
        """
        将表面参数设置为变量
        
        Args:
            surface_pos: 表面位置
            param_name: 参数名称，支持 'radius', 'thickness', 'conic' 等
            min_value: 变量最小值（可选）
            max_value: 变量最大值（可选）
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
            cell = surface.GetCellAt(param_column_map[param_name])
            if current is not None:
                cell.DoubleValue = current
                
            # 获取单元格并设置为变量
            cell.MakeSolveVariable()
            
            # 设置最小值和最大值（如果提供）
            solver_data = cell.GetSolveData()
            if solver_data is not None:
                if min_value is not None:
                    solver_data.MinValue = min_value
                if max_value is not None:
                    solver_data.MaxValue = max_value
                solver_data.Status = status
                cell.SetSolveData(solver_data)
            
            logger.info(f"将表面 {surface_pos} 的 {param_name} 设置为变量")
            return True
            
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
                                     exclude_surfaces: List[int] = None, 
                                     min_value: float = 0.1, max_value: float = 50.0) -> bool:
        """
        批量设置所有表面厚度为变量
        
        Args:
            start_surface: 起始表面编号
            end_surface: 结束表面编号（默认为最后一个表面）
            exclude_surfaces: 排除的表面列表
            min_value: 最小值
            max_value: 最大值
            
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
            
            # 遍历表面设置厚度为变量
            for i in range(start_surface, end_surface):
                if i not in exclude_surfaces:
                    try:
                        # 获取当前厚度值作为初始值
                        surface = self.get_surface(i)
                        current_value = surface.Thickness
                        
                        # 设置厚度为变量
                        result = self.set_variable(i, 'thickness', min_value=min_value, 
                                                max_value=max_value, current=current_value)
                        success = success and result
                        
                        logger.info(f"将表面 {i} 的厚度设置为变量，范围: [{min_value}, {max_value}]")
                    except Exception as e:
                        logger.error(f"将表面 {i} 的厚度设置为变量时出错: {str(e)}")
                        success = False
            
            return success
            
        except Exception as e:
            logger.error(f"批量设置厚度变量失败: {str(e)}")
            return False
    
    def set_all_radii_as_variables(self, start_surface: int = 1, end_surface: int = None, 
                                exclude_surfaces: List[int] = None, 
                                min_value: float = -500.0, max_value: float = 500.0) -> bool:
        """
        批量设置所有表面曲率半径为变量
        
        Args:
            start_surface: 起始表面编号
            end_surface: 结束表面编号（默认为最后一个表面）
            exclude_surfaces: 排除的表面列表
            min_value: 最小值
            max_value: 最大值
            
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
            
            # 遍历表面设置曲率半径为变量
            for i in range(start_surface, end_surface):
                if i not in exclude_surfaces:
                    try:
                        # 获取当前曲率半径值作为初始值
                        surface = self.get_surface(i)
                        current_value = surface.Radius
                        
                        # 如果是平面（无穷大半径），设置一个合理的初始值
                        if abs(current_value) > 1e9:
                            if current_value > 0:
                                current_value = 100.0
                            else:
                                current_value = -100.0
                        
                        # 设置曲率半径为变量
                        result = self.set_variable(i, 'radius', min_value=min_value, 
                                                max_value=max_value, current=current_value)
                        success = success and result
                        
                        logger.info(f"将表面 {i} 的曲率半径设置为变量，范围: [{min_value}, {max_value}]")
                    except Exception as e:
                        logger.error(f"将表面 {i} 的曲率半径设置为变量时出错: {str(e)}")
                        success = False
            
            return success
            
        except Exception as e:
            logger.error(f"批量设置曲率半径变量失败: {str(e)}")
            return False
    
    def set_all_conics_as_variables(self, start_surface: int = 1, end_surface: int = None, 
                                 exclude_surfaces: List[int] = None, 
                                 min_value: float = -5.0, max_value: float = 0.0) -> bool:
        """
        批量设置所有表面的锥面系数为变量
        
        Args:
            start_surface: 起始表面编号
            end_surface: 结束表面编号（默认为最后一个表面）
            exclude_surfaces: 排除的表面列表
            min_value: 最小值
            max_value: 最大值
            
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
                            
                            # 设置为变量
                            conic_cell.MakeSolveVariable()
                            
                            # 设置变量范围
                            solver_data = conic_cell.GetSolveData()
                            if solver_data is not None:
                                solver_data.MinValue = min_value
                                solver_data.MaxValue = max_value
                                solver_data.Status = True
                                conic_cell.SetSolveData(solver_data)
                            
                            logger.info(f"将表面 {i} 的锥面系数设置为变量，范围: [{min_value}, {max_value}]")
                        except Exception as e:
                            logger.error(f"设置表面 {i} 的锥面系数变量失败: {str(e)}")
                            # 尝试使用备用方法
                            try:
                                result = self.set_variable(i, 'conic', min_value=min_value, 
                                                        max_value=max_value, current=current_value)
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
                                   min_value: float = -0.1, max_value: float = 0.1) -> bool:
        """
        批量设置所有表面的非球面各阶系数为变量
        
        Args:
            start_surface: 起始表面编号
            end_surface: 结束表面编号（默认为最后一个表面）
            exclude_surfaces: 排除的表面列表
            order: 设置到第几阶系数（2为4阶，3为6阶，4为8阶，5为10阶...）
            min_value: 最小值
            max_value: 最大值
            
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
                                
                                # 设置为变量
                                param_cell.MakeSolveVariable()
                                
                                # 设置变量范围
                                solver_data = param_cell.GetSolveData()
                                if solver_data is not None:
                                    solver_data.MinValue = min_value
                                    solver_data.MaxValue = max_value
                                    solver_data.Status = True
                                    param_cell.SetSolveData(solver_data)
                                
                                logger.info(f"将表面 {i} 的非球面{(j+1)*2+2}阶系数设置为变量，范围: [{min_value}, {max_value}]")
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
    
    # === 求解器设置 ===
    
    def set_solver(self, surface_pos: int, solver_type: str, param_name: str, 
                 target_value: float = None, reference_surface: int = None) -> bool:
        """
        设置求解器
        
        Args:
            surface_pos: 表面位置
            solver_type: 求解器类型，支持 'position', 'thickness', 'curvature', 'pickup' 等
            param_name: 参数名称
            target_value: 目标值（对于某些求解器类型是必需的）
            reference_surface: 参考表面（对于pickup求解器是必需的）
            
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
                'semi_diameter': self.ZOSAPI.Editors.LDE.SurfaceColumn.SemiDiameter,
                'material': self.ZOSAPI.Editors.LDE.SurfaceColumn.Material
            }
            
            if param_name not in param_column_map:
                raise ValueError(f"不支持的参数名称: {param_name}")
            
            cell = surface.GetCellAt(param_column_map[param_name])
            
            # 根据求解器类型设置不同的求解器
            if solver_type == 'fixed':
                # 固定参数值
                cell.ClearSolve()
                if target_value is not None:
                    if param_name == 'material':
                        cell.Value = target_value
                    else:
                        cell.DoubleValue = target_value
            
            elif solver_type == 'pickup':
                # 拾取求解器
                if reference_surface is None:
                    raise ValueError("pickup求解器需要指定reference_surface")
                    
                try:
                    # 方法1: 直接调用MakeSolvePickup
                    cell.MakeSolvePickup()
                except:
                    try:
                        # 方法2: 使用SetSolveData设置Pickup类型
                        solver_data = cell.GetSolveData()
                        solver_data.Type = 3  # 3通常是Pickup求解器类型
                        cell.SetSolveData(solver_data)
                    except:
                        logger.warning(f"无法设置Pickup求解器，尝试替代方法")
                
                # 设置求解器参数
                solver_data = cell.GetSolveData()
                try:
                    solver_data.PickupSurface = reference_surface
                except:
                    try:
                        solver_data.Source = reference_surface
                    except:
                        logger.warning(f"无法设置参考表面")
                        
                if target_value is not None:  # 可选的缩放系数
                    try:
                        solver_data.ScaleFactor = target_value
                    except:
                        try:
                            solver_data.Scale = target_value
                        except:
                            logger.warning(f"无法设置缩放系数")
                
                cell.SetSolveData(solver_data)
            
            elif solver_type == 'marginal_ray':
                # 边缘光线求解器
                cell.MakeSolveMarginalRay()
                solver_data = cell.GetSolveData()
                if target_value is not None:
                    solver_data.PupilZoneHeight = target_value
                cell.SetSolveData(solver_data)
            
            elif solver_type == 'chief_ray':
                # 主光线求解器
                cell.MakeSolveChiefRay()
                solver_data = cell.GetSolveData()
                if target_value is not None:
                    solver_data.PupilZoneHeight = target_value
                cell.SetSolveData(solver_data)
            
            elif solver_type == 'edge_thickness':
                # 边缘厚度求解器
                try:
                    # 方法1: 直接调用MakeSolveEdgeThickness
                    cell.MakeSolveEdgeThickness()
                except:
                    try:
                        # 方法2: 使用SetSolveData设置EdgeThickness类型
                        solver_data = cell.GetSolveData()
                        solver_data.Type = 4  # 4通常是EdgeThickness求解器类型
                        cell.SetSolveData(solver_data)
                    except:
                        logger.warning(f"无法设置边缘厚度求解器，尝试替代方法")
                
                # 设置目标值
                solver_data = cell.GetSolveData()
                if target_value is not None:
                    try:
                        solver_data.EdgeThickness = target_value
                    except:
                        try:
                            solver_data.Target = target_value
                        except:
                            logger.warning(f"无法设置边缘厚度目标值")
                
                cell.SetSolveData(solver_data)
                if target_value is not None:
                    solver_data.TargetEdgeThickness = target_value
                cell.SetSolveData(solver_data)
            
            else:
                raise ValueError(f"不支持的求解器类型: {solver_type}")
            
            logger.info(f"在表面 {surface_pos} 为 {param_name} 设置 {solver_type} 求解器")
            return True
            
        except Exception as e:
            logger.error(f"设置求解器失败: {str(e)}")
            return False
    
    def set_pickup_solver(self, surface_pos: int, param_name: str, 
                       reference_surface: int, scale_factor: float = 1.0) -> bool:
        """
        设置拾取求解器的快捷方法
        
        Args:
            surface_pos: 表面位置
            param_name: 参数名称
            reference_surface: 参考表面
            scale_factor: 缩放系数（默认为1.0）
            
        Returns:
            是否设置成功
        """
        return self.set_solver(surface_pos, 'pickup', param_name, 
                              target_value=scale_factor, 
                              reference_surface=reference_surface)
    
    def set_edge_thickness_solver(self, surface_pos: int, target_thickness: float) -> bool:
        """
        设置边缘厚度求解器的快捷方法
        
        Args:
            surface_pos: 表面位置
            target_thickness: 目标边缘厚度
            
        Returns:
            是否设置成功
        """
        return self.set_solver(surface_pos, 'edge_thickness', 'thickness', 
                              target_value=target_thickness)
    
    # === 多组态设置 ===
    
    def add_configuration(self, name: str = None) -> int:
        """
        添加新的组态
        
        Args:
            name: 组态名称（可选）
            
        Returns:
            新组态的索引，如果失败则返回-1
        """
        try:
            configs = self.TheSystem.MCE
            
            # 尝试多种方式添加配置
            try:
                # 方法1：不带参数
                new_config = configs.AddConfiguration()
            except:
                try:
                    # 方法2：带名称参数
                    config_name = name or f"配置 {configs.NumberOfConfigurations + 1}"
                    new_config = configs.AddConfiguration(config_name)
                except:
                    try:
                        # 方法3：复制现有配置
                        new_config = configs.AddConfiguration(1, 1)  # 复制第一个配置
                    except:
                        # 如果都失败，尝试简单的插入
                        try:
                            configs.InsertConfiguration(configs.NumberOfConfigurations + 1)
                            new_config = configs.GetConfiguration(configs.NumberOfConfigurations)
                        except:
                            raise ValueError("无法添加新组态，请检查API文档")
            
            # 设置名称（如果提供且支持）
            if name is not None:
                try:
                    new_config.Name = name
                except:
                    try:
                        configs.SetName(configs.NumberOfConfigurations, name)
                    except:
                        logger.warning(f"无法设置组态名称: {name}")
                
            index = configs.NumberOfConfigurations
            logger.info(f"添加了新组态: {name or f'配置 {index}'}")
            return index
            
        except Exception as e:
            logger.error(f"添加组态失败: {str(e)}")
            return -1
    
    def set_configuration_parameter(self, config_index: int, surface_pos: int, 
                                param_name: str, value: Any) -> bool:
        """
        设置特定组态的参数值
        
        Args:
            config_index: 组态索引
            surface_pos: 表面位置
            param_name: 参数名称
            value: 参数值
            
        Returns:
            是否设置成功
        """
        try:
            configs = self.TheSystem.MCE
            
            if config_index <= 0 or config_index > configs.NumberOfConfigurations:
                raise ValueError(f"无效的组态索引: {config_index}")
            
            # 先设置当前组态
            current_config = configs.CurrentConfiguration
            configs.SetCurrentConfiguration(config_index)
            
            # 参数列映射
            param_column_map = {
                'radius': self.ZOSAPI.Editors.LDE.SurfaceColumn.Radius,
                'thickness': self.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness,
                'conic': self.ZOSAPI.Editors.LDE.SurfaceColumn.Conic,
                'semi_diameter': self.ZOSAPI.Editors.LDE.SurfaceColumn.SemiDiameter,
                'material': self.ZOSAPI.Editors.LDE.SurfaceColumn.Material
            }
            
            if param_name not in param_column_map:
                raise ValueError(f"不支持的参数名称: {param_name}")
            
            # 设置参数值
            surface = self.get_surface(surface_pos)
            cell = surface.GetCellAt(param_column_map[param_name])
            
            if param_name == 'material':
                cell.Value = value
            else:
                cell.DoubleValue = value
            
            # 恢复原始组态
            configs.SetCurrentConfiguration(current_config)
            
            logger.info(f"在组态 {config_index} 中设置表面 {surface_pos} 的 {param_name} 为 {value}")
            return True
            
        except Exception as e:
            logger.error(f"设置组态参数失败: {str(e)}")
            # 尝试恢复原始组态
            try:
                configs.SetCurrentConfiguration(current_config)
            except:
                pass
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

    def set_stop_surface(self, surface_pos: int) -> bool:
        """
        设置光阑面
        
        Args:
            surface_pos: 表面位置
            
        Returns:
            是否设置成功
        """
        try:
            # 尝试多种方法设置光阑面
            try:
                # 方法1：通过LDE直接设置
                self.LDE.SetApertureStop(surface_pos)
            except:
                try:
                    # 方法2：通过TheSystem.SystemData设置
                    self.TheSystem.SystemData.Aperture.ApertureStopSurface = surface_pos
                except:
                    # 方法3：通过修改表面类型为光阑
                    surface = self.get_surface(surface_pos)
                    cell = surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Type)
                    cell.Value = "STOP"
            
            logger.info(f"设置表面 {surface_pos} 为光阑面")
            return True
        except Exception as e:
            logger.error(f"设置光阑面失败: {str(e)}")
            return False

    def get_param_code(self, param_name: str) -> int:
        """
        获取参数对应的代码
        
        Args:
            param_name: 参数名称
            
        Returns:
            参数代码
        """
        param_code_map = {
            'radius': 0,  # ZOSAPI.Editors.LDE.SolveType.Curvature
            'thickness': 1,  # ZOSAPI.Editors.LDE.SolveType.Thickness
            'material': 2,  # 材料没有求解器编号，使用自定义编号
            'conic': 3,  # ZOSAPI.Editors.LDE.SolveType.Conic
            'semi_diameter': 4  # 半口径没有求解器编号，使用自定义编号
        }
        
        return param_code_map.get(param_name, -1)
        
    def get_system_info(self) -> Dict:
        """
        获取系统基本信息
        
        Returns:
            包含系统信息的字典
        """
        try:
            # 获取表面数量
            surface_count = self.LDE.NumberOfSurfaces
            
            # 获取物距和总长
            object_distance = 0
            total_length = 0
            component_count = 0
            
            # 使用更健壮的方法获取信息
            try:
                if surface_count > 0:
                    # 尝试获取物距（第一个表面的厚度）
                    try:
                        object_surface = self.LDE.GetSurfaceAt(1)
                        thickness_cell = object_surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness)
                        object_distance = thickness_cell.DoubleValue
                    except:
                        logger.warning("无法获取物距")
                    
                    # 计算总长度（所有表面厚度之和）
                    for i in range(1, surface_count + 1):
                        try:
                            surface = self.LDE.GetSurfaceAt(i)
                            thickness_cell = surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness)
                            total_length += thickness_cell.DoubleValue
                        except:
                            pass
                
                    # 计算组件数量（考虑材料非空的表面数）
                    for i in range(1, surface_count):
                        try:
                            surface = self.LDE.GetSurfaceAt(i)
                            material_cell = surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Material)
                            if material_cell.Value and material_cell.Value != "":
                                component_count += 1
                        except:
                            pass
            except Exception as inner_e:
                logger.warning(f"获取详细系统信息时出错: {str(inner_e)}")
            
            return {
                'surface_count': surface_count,
                'component_count': component_count,
                'object_distance': object_distance,
                'total_length': total_length
            }
            
        except Exception as e:
            logger.error(f"获取系统信息失败: {str(e)}")
            return {
                'surface_count': 0,
                'component_count': 0,
                'object_distance': 0,
                'total_length': 0,
                'error': str(e)
            }
            
        return {
            'surface_count': 0,
            'component_count': 0,
            'object_distance': 0,
            'total_length': 0
        }

# 便捷函数，创建镜头设计管理器
def create_lens_design_manager(zos_manager):
    """
    创建镜头设计管理器实例
    
    Args:
        zos_manager: ZOSAPIManager 实例
        
    Returns:
        LensDesignManager 实例
    """
    return LensDesignManager(zos_manager)
