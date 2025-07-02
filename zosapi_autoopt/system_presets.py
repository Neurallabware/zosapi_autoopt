"""
系统参数配置预设
定义常用的光学系统参数组合

Author: allin-love
Date: 2025-07-01
"""

# 常用孔径配置
APERTURE_PRESETS = {
    'wide_angle': {
        'type': 'entrance_pupil_diameter',
        'value': 50.0,
        'description': '广角镜头 - 入瞳直径50mm'
    },
    'telephoto': {
        'type': 'entrance_pupil_diameter', 
        'value': 80.0,
        'description': '长焦镜头 - 入瞳直径80mm'
    },
    'microscope': {
        'type': 'image_space_fnum',
        'value': 4.0,
        'description': '显微镜物镜 - 像方F/4'
    },
    'telescope': {
        'type': 'entrance_pupil_diameter',
        'value': 200.0,
        'description': '望远镜 - 入瞳直径200mm'
    },
    'f2p8': {
        'type': 'paraxial_working_fnum',
        'value': 2.8,
        'description': 'F/2.8 光圈'
    },
    'f4': {
        'type': 'paraxial_working_fnum',
        'value': 4.0,
        'description': 'F/4 光圈'
    }
}

# 常用波长配置
WAVELENGTH_PRESETS = {
    'visible': {
        'preset': 'fdc_visible',
        'description': '可见光谱 (F,d,C线)'
    },
    'd_line': {
        'preset': 'd_0p587',
        'description': 'D线单色光 (0.587μm)'
    },
    'f_line': {
        'preset': 'f_0p486',
        'description': 'F线单色光 (0.486μm)'
    },
    'c_line': {
        'preset': 'c_0p656',
        'description': 'C线单色光 (0.656μm)'
    },
    'near_ir': {
        'preset': 'hene_0p6328',
        'description': '氦氖激光 (0.6328μm)'
    },
    'rgb': {
        'custom': [
            (0.486, 1.0),  # 蓝光
            (0.546, 1.0),  # 绿光  
            (0.656, 1.0)   # 红光
        ],
        'primary': 2,  # 绿光为主
        'description': 'RGB三色光'
    }
}

# 常用视场配置
FIELD_PRESETS = {
    'on_axis': {
        'type': 'angle',
        'fields': [(0, 0)],
        'description': '仅轴上视场'
    },
    'small_fov': {
        'type': 'angle',
        'fields': [(0, 0), (0, 5), (0, 10)],
        'description': '小视场 (0°, 5°, 10°)'
    },
    'medium_fov': {
        'type': 'angle', 
        'fields': [(0, 0), (0, 10), (0, 20)],
        'description': '中等视场 (0°, 10°, 20°)'
    },
    'wide_fov': {
        'type': 'angle',
        'fields': [(0, 0), (0, 15), (0, 30), (0, 40)],
        'description': '大视场 (0°, 15°, 30°, 40°)'
    },
    'object_height_5mm': {
        'type': 'object_height',
        'fields': [(0, 0), (0, 2.5), (0, 5)],
        'description': '物高视场 (0, 2.5, 5mm)'
    },
    'rectangular_fov': {
        'type': 'angle',
        'fields': [(0, 0), (10, 0), (0, 10), (10, 10)],
        'description': '矩形视场 (4点)'
    }
}

