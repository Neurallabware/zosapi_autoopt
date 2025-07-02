# ZOS-API 系统参数设置功能使用指南

## 概述

新增的系统参数设置功能提供了简洁的接口来设置光学系统的关键参数，包括：
- 孔径类型和大小
- 波长设置
- 视场配置
- 环境参数

## 快速开始

### 基本使用

```python
from zosapi_autoopt import create_zosapi_manager, create_system_parameter_manager

# 创建管理器
zos = create_zosapi_manager()
zos.TheSystem.New(False)  # 创建新系统
sys_param = create_system_parameter_manager(zos)

# 快速设置系统参数
sys_param.setup_simple_system(
    aperture_value=40.0,
    field_angles=[(0, 0), (0, 10), (0, 20)],
    wavelength_preset='visible'
)
```

### 使用预设配置

```python
from zosapi_autoopt import apply_system_preset, list_available_presets

# 查看可用预设
list_available_presets()

# 应用预设配置
apply_system_preset(sys_param, 'camera_lens_standard')
```

## 详细功能

### 1. 孔径设置

```python
# 设置入瞳直径
sys_param.set_aperture('entrance_pupil_diameter', 50.0)

# 设置F数
sys_param.set_aperture('paraxial_working_fnum', 2.8)

# 设置数值孔径
sys_param.set_aperture('image_space_na', 0.4)

# 获取孔径信息
aperture_info = sys_param.get_aperture_info()
```

支持的孔径类型：
- `entrance_pupil_diameter`: 入瞳直径
- `image_space_na`: 像方数值孔径
- `object_space_na`: 物方数值孔径
- `float_by_stop_size`: 按光阑大小浮动
- `paraxial_working_fnum`: 近轴工作F数
- `object_cone_angle`: 物方锥角

### 2. 波长设置

```python
# 使用预设波长
sys_param.set_wavelength_preset('visible')  # 可见光
sys_param.set_wavelength_preset('d_0p587')  # D线

# 添加自定义波长
sys_param.add_wavelength(0.587, 1.0)  # 波长0.587μm，权重1.0

# 获取波长信息
wavelength_info = sys_param.get_wavelength_info()
```

### 3. 视场设置

```python
# 设置视场类型
sys_param.set_field_type('angle')  # 角度类型

# 添加视场点
sys_param.add_field(0, 10.0, 1.0)  # (x, y, weight)

# 获取视场信息
field_info = sys_param.get_field_info()
```

支持的视场类型：
- `angle`: 角度
- `object_height`: 物高
- `paraxial_image_height`: 近轴像高
- `real_image_height`: 实际像高

### 4. 环境设置

```python
# 设置环境参数
sys_param.set_environment(
    temperature=25.0,  # 温度（摄氏度）
    pressure=1.0,      # 压力（大气压）
    adjust_index=True  # 是否调整折射率
)
```

## 预设配置

系统提供了多种预设配置，适用于不同的应用场景：

### 系统预设
- `camera_lens_standard`: 标准相机镜头
- `camera_lens_wide`: 广角相机镜头
- `telescope_primary`: 天文望远镜主镜
- `microscope_objective`: 显微镜物镜
- `ir_system`: 红外系统

### 使用示例

```python
# 设置为标准相机镜头配置
apply_system_preset(sys_param, 'camera_lens_standard')

# 设置为显微镜物镜配置
apply_system_preset(sys_param, 'microscope_objective')
```

## 获取系统信息

```python
# 获取完整系统摘要
summary = sys_param.get_system_summary()
print(f"孔径: {summary['aperture']}")
print(f"波长数: {len(summary['wavelengths'])}")
print(f"视场数: {len(summary['fields'])}")

# 获取具体参数信息
aperture_info = sys_param.get_aperture_info()
wavelength_info = sys_param.get_wavelength_info()
field_info = sys_param.get_field_info()
```

## 示例文件

- `examples/system_parameter_example.py`: 详细使用示例
- `examples/system_parameter_test.py`: 快速测试功能

## 错误处理

所有方法都包含适当的错误处理和日志记录。如果遇到问题，请检查：

1. ZOSAPI连接是否正常
2. 参数值是否在有效范围内
3. 系统是否已正确初始化

## 注意事项

- 使用前确保已正确初始化ZOSAPIManager
- 某些参数设置可能会影响其他参数
- 建议在设置完参数后调用`get_system_summary()`验证设置结果
- 波长和视场的索引从1开始（与ZOS-API保持一致）
