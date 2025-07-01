"""
Zemax OpticStudio Python API 封装库
提供简化的接口用于光学分析和优化

模块说明:
- zosapi_core: 核心连接和管理功能
- zosapi_utils: 数据处理和转换工具
- zosapi_plotting: 绘图和可视化功能
- zosapi_analysis: 光学分析功能

Author: allin-love
Date: 2025-06-29
Version: 1.0.0
"""

from zosapi_autoopt.zosapi_core import ZOSAPIManager, create_zosapi_manager
from zosapi_autoopt.zosapi_analysis import ZOSAnalyzer, BatchAnalyzer
from zosapi_autoopt.zosapi_plotting import plot_spots, plot_rayfan, plot_mtf, plot_field_curvature_distortion, analyze_and_plot_system
from zosapi_autoopt.zosapi_utils import ZOSDataProcessor
from zosapi_autoopt import get_version, get_info

__version__ = "1.0.0"
__author__ = "allin-love"
__all__ = [
    # 核心类
    "ZOSAPIManager",
    "ZOSAnalyzer", 
    "BatchAnalyzer",
    "ZOSDataProcessor",
    
    # 便捷函数
    "create_zosapi_manager",
    
    # 绘图函数
    "plot_spots", 
    "plot_rayfan", 
    "plot_mtf", 
    "plot_field_curvature_distortion",
    "analyze_and_plot_system",
    
    # 工具函数
    "get_version",
    "get_info"
]