# 完整系统配置预设
SYSTEM_PRESETS = {
    'camera_lens_standard': {
        'aperture': APERTURE_PRESETS['f2p8'],
        'wavelength': WAVELENGTH_PRESETS['visible'],
        'field': FIELD_PRESETS['medium_fov'],
        'environment': {'temperature': 20.0, 'pressure': 1.0},
        'description': '标准相机镜头配置'
    },
    'camera_lens_wide': {
        'aperture': APERTURE_PRESETS['wide_angle'],
        'wavelength': WAVELENGTH_PRESETS['visible'],
        'field': FIELD_PRESETS['wide_fov'],
        'environment': {'temperature': 20.0, 'pressure': 1.0},
        'description': '广角相机镜头配置'
    },
    'telescope_primary': {
        'aperture': APERTURE_PRESETS['telescope'],
        'wavelength': WAVELENGTH_PRESETS['visible'],
        'field': FIELD_PRESETS['small_fov'],
        'environment': {'temperature': 0.0, 'pressure': 0.1},
        'description': '天文望远镜主镜配置'
    },
    'microscope_objective': {
        'aperture': APERTURE_PRESETS['microscope'],
        'wavelength': WAVELENGTH_PRESETS['d_line'],
        'field': FIELD_PRESETS['on_axis'],
        'environment': {'temperature': 25.0, 'pressure': 1.0},
        'description': '显微镜物镜配置'
    },
    'ir_system': {
        'aperture': APERTURE_PRESETS['f4'],
        'wavelength': WAVELENGTH_PRESETS['near_ir'],
        'field': FIELD_PRESETS['medium_fov'],
        'environment': {'temperature': 20.0, 'pressure': 1.0},
        'description': '红外系统配置'
    }
}


def apply_system_preset(sys_param_manager, preset_name: str):
    """
    应用系统预设配置
    
    Args:
        sys_param_manager: SystemParameterManager 实例
        preset_name: 预设名称
    """
    if preset_name not in SYSTEM_PRESETS:
        raise ValueError(f"未知的系统预设: {preset_name}")
    
    preset = SYSTEM_PRESETS[preset_name]
    
    # 设置孔径
    aperture_config = preset['aperture']
    sys_param_manager.set_aperture(
        aperture_config['type'],
        aperture_config['value']
    )
    
    # 设置波长
    wavelength_config = preset['wavelength']
    if 'preset' in wavelength_config:
        sys_param_manager.set_wavelength_preset(wavelength_config['preset'])
    elif 'custom' in wavelength_config:
        # 清除现有波长
        wavelengths = sys_param_manager.system_data.Wavelengths
        while wavelengths.NumberOfWavelengths > 0:
            wavelengths.RemoveWavelength(1)
        
        # 添加自定义波长
        for wave, weight in wavelength_config['custom']:
            sys_param_manager.add_wavelength(wave, weight)
        
        # 设置主波长
        if 'primary' in wavelength_config:
            sys_param_manager.set_primary_wavelength(wavelength_config['primary'])
    
    # 设置视场
    field_config = preset['field']
    sys_param_manager.set_field_type(field_config['type'])
    
    # 清除现有视场
    fields = sys_param_manager.system_data.Fields
    while fields.NumberOfFields > 0:
        fields.DeleteFieldAt(1)
    
    # 添加新视场
    for x, y in field_config['fields']:
        sys_param_manager.add_field(x, y)
    
    # 设置环境
    env_config = preset['environment']
    sys_param_manager.set_environment(
        temperature=env_config.get('temperature', 20.0),
        pressure=env_config.get('pressure', 1.0)
    )
    
    print(f"已应用预设配置: {preset['description']}")


def list_available_presets():
    """列出所有可用的预设配置"""
    print("可用的系统预设配置:")
    print("=" * 50)
    
    for name, config in SYSTEM_PRESETS.items():
        print(f"{name:20} - {config['description']}")
    
    print("\n可用的孔径预设:")
    print("-" * 30)
    for name, config in APERTURE_PRESETS.items():
        print(f"{name:15} - {config['description']}")
    
    print("\n可用的波长预设:")
    print("-" * 30)
    for name, config in WAVELENGTH_PRESETS.items():
        print(f"{name:15} - {config['description']}")
    
    print("\n可用的视场预设:")
    print("-" * 30)
    for name, config in FIELD_PRESETS.items():
        print(f"{name:20} - {config['description']}")


if __name__ == "__main__":
    list_available_presets()
