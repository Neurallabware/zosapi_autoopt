"""
Zemax OpticStudio Python API 封装库
提供简化的接口用于光学分析和优化

模块说明:
- zosapi_core: 核心连接和管理功能
- zosapi_utils: 数据处理和转换工具
- zosapi_plotting: 绘图和可视化功能
- zosapi_analysis: 光学分析功能
- example_usage: 使用示例

Author: allin-love
Date: 2025-06-29
Version: 1.0.0
"""

from .zosapi_core import ZOSAPIManager, create_zosapi_manager
from .zosapi_analysis import ZOSAnalyzer, BatchAnalyzer
# 由于没有ZOSPlotter类，因此从plot_spots开始导入重要的绘图函数
from .zosapi_plotting import ZOSPlotter
from .zosapi_utils import ZOSDataProcessor
from .zosapi_layout import ZOSLayoutAnalyzer
from .zosapi_system import SystemParameterManager, create_system_parameter_manager
from .zosapi_lde import LensDesignManager, create_lens_design_manager
from .merit_function import MeritFunctionEditor

__version__ = "1.0.0"
__author__ = "allin-love"
__all__ = [
    # 核心类
    "ZOSAPIManager",
    "ZOSAnalyzer", 
    "BatchAnalyzer",
    "ZOSPlotter",
    "ZOSDataProcessor",
    "ZOSLayoutAnalyzer",
    "SystemParameterManager",
    "LensDesignManager",
    "MeritFunctionEditor",
    
    # 便捷函数
    "create_zosapi_manager",
    "create_system_parameter_manager",
    "create_lens_design_manager",
    
]

def get_version():
    """获取版本信息"""
    return __version__

def get_info():
    """获取库信息"""
    return {
        "name": "Zemax OpticStudio Python API 封装库",
        "version": __version__,
        "author": __author__,
        "description": "提供简化的接口用于光学分析和优化"
    }
