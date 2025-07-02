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
    
    def set_aperture(self, aperture_type: str, value: float, stop_surface: int = 0):
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
