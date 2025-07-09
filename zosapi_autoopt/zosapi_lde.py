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
    
    def set_surface_type(self, surface_pos: int, surface_type: str):
        """
        设置表面类型，使用全面且准确的映射字典。

        Args:
            surface_pos (int): 表面位置。
            surface_type (str): 表面类型的用户友好名称 (小写)。
        """
        surface_type_mapping = {
            # --- Standard & General ---
            'standard': 'Standard',
            'paraxial': 'Paraxial',
            'coordinate_break': 'CoordinateBreak',
            'dummy': 'Standard', # Dummy is a standard surface with no optical properties
            
            # --- Aspheric Surfaces (非球面) ---
            'evenaspheric': 'EvenAspheric',
            'oddaspheric': 'OddAspheric',
            'qtypeasphere': 'QTypeAsphere',
            'conic': 'EvenAspheric', # Conic is a property, but usually set on an aspheric surface
            'aspheric': 'EvenAspheric', # Common alias
            'toroidal': 'Toroidal',
            'polynomial': 'Polynomial',
            'zernikesag': 'ZernikeSag',
            'extendedasphere': 'ExtendedAsphere',
            'superconic': 'Superconic',
            'cubicsp': 'CubicSpline',
            'aspherictoroid': 'AsphericToroid',
            
            # --- Diffractive & Grating (衍射与光栅) ---
            'binaryoptic1': 'BinaryOptic1',
            'binaryoptic2': 'BinaryOptic2',
            'diffractiongrating': 'DiffractionGrating',
            'hologram1': 'Hologram1',
            'hologram2': 'Hologram2',
            'toroidalhologram': 'ToroidalHologram',

            # --- Grid Based & Freeform ---
            'gridsag': 'GridSag',
            'gridphasesag': 'GridPhase',
            
            # --- Others ---
            'fresnel': 'Fresnel',
            'variable': 'Variable',
            'tiltsurface': 'Tilted',
            # ... and many more could be added as needed
        }
        
        # 将输入统一转为小写，以便不区分大小写地查找
        normalized_surface_type = surface_type.lower().replace(" ", "").replace("_", "")

        if normalized_surface_type not in surface_type_mapping:
            raise ValueError(
                f"不支持的表面类型: '{surface_type}'. "
                f"支持的类型包括: {list(surface_type_mapping.keys())}"
            )
            
        api_type_name = surface_type_mapping[normalized_surface_type]
        
        surface = self.get_surface(surface_pos)
        type_enum = getattr(self.ZOSAPI.Editors.LDE.SurfaceType, api_type_name)
        type_settings = surface.GetSurfaceTypeSettings(type_enum)
        surface.ChangeType(type_settings)
        
        logger.info(f"成功将表面 {surface_pos} 的类型设置为: {api_type_name}")
    
    def set_conic(self, surface_pos: int, conic_value: float):
        """
        精确地设置表面的锥面系数 (Conic Constant)。

        Args:
            surface_pos (int): 表面位置。
            conic_value (float): 锥面系数值。
        """
        surface = self.get_surface(surface_pos)
        surface.Conic = conic_value
        logger.info(f"成功将表面 {surface_pos} 的锥面系数设置为: {conic_value}")

    def set_aspheric_coefficients(self, surface_pos: int, coefficients: Dict[int, float]):
        """
        以智能、安全的方式设置非球面系数。

        Args:
            surface_pos (int): 表面位置。
            coefficients (Dict[int, float]): 一个字典，键是偶次幂的阶数 (4, 6, 8...), 
                                             值是对应的非球面系数值。
                                             示例: {4: 1.2e-5, 6: -3.4e-8, 8: 5.6e-11}
        """
        surface = self.get_surface(surface_pos)
        
        for order, value in coefficients.items():
            # 必须是大于等于4的偶数阶
            if order < 4 or order % 2 != 0:
                logger.warning(f"跳过无效的非球面阶数: {order}。只接受>=4的偶数阶。")
                continue
            
            # 公式: param_index = (order / 2) - 1
            param_index = int(order / 2) - 1
            
            # Convert enum to integer and add the offset to avoid enum arithmetic issues
            param_column_int = int(self.ZOSAPI.Editors.LDE.SurfaceColumn.Par1) + param_index
            
            cell = surface.GetCellAt(param_column_int)
            cell.DoubleValue = value
            logger.info(f"  - 已设置表面 {surface_pos} 的 {order} 阶非球面系数 (Par{param_index + 1}) 为: {value}")
            
        logger.info(f"完成对表面 {surface_pos} 的非球面系数设置。")
    
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
    
    def set_variable(self, surface_pos: int, param_name: str, status: bool = True) -> bool:
        """
        将单个表面参数设置为变量（简化版）。

        Args:
            surface_pos: 表面位置, int
            param_name: 参数名称，支持 'radius', 'thickness', 'conic' 等
            status: 变量状态，True表示启用，False表示禁用
            
        Returns:
            是否设置成功
        """
        try:
            surface = self.get_surface(surface_pos)
            param_column_map = {
                'radius': self.ZOSAPI.Editors.LDE.SurfaceColumn.Radius,
                'thickness': self.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness,
                'conic': self.ZOSAPI.Editors.LDE.SurfaceColumn.Conic,
            }
            if param_name not in param_column_map:
                raise ValueError(f"不支持的参数名称: {param_name}")
            
            column_type = param_column_map[param_name]
            cell, is_var, _ = self.set_cell_as_variable(surface, column_type, f"表面 {surface_pos} 的 {param_name}")
            
            # 设置变量状态 (启用/禁用)
            if is_var and status is not None:
                solver_data = cell.GetSolveData()
                if solver_data:
                    solver_data.Status = status
                    cell.SetSolveData(solver_data)
            
            return is_var
        except Exception as e:
            logger.error(f"设置变量失败: {str(e)}")
            return False
        
    def set_cell_as_variable(self, surface: Any, column_type: Any, description: str = "") -> tuple:
        """
        将表面的单元格设置为变量 (简化版)。
        我们只使用最稳定可靠的 MakeSolveVariable 方法。
        """
        try:
            cell = surface.GetCellAt(int(column_type))
            cell.MakeSolveVariable()
            solver_data = cell.GetSolveData()
            solve_type = solver_data.Type if solver_data else None
            logger.info(f"成功将 {description} 设置为变量")
            return cell, True, solve_type
        except Exception as e:
            logger.error(f"将 {description} 设置为变量失败: {str(e)}")
            return None, False, None
    def _set_all_parameters_as_variables(self, param_name: str, start_surface: int = 1, end_surface: int = None, 
                                        exclude_surfaces: List[int] = None, status: bool = True) -> bool:
        """
        【私有辅助方法】统一处理所有批量设置变量的逻辑。
        """
        surface_count = self.LDE.NumberOfSurfaces
        if end_surface is None or end_surface >= surface_count:
            end_surface = surface_count - 1 # 不处理像面
        
        if exclude_surfaces is None:
            exclude_surfaces = []

        success_count = 0
        for i in range(start_surface, end_surface + 1):
            if i not in exclude_surfaces:
                try:
                    if self.set_variable(i, param_name, status=status):
                        success_count += 1
                except Exception as e:
                    # 某些表面可能没有特定参数（如非球面的conic），这是正常情况，记录为debug信息
                    logger.debug(f"为表面 {i} 设置 {param_name} 变量时跳过: {str(e)}")
        
        logger.info(f"完成了对参数 '{param_name}' 的批量变量设置，共成功设置 {success_count} 个表面。")
        return success_count > 0

    def set_all_radii_as_variables(self, start_surface: int = 1, end_surface: int = None, 
                                  exclude_surfaces: List[int] = None, status: bool = True) -> bool:
        """批量设置所有表面的曲率半径为变量。"""
        logger.info("开始批量设置曲率半径为变量...")
        # 尝试使用官方工具，如果失败则回退到手动循环
        try:
            tools = self.TheSystem.Tools
            tools.SetAllRadiiVariable()
            logger.info("已使用官方工具 'SetAllRadiiVariable'。")
            return True
        except Exception:
            logger.warning("官方工具 'SetAllRadiiVariable' 不可用或执行失败，将回退到逐个表面设置的方法。")
            return self._set_all_parameters_as_variables('radius', start_surface, end_surface, exclude_surfaces, status)

    def set_all_thickness_as_variables(self, start_surface: int = 1, end_surface: int = None, 
                                      exclude_surfaces: List[int] = None, status: bool = True) -> bool:
        """批量设置所有表面的厚度为变量。"""
        logger.info("开始批量设置厚度为变量...")
        return self._set_all_parameters_as_variables('thickness', start_surface, end_surface, exclude_surfaces, status)

    def set_all_conics_as_variables(self, start_surface: int = 1, end_surface: int = None, 
                                   exclude_surfaces: List[int] = None, status: bool = True) -> bool:
        """批量设置所有表面的锥面系数为变量。"""
        logger.info("开始批量设置锥面系数为变量...")
        return self._set_all_parameters_as_variables('conic', start_surface, end_surface, exclude_surfaces, status)
    
    def set_aspheric_variables(
        self, 
        surface_pos: int, 
        orders: List[int] = [4,6], 
        set_conic_as_variable: bool = False
    ):
        """
        精确地将指定阶数的非球面系数设置为变量，并可选择是否将锥面系数也设为变量。

        Args:
            surface_pos (int): 表面位置。
            orders (List[int], optional): 一个包含要设为变量的偶次幂阶数的列表。
                                          示例: [4, 6, 8] 只会将4阶、6阶、8阶系数设为变量。
                                          默认为 None，即不设置任何高阶系数。
            set_conic_as_variable (bool): 是否将该表面的锥面系数(Conic)也设置为变量。
        """
        surface = self.get_surface(surface_pos)
        
        # 1. 设置锥面系数变量
        if set_conic_as_variable:
            try:
                surface.ConicCell.MakeSolveVariable()
                logger.info(f"已将表面 {surface_pos} 的锥面系数设为变量。")
            except Exception as e:
                logger.error(f"为表面 {surface_pos} 设置锥面系数变量失败: {e}")

        # 2. 设置指定阶数的非球面系数变量
        if orders:
            for order in orders:
                # 必须是大于等于4的偶数阶
                if order < 4 or order % 2 != 0:
                    logger.warning(f"跳过无效的非球面阶数: {order}。只接受>=4的偶数阶。")
                    continue
                
                # 核心逻辑：将阶数映射到正确的Param#
                # 公式: param_index = (order / 2) - 1
                param_index = int(order / 2) - 1
                
                try:
                    # Convert enum to integer and add the offset to avoid enum arithmetic issues
                    param_column_int = int(self.ZOSAPI.Editors.LDE.SurfaceColumn.Par1) + param_index
                    cell = surface.GetCellAt(param_column_int)
                    cell.MakeSolveVariable()
                    logger.info(f"  - 已将表面 {surface_pos} 的 {order} 阶非球面系数 (Par{param_index + 1}) 设为变量。")
                except Exception as e:
                    logger.error(f"为表面 {surface_pos} 的 {order} 阶系数设置变量失败: {e}")




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
        
    def clear_all_variables(self) -> bool:
        """
        一键清除当前系统中所有表面上的所有优化变量。

        这个方法是对ZOS-API原生 "Remove All Variables" 工具的直接封装，
        是准备新一轮优化或清理设计时的常用功能。

        Returns:
            bool: 是否成功清除所有变量
        """
        try:
            tools = self.TheSystem.Tools
            if hasattr(tools, 'RemoveAllVariables'):
                tools.RemoveAllVariables()
                logger.info("已成功清除系统中所有的优化变量。")
                return True
            else:
                logger.error("当前ZOS-API版本不支持 'RemoveAllVariables' 工具。")
                return False
        except Exception as e:
            logger.error(f"清除所有变量时发生错误: {str(e)}")
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

    # def set_cell_as_variable(self, surface, column_type, description="") -> tuple:
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
        
    # === 求解器设置 ===
    def _get_cell(self, surface_pos: int, param_name: str) -> Any:
        """【私有辅助函数】获取指定表面和参数的单元格对象。"""
        surface = self.get_surface(surface_pos)
        param_column_map = {
            'radius': self.ZOSAPI.Editors.LDE.SurfaceColumn.Radius,
            'thickness': self.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness,
            'material': self.ZOSAPI.Editors.LDE.SurfaceColumn.Material,
            'conic': self.ZOSAPI.Editors.LDE.SurfaceColumn.Conic
        }
        if param_name.lower() not in param_column_map:
            raise ValueError(f"不支持的参数名称: {param_name}")
        
        column_enum = param_column_map[param_name.lower()]
        # Convert enum to integer value to ensure compatibility with GetCellAt
        try:
            return surface.GetCellAt(int(column_enum))
        except:
            # Fallback: try with enum directly (for compatibility with different ZOS-API versions)
            return surface.GetCellAt(column_enum)


    def set_pickup_solve(self, surface_pos: int, param_name: str, from_surface: int, scale: float = 1.0, offset: float = 0.0, from_column: str = None):
        """设置拾取 (Pickup) 求解器。"""
        cell = self._get_cell(surface_pos, param_name)
        solver = cell.CreateSolveType(self.ZOSAPI.Editors.SolveType.SurfacePickup)
        solver._S_SurfacePickup.Surface = from_surface
        solver._S_SurfacePickup.ScaleFactor = scale
        solver._S_SurfacePickup.Offset = offset
        if from_column:
            solver._S_SurfacePickup.Column = getattr(self.ZOSAPI.Editors.LDE.SurfaceColumn, from_column)
        cell.SetSolveData(solver)
        logger.info(f"成功为表面 {surface_pos} 的 '{param_name}' 设置了 Pickup 求解器。")

    def set_f_number_solve(self, surface_pos: int, f_number: float):
        """在曲率半径上设置 F/# 求解器。"""
        cell = self._get_cell(surface_pos, 'radius')
        solver = cell.CreateSolveType(self.ZOSAPI.Editors.SolveType.FNumber)
        solver._S_FNumber.FNumber = f_number
        cell.SetSolveData(solver)
        logger.info(f"成功为表面 {surface_pos} 的曲率半径设置了 FNumber 求解器。")

    def set_marginal_ray_angle_solve(self, surface_pos: int, angle: float):
        """在厚度上设置边际光线角 (Marginal Ray Angle) 求解器。"""
        cell = self._get_cell(surface_pos, 'thickness')
        solver = cell.CreateSolveType(self.ZOSAPI.Editors.SolveType.MarginalRayAngle)
        solver._S_MarginalRayAngle.Angle = angle
        cell.SetSolveData(solver)
        logger.info(f"成功为表面 {surface_pos} 的厚度设置了 MarginalRayAngle 求解器。")

    def set_substitute_solve(self, surface_pos: int, catalog: str):
        """在材料单元格上设置替代 (Substitute) 求解器。"""
        surface = self.get_surface(surface_pos)
        cell = surface.MaterialCell
        solver = cell.CreateSolveType(self.ZOSAPI.Editors.SolveType.MaterialSubstitute)
        solver._S_MaterialSubstitute.Catalog = catalog
        cell.SetSolveData(solver)
        logger.info(f"成功为表面 {surface_pos} 的材料设置了 Substitute 求解器，使用 '{catalog}' 库。")
            
    def clear_solve(self, surface_pos: int, param_name: str):
        """清除指定参数上的求解器。"""
        cell = self._get_cell(surface_pos, param_name)
        cell.ClearSolve()
        logger.info(f"已清除表面 {surface_pos} 的 '{param_name}' 上的求解器。")


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
