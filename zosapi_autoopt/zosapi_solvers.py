"""
Zemax OpticStudio 镜头数据编辑器(LDE)模块 - 变量与求解器扩展
提供设置变量、求解器和多组态功能
Author: allin-love
Date: 2025-07-03
"""

# 定义求解器和变量类型
SOLVER_TYPES = {
    'position': '位置求解器',
    'thickness': '厚度求解器', 
    'curvature': '曲率求解器',
    'pickup': '拾取求解器',
    'edge_thickness': '边缘厚度求解器',
    'marginal_ray': '边缘光线求解器',
    'chief_ray': '主光线求解器',
    'fixed': '固定求解器',
    'thermal': '热膨胀求解器',
    'variable': '变量'
}

# 求解器支持的参数列表
SOLVER_PARAM_TYPES = {
    'position': ['x', 'y', 'z', 'tilt_x', 'tilt_y', 'tilt_z'],
    'thickness': ['thickness'],
    'curvature': ['radius', 'conic'],
    'pickup': ['radius', 'thickness', 'material', 'conic', 'semi_diameter'],
    'edge_thickness': ['thickness', 'radius'],
    'marginal_ray': ['radius', 'thickness'],
    'chief_ray': ['radius', 'thickness'],
    'fixed': ['radius', 'thickness', 'conic', 'semi_diameter'],
    'thermal': ['radius', 'thickness'],
    'variable': ['radius', 'thickness', 'conic', 'semi_diameter', 'x', 'y', 'z', 'tilt_x', 'tilt_y', 'tilt_z']
}

# 变量求解器的目标函数类型
MERIT_FUNCTION_TYPES = {
    'spot_size': '点列图尺寸',
    'wavefront': '波前',
    'mtf': 'MTF值',
    'encircled_energy': '能量密集度',
    'lateral_color': '侧向色差',
    'distortion': '畸变'
}
