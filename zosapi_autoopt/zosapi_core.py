"""
Zemax OpticStudio Python API 核心模块
提供统一的初始化、连接管理和基础操作功能
Author: allin-love
Date: 2025-06-29
"""

import clr
import os
import winreg
from typing import Optional, Union
import logging
from .config import LOG_SETTINGS

# 配置日志 - 使用配置文件中的设置
log_level = getattr(logging, LOG_SETTINGS.get("level", "WARNING").upper())
logging.basicConfig(level=log_level, format=LOG_SETTINGS.get("format", "%(levelname)s:%(name)s:%(message)s"))
logger = logging.getLogger(__name__)


class ZOSAPIException(Exception):
    """ZOSAPI 基础异常类"""
    pass


class LicenseException(ZOSAPIException):
    """许可证异常"""
    pass


class ConnectionException(ZOSAPIException):
    """连接异常"""
    pass


class InitializationException(ZOSAPIException):
    """初始化异常"""
    pass


class SystemNotPresentException(ZOSAPIException):
    """系统不存在异常"""
    pass


class ZOSAPIManager:
    """
    Zemax OpticStudio API 管理器
    提供统一的初始化、连接管理和基础操作功能
    """
    
    def __init__(self, custom_path: Optional[str] = None, auto_connect: bool = True):
        """
        初始化 ZOSAPI 管理器
        
        Args:
            custom_path: 自定义 OpticStudio 安装路径
            auto_connect: 是否自动连接到 OpticStudio
        """
        # 初始化属性
        self.TheApplication = None
        self.TheConnection = None
        self.TheSystem = None
        self.ZOSAPI = None
        self.is_connected = False
        
        if auto_connect:
            self.connect(custom_path)
    
    def connect(self, custom_path: Optional[str] = None) -> bool:
        """
        连接到 Zemax OpticStudio
        
        Args:
            custom_path: 自定义 OpticStudio 安装路径
            
        Returns:
            bool: 连接是否成功
        """
        try:
            logger.info("开始初始化 ZOSAPI 连接...")
            
            # 步骤1: 获取 NetHelper 路径并添加引用
            self._setup_nethelper()
            
            # 步骤2: 初始化 ZOSAPI
            self._initialize_zosapi(custom_path)
            
            # 步骤3: 创建连接
            self._create_connection()
            
            # 步骤4: 创建应用程序实例
            self._create_application()
            
            # 步骤5: 验证许可证
            self._verify_license()
            
            # 步骤6: 获取主系统
            self._get_primary_system()
            
            self.is_connected = True
            logger.info("ZOSAPI 连接成功!")
            return True
            
        except Exception as e:
            logger.error(f"ZOSAPI 连接失败: {str(e)}")
            self.disconnect()
            return False
    
    def _setup_nethelper(self) -> None:
        """设置 NetHelper"""
        try:
            # 从注册表获取 Zemax 安装路径
            aKey = winreg.OpenKey(
                winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER),
                r"Software\Zemax",
                0,
                winreg.KEY_READ
            )
            zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
            NetHelper = os.path.join(zemaxData[0], r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
            winreg.CloseKey(aKey)
            
            if not os.path.exists(NetHelper):
                raise InitializationException(f"NetHelper 文件不存在: {NetHelper}")
            
            clr.AddReference(NetHelper)
            import ZOSAPI_NetHelper
            self._nethelper = ZOSAPI_NetHelper
            
        except Exception as e:
            raise InitializationException(f"设置 NetHelper 失败: {str(e)}")
    
    def _initialize_zosapi(self, custom_path: Optional[str] = None) -> None:
        """初始化 ZOSAPI"""
        try:
            # 初始化 ZOSAPI
            if custom_path is None:
                isInitialized = self._nethelper.ZOSAPI_Initializer.Initialize()
            else:
                isInitialized = self._nethelper.ZOSAPI_Initializer.Initialize(custom_path)
            
            # 获取 ZOS 根目录
            if isInitialized:
                zos_dir = self._nethelper.ZOSAPI_Initializer.GetZemaxDirectory()
            else:
                # 尝试默认路径作为备选
                default_paths = [
                    r"C:\Program Files\ANSYS Inc\v242\Zemax OpticStudio",
                    r"C:\Program Files\Zemax OpticStudio",
                    r"C:\Program Files (x86)\Zemax OpticStudio"
                ]
                
                zos_dir = None
                for path in default_paths:
                    if os.path.exists(path):
                        try:
                            isInitialized = self._nethelper.ZOSAPI_Initializer.Initialize(path)
                            if isInitialized:
                                zos_dir = self._nethelper.ZOSAPI_Initializer.GetZemaxDirectory()
                                break
                        except:
                            continue
                
                if not isInitialized or zos_dir is None:
                    raise InitializationException("无法定位 Zemax OpticStudio，请尝试指定自定义路径")
            
            # 添加 ZOS-API 引用
            clr.AddReference(os.path.join(zos_dir, "ZOSAPI.dll"))
            clr.AddReference(os.path.join(zos_dir, "ZOSAPI_Interfaces.dll"))
            import ZOSAPI
            self.ZOSAPI = ZOSAPI
            
        except Exception as e:
            raise InitializationException(f"初始化 ZOSAPI 失败: {str(e)}")
    
    def _create_connection(self) -> None:
        """创建连接"""
        try:
            self.TheConnection = self.ZOSAPI.ZOSAPI_Connection()
            if self.TheConnection is None:
                raise ConnectionException("无法创建到 ZOSAPI 的 .NET 连接")
        except Exception as e:
            raise ConnectionException(f"创建连接失败: {str(e)}")
    
    def _create_application(self) -> None:
        """创建应用程序实例"""
        try:
            self.TheApplication = self.TheConnection.CreateNewApplication()
            if self.TheApplication is None:
                raise InitializationException("无法获取 ZOSAPI 应用程序实例")
        except Exception as e:
            raise InitializationException(f"创建应用程序实例失败: {str(e)}")
    
    def _verify_license(self) -> None:
        """验证许可证"""
        try:
            if not self.TheApplication.IsValidLicenseForAPI:
                raise LicenseException("许可证对 ZOSAPI 使用无效")
        except Exception as e:
            raise LicenseException(f"许可证验证失败: {str(e)}")
    
    def _get_primary_system(self) -> None:
        """获取主系统"""
        try:
            self.TheSystem = self.TheApplication.PrimarySystem
            if self.TheSystem is None:
                raise SystemNotPresentException("无法获取主系统")
        except Exception as e:
            raise SystemNotPresentException(f"获取主系统失败: {str(e)}")
    
    def disconnect(self) -> None:
        """断开连接并清理资源"""
        try:
            if self.TheApplication is not None:
                self.TheApplication.CloseApplication()
                self.TheApplication = None
            
            self.TheConnection = None
            self.TheSystem = None
            self.is_connected = False
            
            logger.info("ZOSAPI 连接已断开")
            
        except Exception as e:
            logger.error(f"断开连接时发生错误: {str(e)}")
    
    def close(self) -> None:
        """
        关闭连接（disconnect的别名）
        """
        self.disconnect()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()
    
    def __del__(self):
        """析构函数"""
        self.disconnect()
    
    # === 文件操作方法 ===
    
    def open_file(self, filepath: str, save_if_needed: bool = False) -> bool:
        """
        打开光学系统文件
        
        Args:
            filepath: 文件路径
            save_if_needed: 如果需要是否保存当前文件
            
        Returns:
            bool: 是否成功打开文件
            
        Raises:
            SystemNotPresentException: 系统不存在
        """
        if self.TheSystem is None:
            raise SystemNotPresentException("无法获取主系统")
        
        try:
            # 确保路径存在
            if not os.path.exists(filepath):
                logger.error(f"文件不存在: {filepath}")
                return False
            
            # 使用绝对路径
            abs_filepath = os.path.abspath(filepath)
            logger.info(f"尝试加载文件: {abs_filepath}")
            
            # 调用LoadFile方法
            result = self.TheSystem.LoadFile(abs_filepath, save_if_needed)
            
            # 检查结果（某些版本的LoadFile会返回状态）
            if hasattr(result, 'Success') and not result.Success:
                logger.error(f"文件加载失败: {result.ErrorMessage if hasattr(result, 'ErrorMessage') else '未知错误'}")
                return False
            
            logger.info(f"成功打开文件: {abs_filepath}")
            return True
            
        except Exception as e:
            logger.error(f"打开文件失败: {str(e)}")
            return False
    
    def close_file(self, save: bool = False) -> None:
        """
        关闭当前文件
        
        Args:
            save: 是否保存文件
            
        Raises:
            SystemNotPresentException: 系统不存在
        """
        if self.TheSystem is None:
            raise SystemNotPresentException("无法获取主系统")
        
        try:
            self.TheSystem.Close(save)
            logger.info("文件已关闭")
        except Exception as e:
            logger.error(f"关闭文件失败: {str(e)}")
            raise
    
    def new_file(self) -> None:
        """
        创建新文件
        
        Raises:
            SystemNotPresentException: 系统不存在
        """
        if self.TheSystem is None:
            raise SystemNotPresentException("无法获取主系统")
        
        try:
            self.TheSystem.New(False)  # False表示不显示向导
            logger.info("已创建新文件")
        except Exception as e:
            logger.error(f"创建新文件失败: {str(e)}")
            raise
    
    def save_file(self, filepath: Optional[str] = None) -> None:
        """
        保存文件
        
        Args:
            filepath: 保存路径，如果为None则保存到当前路径
        """
        if self.TheSystem is None:
            raise SystemNotPresentException("无法获取主系统")
        
        try:
            if filepath is None:
                self.TheSystem.Save()
            else:
                self.TheSystem.SaveAs(filepath)
            logger.info(f"文件已保存: {filepath or '当前路径'}")
        except Exception as e:
            logger.error(f"保存文件失败: {str(e)}")
            raise
    
    # === 信息获取方法 ===
    
    def get_samples_dir(self) -> str:
        """获取样本文件目录"""
        if self.TheApplication is None:
            raise InitializationException("无法获取 ZOSAPI 应用程序实例")
        return self.TheApplication.SamplesDir
    
    def get_license_type(self) -> str:
        """获取许可证类型"""
        if self.TheApplication is None:
            raise InitializationException("无法获取 ZOSAPI 应用程序实例")
        
        license_status = self.TheApplication.LicenseStatus
        if license_status == self.ZOSAPI.LicenseStatusType.PremiumEdition:
            return "Premium"
        elif license_status == self.ZOSAPI.LicenseStatusType.ProfessionalEdition:
            return "Professional"
        elif license_status == self.ZOSAPI.LicenseStatusType.StandardEdition:
            return "Standard"
        else:
            return "Invalid"
    
    def get_system_info(self) -> dict:
        """获取系统信息"""
        if self.TheSystem is None:
            raise SystemNotPresentException("无法获取主系统")
        
        try:
            # 安全地获取系统信息，处理可能不存在的属性
            info = {}
            
            # 基本信息
            try:
                info["title"] = str(self.TheSystem.SystemData.Title) if hasattr(self.TheSystem.SystemData, 'Title') else "未知"
            except:
                info["title"] = "未知"
            
            # 孔径信息
            try:
                info["aperture_type"] = str(self.TheSystem.SystemData.Aperture.ApertureType)
                info["aperture_value"] = float(self.TheSystem.SystemData.Aperture.ApertureValue)
            except:
                info["aperture_type"] = "未知"
                info["aperture_value"] = 0.0
            
            # 视场信息
            try:
                info["field_type"] = str(self.TheSystem.SystemData.Fields.GetFieldType())
                info["field_count"] = self.TheSystem.SystemData.Fields.NumberOfFields
            except:
                info["field_type"] = "未知"
                info["field_count"] = 0
            
            # 波长信息
            try:
                info["wavelength_count"] = self.TheSystem.SystemData.Wavelengths.NumberOfWavelengths
            except:
                info["wavelength_count"] = 0
            
            # 面数信息
            try:
                info["surface_count"] = self.TheSystem.LDE.NumberOfSurfaces
            except:
                info["surface_count"] = 0
            
            return info
            
        except Exception as e:
            logger.error(f"获取系统信息失败: {str(e)}")
            return {
                "title": "未知",
                "aperture_type": "未知",
                "aperture_value": 0.0,
                "field_type": "未知",
                "field_count": 0,
                "wavelength_count": 0,
                "surface_count": 0
            }


# === 便捷函数 ===

def create_zosapi_manager(custom_path: Optional[str] = None) -> ZOSAPIManager:
    """
    创建 ZOSAPI 管理器的便捷函数
    
    Args:
        custom_path: 自定义 OpticStudio 安装路径
        
    Returns:
        ZOSAPIManager 实例
    """
    return ZOSAPIManager(custom_path=custom_path)


def quick_connect(custom_path: Optional[str] = None) -> ZOSAPIManager:
    """
    快速连接的便捷函数
    
    Args:
        custom_path: 自定义 OpticStudio 安装路径
        
    Returns:
        已连接的 ZOSAPIManager 实例
    """
    manager = ZOSAPIManager(custom_path=custom_path, auto_connect=True)
    return manager
