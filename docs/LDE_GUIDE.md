# ZOS-API 镜头数据编辑器(LDE)功能使用指南

## 概述

镜头数据编辑器(Lens Data Editor, LDE)功能模块提供了编程方式操作Zemax OpticStudio光学系统设计的能力，包括：
- 添加、删除和修改光学表面
- 设置表面参数（曲率半径、厚度、材料等）
- 设置特殊表面属性（表面类型、倾斜偏心等）
- 获取系统镜头信息

## 快速开始

### 基本使用

```python
from zosapi_autoopt import create_zosapi_manager, create_lens_design_manager

# 创建管理器
zos = create_zosapi_manager()
zos.TheSystem.New(False)  # 创建新系统
lde = create_lens_design_manager(zos)

# 设计一个简单的双凸透镜
lde.set_radius(1, 50.0)         # 前表面曲率半径
lde.set_thickness(1, 5.0)       # 前表面到后表面的厚度
lde.set_material(1, "N-BK7")    # 材料

lde.insert_surface(2)           # 插入后表面
lde.set_radius(2, -50.0)        # 后表面曲率半径
lde.set_thickness(2, 100.0)     # 后表面到像面的距离

lde.insert_surface(3)           # 插入像面
lde.set_radius(3, 0.0)          # 像面为平面
lde.set_thickness(3, 0.0)       # 像面厚度为0

# 保存文件
zos.TheSystem.SaveAs("双凸透镜.zos")
```

## 详细功能

### 1. 基本表面操作

```python
# 插入新表面
lde.insert_surface(2)  # 在位置2插入表面

# 删除表面
lde.delete_surface(2)  # 删除位置2的表面

# 获取表面对象
surface = lde.get_surface(2)

# 获取表面总数
count = lde.get_surface_count()

# 复制表面
lde.copy_surfaces(2, 3, 5)  # 从位置2开始复制3个表面到位置5
```

### 2. 表面参数设置

```python
# 设置曲率半径
lde.set_radius(2, 50.0)  # 设置位置2的表面曲率半径为50

# 设置厚度
lde.set_thickness(2, 5.0)  # 设置位置2的表面厚度为5

# 设置材料
lde.set_material(2, "N-BK7")  # 设置位置2的表面材料为N-BK7

# 设置半口径
lde.set_semi_diameter(2, 10.0)  # 设置位置2的表面半口径为10
```

### 3. 特殊表面属性

```python
# 设置表面类型
lde.set_surface_type(2, "aspheric")  # 设置位置2的表面为非球面

# 设置锥面系数
lde.set_conic(2, -1.0)  # 设置位置2的表面锥面系数为-1

# 设置非球面系数
lde.set_aspheric_coefficients(2, [1e-6, 1e-8, 1e-10])  # 设置非球面系数

# 设置倾斜偏心
lde.set_tilt_decenter(2, tilt_x=5.0, decenter_y=2.0)  # 设置位置2的表面X轴倾斜5度，Y轴偏心2mm

# 设置光阑
lde.set_aperture(2, "circular", 10.0)  # 设置位置2的表面为圆形光阑，半径10mm
```

### 4. 坐标系转换

```python
# 局部坐标转全局坐标
lde.convert_local_to_global(2, 5, 1)  # 将位置2到5的表面转换为全局坐标，参考表面为1

# 全局坐标转局部坐标
lde.convert_global_to_local(2, 5, "forward")  # 将位置2到5的表面转换为局部坐标，按前向顺序
```

### 5. 获取信息

```python
# 获取表面参数
params = lde.get_surface_parameters(2)
print(f"曲率半径: {params['radius']}")
print(f"厚度: {params['thickness']}")
print(f"材料: {params['material']}")

# 获取系统摘要
summary = lde.get_system_summary()
print(f"表面数量: {summary['surface_count']}")
for i, surface in enumerate(summary['surfaces'], 1):
    print(f"表面 {i}: {surface['radius']}, {surface['thickness']}, {surface['material']}")
```

## 示例文件

- `examples/lde_basic_test.py`: 基本功能测试示例
- `examples/lde_double_gauss.py`: 创建双高斯镜头示例

## 注意事项

- 表面索引从0开始，0表示物面
- 设置锥面系数等特殊参数前，需要先将表面类型设置为对应类型
- 对于不同类型的表面，可用的参数可能不同
- 复杂的镜头设计建议先在OpticStudio中设计好，然后用API进行修改
