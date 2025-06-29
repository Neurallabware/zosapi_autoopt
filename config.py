"""
Zemax OpticStudio Python API 配置文件
包含常用的设置和参数
"""

import os

# === 路径配置 ===

# 默认的 Zemax OpticStudio 安装路径候选
DEFAULT_ZEMAX_PATHS = [
    r"C:\Program Files\ANSYS Inc\v242\Zemax OpticStudio",
    r"C:\Program Files\Zemax OpticStudio",
    r"C:\Program Files (x86)\Zemax OpticStudio",
    r"C:\Program Files\ANSYS Inc\v241\Zemax OpticStudio",
    r"C:\Program Files\ANSYS Inc\v232\Zemax OpticStudio"
]

# 输出目录
OUTPUT_DIR = "zosapi_output"

# 示例文件路径
SAMPLE_FILES = {
    "cooke_triplet": r"C:\Program Files\ANSYS Inc\v242\Zemax OpticStudio\Samples\Sequential\Objectives\Cooke 40 degree field.zos",
    "double_gauss": r"C:\Program Files\ANSYS Inc\v242\Zemax OpticStudio\Samples\Sequential\Objectives\Double Gauss 28 degree field.zos",
    "singlet": r"C:\Program Files\ANSYS Inc\v242\Zemax OpticStudio\Samples\Sequential\Objectives\Singlet.zos"
}

# === 分析配置 ===

# 默认分析参数
DEFAULT_ANALYSIS_SETTINGS = {
    "spot_diagram": {
        "ray_density": 3,
        "field_index": 1,
        "wavelength_index": 1
    },
    "wavefront": {
        "sampling": 32,
        "field_index": 1,
        "wavelength_index": 1
    },
    "mtf": {
        "max_frequency": 100.0,
        "num_points": 50,
        "field_index": 1,
        "wavelength_index": 1
    },
    "ray_fan": {
        "fan_type": "Y",
        "field_index": 1,
        "wavelength_index": 1
    }
}

# === 优化配置 ===

DEFAULT_OPTIMIZATION_SETTINGS = {
    "max_iterations": 100,
    "target_improvement": 1e-6,
    "algorithm": "DampedLeastSquares"
}

# === 绘图配置 ===

PLOT_SETTINGS = {
    "style": "default",
    "figsize": (10, 8),
    "dpi": 300,
    "colors": {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e', 
        'success': '#2ca02c',
        'danger': '#d62728',
        'warning': '#ff9800',
        'info': '#17a2b8'
    },
    "save_format": "png"
}

# === 日志配置 ===

LOG_SETTINGS = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "zosapi.log"
}

# === 文件类型配置 ===

ZEMAX_FILE_EXTENSIONS = [
    ".zmx",  # Zemax 光学系统文件
    ".zos",  # OpticStudio 系统文件
    ".zrd",  # 光线数据库文件
    ".cfg"   # 配置文件
]

# === 单位转换配置 ===

UNIT_CONVERSIONS = {
    "mm_to_microns": 1000.0,
    "microns_to_mm": 0.001,
    "degrees_to_radians": 0.017453292519943295,
    "radians_to_degrees": 57.29577951308232
}

# === 功能开关 ===

FEATURE_FLAGS = {
    "enable_auto_save": False,
    "enable_progress_bar": True,
    "enable_detailed_logging": False,
    "enable_plot_cache": True,
    "enable_parallel_analysis": False
}


def create_output_directory():
    """创建输出目录"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"创建输出目录: {OUTPUT_DIR}")


def get_default_zemax_path():
    """获取默认的 Zemax 安装路径"""
    for path in DEFAULT_ZEMAX_PATHS:
        if os.path.exists(path):
            return path
    return None


def validate_settings():
    """验证配置设置"""
    issues = []
    
    # 检查输出目录权限
    try:
        create_output_directory()
    except Exception as e:
        issues.append(f"无法创建输出目录: {str(e)}")
    
    # 检查 Zemax 路径
    if not get_default_zemax_path():
        issues.append("未找到有效的 Zemax OpticStudio 安装路径")
    
    return issues


# === 导出配置 ===

def get_config():
    """获取完整配置字典"""
    return {
        "paths": {
            "zemax_paths": DEFAULT_ZEMAX_PATHS,
            "output_dir": OUTPUT_DIR
        },
        "analysis": DEFAULT_ANALYSIS_SETTINGS,
        "optimization": DEFAULT_OPTIMIZATION_SETTINGS,
        "plotting": PLOT_SETTINGS,
        "logging": LOG_SETTINGS,
        "units": UNIT_CONVERSIONS,
        "features": FEATURE_FLAGS
    }
