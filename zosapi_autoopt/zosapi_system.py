"""
Zemax OpticStudio Python API 系统参数设置模块
提供孔径、波长、视场等系统参数的设置功能
Author: allin-love
Date: 2025-07-01
"""

import logging
from typing import List, Tuple, Optional, Union
from .config import LOG_SETTINGS

# 配置日志
log_level = getattr(logging, LOG_SETTINGS.get("level", "WARNING").upper())
logger = logging.getLogger(__name__)


class SystemParameterManager:
    """
    系统参数管理器
    提供孔径、波长、视场等系统参数的设置功能
    """
    
    def __init__(self, zos_manager):
        """
        初始化系统参数管理器
        
        Args:
            zos_manager: ZOSAPIManager 实例
        """
        self.zos_manager = zos_manager
        self.TheSystem = zos_manager.TheSystem
        self.ZOSAPI = zos_manager.ZOSAPI
        
    @property
    def system_data(self):
        """获取系统数据对象"""
        return self.TheSystem.SystemData
    
    # === 孔径设置 ===

    def set_aperture(self, aperture_type: str, value: float, stop_surface: int = 0, clear_aperture_margin: float = None):
        """
        设置系统孔径
        
        Args:
            aperture_type: 孔径类型 ('entrance_pupil_diameter', 'image_space_fnum', 'object_space_na', 'float_by_stop_size', 'paraxial_working_fnum', 'object_cone_angle')
            value: 孔径值
            stop_surface: 光阑面序号 (默认为0，自动选择)
        """
        try:
            aperture = self.system_data.Aperture
            
            # 映射孔径类型
            aperture_type_map = {
                'entrance_pupil_diameter': self.ZOSAPI.SystemData.ZemaxApertureType.EntrancePupilDiameter,
                'image_space_fnum': self.ZOSAPI.SystemData.ZemaxApertureType.ImageSpaceFNum,
                'object_space_na': self.ZOSAPI.SystemData.ZemaxApertureType.ObjectSpaceNA,
                'float_by_stop_size': self.ZOSAPI.SystemData.ZemaxApertureType.FloatByStopSize,
                'paraxial_working_fnum': self.ZOSAPI.SystemData.ZemaxApertureType.ParaxialWorkingFNum,
                'object_cone_angle': self.ZOSAPI.SystemData.ZemaxApertureType.ObjectConeAngle
            }
            
            if aperture_type not in aperture_type_map:
                raise ValueError(f"不支持的孔径类型: {aperture_type}")
            
            aperture.ApertureType = aperture_type_map[aperture_type]
            aperture.ApertureValue = value
            
            if stop_surface > 0:
                aperture.StopSurface = stop_surface

            if clear_aperture_margin is not None:
            # 这个属性用于设置净口径余量
                aperture.SemiDiameterMargin = clear_aperture_margin


            logger.info(f"设置孔径: 类型={aperture_type}, 值={value}, 光阑面={stop_surface}")
            

        except Exception as e:
            logger.error(f"设置孔径失败: {str(e)}")
            raise
    
    def get_aperture_info(self) -> dict:
        """
        获取当前孔径信息
        
        Returns:
            包含孔径信息的字典
        """
        try:
            aperture = self.system_data.Aperture
            info = {
                'type': str(aperture.ApertureType),
                'value': aperture.ApertureValue
            }
            
            # 尝试获取光阑面信息（如果存在）
            try:
                info['stop_surface'] = aperture.StopSurface
            except:
                info['stop_surface'] = 0
                
            return info
        except Exception as e:
            logger.error(f"获取孔径信息失败: {str(e)}")
            return {}
    
    # === 波长设置 ===
    
    def set_wavelength_preset(self, preset: str):
        """
        设置波长预设
        
        Args:
            preset: 波长预设类型 ('d_0p587', 'f_0p486', 'c_0p656', 'visible', 'near_ir', etc.)
        """
        try:
            wavelengths = self.system_data.Wavelengths
            
            # 映射波长预设
            preset_map = {
                'd_0p587': self.ZOSAPI.SystemData.WavelengthPreset.d_0p587,
                'f_0p486': self.ZOSAPI.SystemData.WavelengthPreset.F_0p486,
                'c_0p656': self.ZOSAPI.SystemData.WavelengthPreset.C_0p656,
                'fdc_visible': self.ZOSAPI.SystemData.WavelengthPreset.FdC_Visible,
                'fpec_visible': self.ZOSAPI.SystemData.WavelengthPreset.FpeCp_Visible,
                'hene_0p6328': self.ZOSAPI.SystemData.WavelengthPreset.HeNe_0p6328
            }
            
            if preset not in preset_map:
                raise ValueError(f"不支持的波长预设: {preset}")
            
            wavelengths.SelectWavelengthPreset(preset_map[preset])
            logger.info(f"设置波长预设: {preset}")
            
        except Exception as e:
            logger.error(f"设置波长预设失败: {str(e)}")
            raise
    
    def add_wavelength(self, wavelength: float, weight: float = 1.0):
        """
        添加波长
        
        Args:
            wavelength: 波长值 (微米)
            weight: 权重
        """
        try:
            wavelengths = self.system_data.Wavelengths
            new_wavelength = wavelengths.AddWavelength(wavelength, weight)
            logger.info(f"添加波长: {wavelength} μm, 权重: {weight}")
            return new_wavelength
            
        except Exception as e:
            logger.error(f"添加波长失败: {str(e)}")
            raise

    def set_wavelengths(self, wavelength_list: List[float], weights: List[float] = None):
        """
        设置系统波长
        
        Args:
            wavelength_list: 波长列表 (纳米)
            weights: 各波长的权重列表，默认每个波长权重为1.0
        """
        try:
            # 获取波长对象
            wavelengths = self.system_data.Wavelengths
            
            # 先记录当前波长数量
            current_wl_count = wavelengths.NumberOfWavelengths
            
            # 清除现有波长
            if current_wl_count > 0:
                # 只保留一个波长，然后使用它
                while wavelengths.NumberOfWavelengths > 1:
                    wavelengths.RemoveWavelength(wavelengths.NumberOfWavelengths)
                
                # 使用第一个波长
                first_wl = wavelengths.GetWavelength(1)
                
                # 添加新的波长
                if weights is None:
                    weights = [1.0] * len(wavelength_list)
                    
                for i, wl in enumerate(wavelength_list):
                    wl_microns = wl / 1000.0  # 转换为微米
                    weight = weights[i] if i < len(weights) else 1.0
                    
                    # 如果是第一个波长，修改现有波长而不是添加
                    if i == 0:
                        first_wl.Wavelength = wl_microns
                        first_wl.Weight = weight
                    else:
                        self.add_wavelength(wl_microns, weight)
            else:
                # 没有现有波长，直接添加新的
                if weights is None:
                    weights = [1.0] * len(wavelength_list)
                    
                for i, wl in enumerate(wavelength_list):
                    wl_microns = wl / 1000.0  # 转换为微米
                    weight = weights[i] if i < len(weights) else 1.0
                    self.add_wavelength(wl_microns, weight)
                
            # 设置主波长（波长数据可能没有SetPrimary方法，尝试使用对应属性）
            if len(wavelength_list) > 0:
                try:
                    # 尝试使用SetPrimary方法
                    wavelengths.SetPrimary(1)
                except:
                    try:
                        # 尝试设置Primary属性
                        wavelengths.Primary = 1
                    except:
                        # 如果都失败，只记录警告
                        logger.warning("无法设置主波长")
                
            logger.info(f"设置了 {len(wavelength_list)} 个波长")
            return True
            
        except Exception as e:
            logger.error(f"设置波长失败: {str(e)}")
            return False
    
    def get_wavelength_info(self) -> List[dict]:
        """
        获取波长信息
        
        Returns:
            波长信息列表
        """
        try:
            wavelengths = self.system_data.Wavelengths
            wave_info = []
            
            for i in range(1, wavelengths.NumberOfWavelengths + 1):
                wave = wavelengths.GetWavelength(i)
                wave_info.append({
                    'index': i,
                    'wavelength': wave.Wavelength,
                    'weight': wave.Weight,
                    'is_primary': wave.IsPrimary
                })
            
            return wave_info
            
        except Exception as e:
            logger.error(f"获取波长信息失败: {str(e)}")
            return []
    
    # === 视场设置 ===
    
    def set_field_type(self, field_type: str):
        """
        设置视场类型
        
        Args:
            field_type: 视场类型 ('angle', 'object_height', 'paraxial_image_height', 'real_image_height')
        """
        try:
            fields = self.system_data.Fields
            
            # 映射视场类型
            field_type_map = {
                'angle': self.ZOSAPI.SystemData.FieldType.Angle,
                'object_height': self.ZOSAPI.SystemData.FieldType.ObjectHeight,
                'paraxial_image_height': self.ZOSAPI.SystemData.FieldType.ParaxialImageHeight,
                'real_image_height': self.ZOSAPI.SystemData.FieldType.RealImageHeight
            }
            
            if field_type not in field_type_map:
                raise ValueError(f"不支持的视场类型: {field_type}")
            
            fields.SetFieldType(field_type_map[field_type])
            logger.info(f"设置视场类型: {field_type}")
            
        except Exception as e:
            logger.error(f"设置视场类型失败: {str(e)}")
            raise
    
    def add_field(self, x: float, y: float, weight: float = 1.0, vdx: float = 0.0, vdy: float = 0.0, vcx: float = 0.0, vcy: float = 0.0, van: float = 0.0):
        """
        添加视场点
        
        Args:
            x: X坐标
            y: Y坐标
            weight: 权重
            vdx: X方向渐晕系数
            vdy: Y方向渐晕系数
            vcx: X方向渐晕中心
            vcy: Y方向渐晕中心
            van: 渐晕角度
        """
        try:
            fields = self.system_data.Fields
            new_field = fields.AddField(x, y, weight)
            
            # 设置渐晕参数
            if vdx != 0.0:
                new_field.VDX = vdx
            if vdy != 0.0:
                new_field.VDY = vdy
            if vcx != 0.0:
                new_field.VCX = vcx
            if vcy != 0.0:
                new_field.VCY = vcy
            if van != 0.0:
                new_field.VAN = van
            
            logger.info(f"添加视场点: ({x}, {y}), 权重: {weight}")
            return new_field
            
        except Exception as e:
            logger.error(f"添加视场点失败: {str(e)}")
            raise
    
    def set_field(self, field_type: str, field_points: List[Tuple[float, float]], weights: List[float] = None):
        """
        设置系统视场
        
        Args:
            field_type: 视场类型 ('angle', 'object_height', 'paraxial_image_height', 'real_image_height')
            field_points: 视场点列表，每个点是一个 (x, y) 坐标元组
            weights: 各视场点的权重列表，默认每个点权重为1.0
        """
        try:
            # 设置视场类型
            self.set_field_type(field_type)
            
            # 清除所有现有视场点
            fields = self.system_data.Fields
            
            # 先记录当前视场数量
            current_field_count = fields.NumberOfFields
            
            # 清除现有视场
            if current_field_count > 0:
                # 只保留一个视场点，然后使用它
                while fields.NumberOfFields > 1:
                    fields.RemoveField(fields.NumberOfFields)
                
                # 使用第一个视场点
                first_field = fields.GetField(1)
                
                # 添加新的视场点
                if weights is None:
                    weights = [1.0] * len(field_points)
                    
                for i, (x, y) in enumerate(field_points):
                    weight = weights[i] if i < len(weights) else 1.0
                    # 如果是第一个点，修改现有点而不是添加
                    if i == 0:
                        first_field.X = x
                        first_field.Y = y
                        first_field.Weight = weight
                    else:
                        self.add_field(x, y, weight)
            else:
                # 没有现有视场点，直接添加新的
                if weights is None:
                    weights = [1.0] * len(field_points)
                    
                for i, (x, y) in enumerate(field_points):
                    weight = weights[i] if i < len(weights) else 1.0
                    self.add_field(x, y, weight)
                
            logger.info(f"设置了 {len(field_points)} 个视场点")
            return True
            
        except Exception as e:
            logger.error(f"设置视场失败: {str(e)}")
            return False
    
    def get_field_info(self) -> List[dict]:
        """
        获取视场信息
        
        Returns:
            视场信息列表
        """
        try:
            fields = self.system_data.Fields
            field_info = []
            
            for i in range(1, fields.NumberOfFields + 1):
                field = fields.GetField(i)
                field_info.append({
                    'index': i,
                    'x': field.X,
                    'y': field.Y,
                    'weight': field.Weight,
                    'vdx': field.VDX,
                    'vdy': field.VDY,
                    'vcx': field.VCX,
                    'vcy': field.VCY,
                    'van': field.VAN
                })
            
            return field_info
            
        except Exception as e:
            logger.error(f"获取视场信息失败: {str(e)}")
            return []
    
    # === 环境设置 ===
    
    def set_environment(self, temperature: float = 20.0, pressure: float = 1.0, adjust_index: bool = True):
        """
        设置环境参数
        
        Args:
            temperature: 温度 (摄氏度)
            pressure: 压力 (大气压)
            adjust_index: 是否调整折射率
        """
        try:
            environment = self.system_data.Environment
            environment.Temperature = temperature
            environment.Pressure = pressure
            environment.AdjustIndexToEnvironment = adjust_index
            
            logger.info(f"设置环境参数: 温度={temperature}°C, 压力={pressure}atm, 调整折射率={adjust_index}")
            
        except Exception as e:
            logger.error(f"设置环境参数失败: {str(e)}")
            raise
    
    # === 视场清除方法 ===
    
    def clear_fields(self):
        """
        清除所有视场点，仅保留第一个视场点并重置其参数
        """
        try:
            fields = self.system_data.Fields
            # 删除除第一个视场外的所有视场
            while fields.NumberOfFields > 1:
                fields.DeleteFieldAt(fields.NumberOfFields)
            
            # 重置第一个视场
            first_field = fields.GetField(1)
            first_field.X = 0
            first_field.Y = 0
            first_field.Weight = 1.0
            
            logger.info("清除视场点完成")
            
        except Exception as e:
            logger.error(f"清除视场点失败: {str(e)}")
            raise

    def add_catalog(self, catalog_name: str):
        """
        向系统中添加指定的材料库。

        Args:
            catalog_name (str): 要添加的材料库名称。
        
        常用材料库 (Common catalogs include):
            - "SCHOTT"      (德国肖特)
            - "CDGM"        (中国成都光明)
            - "HOYA"        (日本豪雅)
            - "OHARA"       (日本小原)
            - "SUMITA"      (日本住田)
            - "CORNING"     (美国康宁)
            - "HIKARI"      (日本光)
            - "NHG"         (Newport)
            - "INFRARED"    (红外材料)
            - "UV"          (紫外材料)
            - "MISC"        (其他杂项材料)
            - "PLASTIC"     (塑料材料)
        """
        try:
            catalogs = self.system_data.MaterialCatalogs
            catalogs.AddCatalog(catalog_name)
            logger.info(f"成功添加材料库: {catalog_name}")
        except Exception as e:
            logger.error(f"添加材料库 '{catalog_name}' 失败: {str(e)}")
            raise

    def remove_catalog(self, catalog_name: str):
        """
        从系统中移除指定的材料库。
        Args:
            catalog_name (str): 要移除的材料库名称。
        """
        try:
            catalogs = self.system_data.MaterialCatalogs
            catalogs.RemoveCatalog(catalog_name)
            logger.info(f"成功移除材料库: {catalog_name}")
        except Exception as e:
            logger.error(f"移除材料库 '{catalog_name}' 失败: {str(e)}")
            raise
            
    def get_catalogs(self) -> List[str]:
        """
        获取当前系统中已加载的所有材料库列表。
        注意: ZOS-API本身不直接支持获取列表，此功能受限。
        Returns:
            List[str]: 已加载材料库的名称列表 (当前返回空列表)。
        """
        try:
            catalogs = self.system_data.MaterialCatalogs
            logger.warning("ZOS-API不直接支持获取已加载材料库的列表。")
            return []
        except Exception as e:
            logger.error(f"获取材料库列表失败: {str(e)}")
            return []

    def get_system_summary(self) -> dict:
        """
        获取系统参数摘要
        
        Returns:
            系统参数摘要字典
        """
        try:
            summary = {
                'aperture': self.get_aperture_info(),
                'wavelengths': self.get_wavelength_info(),
                'fields': self.get_field_info(),
                'environment': {
                    'temperature': self.system_data.Environment.Temperature,
                    'pressure': self.system_data.Environment.Pressure,
                    'adjust_index': self.system_data.Environment.AdjustIndexToEnvironment
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"获取系统摘要失败: {str(e)}")
            return {}


# === 便捷函数 ===

def create_system_parameter_manager(zos_manager) -> SystemParameterManager:
    """
    创建系统参数管理器的便捷函数
    
    Args:
        zos_manager: ZOSAPIManager 实例
        
    Returns:
        SystemParameterManager 实例
    """
    return SystemParameterManager(zos_manager)
