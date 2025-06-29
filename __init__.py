"""
Zemax OpticStudio Python API 封装库
提供简化的接口用于光学分析和优化

模块说明:
- zosapi_core: 核心连接和管理功能
- zosapi_utils: 数据处理和转换工具
- zosapi_plotting: 绘图和可视化功能
- zosapi_analysis: 光学分析功能
- example_usage: 使用示例

Author: Your Name
Date: 2025-06-29
Version: 1.0.0
"""

from zosapi_core import ZOSAPIManager, quick_connect, create_zosapi_manager
from zosapi_analysis import ZOSAnalyzer, BatchAnalyzer
from zosapi_plotting import ZOSPlotter
from zosapi_utils import ZOSDataProcessor

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = [
    # 核心类
    "ZOSAPIManager",
    "ZOSAnalyzer", 
    "BatchAnalyzer",
    "ZOSPlotter",
    "ZOSDataProcessor",
    
    # 便捷函数
    "quick_connect",
    "create_zosapi_manager"
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
