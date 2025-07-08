
## `zosapi_autoopt` 自动化库使用总指南

-----

### **1. 核心连接器: `ZOSAPIManager`**

**概述**: `ZOSAPIManager`是您与Zemax OpticStudio沟通的桥梁，负责处理所有底层的连接、授权和文件操作。**所有工作都始于这个管理器**。

#### **1.1 初始化与连接**

```python
from zosapi_autoopt.zosapi_core import ZOSAPIManager

# 初始化管理器，它会自动尝试连接到已打开的Zemax OpticStudio实例
zos_manager = ZOSAPIManager()

# 检查连接状态
if zos_manager.is_connected:
    print("成功连接到Zemax OpticStudio！")
```

#### **1.2 文件操作**

```python
# 创建一个全新的空文件
zos_manager.new_file()

# 打开一个已存在的文件
# (推荐使用API自动查找路径，以保证通用性)
sample_dir = zos_manager.get_samples_dir()
file_path = f"{sample_dir}/Sequential/Objectives/Double Gauss 28 degree field.zos"
zos_manager.open_file(file_path)

# 将当前系统保存到新文件
output_path = "./output/my_new_design.zos"
zos_manager.save_file(output_path)

# 关闭与Zemax的连接
zos_manager.close()
```

-----

### **2. 镜头数据编辑器: `LensDesignManager` (LDE)**

**概述**: `LensDesignManager`让您可以通过代码来操作“镜头数据编辑器”，实现对光学系统每一个面的精确控制。

#### **2.1 基本表面操作**

```python
from zosapi_autoopt.zosapi_lde import LensDesignManager

lde_manager = LensDesignManager(zos_manager)

# 在第2个位置插入一个新表面
lde_manager.insert_surface(2)

# 设置第2个面的曲率半径、厚度和材料
lde_manager.set_radius(2, 50.0)
lde_manager.set_thickness(2, 5.0)
lde_manager.set_material(2, "N-BK7")

# 将第1个面设为光阑面
lde_manager.set_stop_surface(1)
```

#### **2.2 设置优化变量**

这是所有优化的前提步骤。

```python
# 将第2个面的曲率半径设置为变量
lde_manager.set_variable(2, 'radius')

# 批量将所有曲率半径和厚度都设置为变量
# (可以排除物镜面、光阑面和像面)
lde_manager.set_all_radii_as_variables(exclude_surfaces=[0, 1, 7])
lde_manager.set_all_thickness_as_variables(exclude_surfaces=[0, 1, 7])

# 为非球面设置变量
lde_manager.set_surface_type(3, 'aspheric') # 首先确保表面类型正确
lde_manager.set_variable(3, 'conic')       # 设置锥面系数为变量
lde_manager.set_all_aspheric_as_variables(start_surface=3, end_surface=3, order=4)
```

-----

### **3. 系统参数管理器: `SystemParameterManager`**

**概述**: `SystemParameterManager`用于设置全局性的系统参数，相当于Zemax中的“System Explorer”。

```python
from zosapi_autoopt.zosapi_system import SystemParameterManager

sys_param_manager = SystemParameterManager(zos_manager)

# 1. 设置系统孔径
sys_param_manager.set_aperture('entrance_pupil_diameter', 20.0)

# 2. 设置波长
sys_param_manager.set_wavelength_preset('fdc_visible') # 使用F, d, C三色光预设

# 3. 设置视场
sys_param_manager.set_field_type('angle') # 将视场类型设为角度
sys_param_manager.clear_fields()          # 清空默认视场
sys_param_manager.add_field(x=0, y=0, weight=1.0)
sys_param_manager.add_field(x=0, y=10.0, weight=1.0) # 添加0度和10度两个视场
```

-----

### **4. 评价函数编辑器: `MeritFunctionEditor`**

```python
from zosapi_autoopt.merit_function import MeritFunctionEditor

mf_editor = MeritFunctionEditor(zos_manager)
Op = mf_editor.Operands # 创建别名

# 1. 使用优化向导快速构建
mf_editor.use_optimization_wizard('rms_spot')

# 2. 手动添加操作数进行微调
mf_editor.add_operand(Op.TOTR, target=80.0, weight=1.0) # 控制总长
mf_editor.add_operand(Op.MNCG, target=2.0, weight=10.0, surf1=1, surf2=5) # 控制最小玻璃厚度

# 3. 运行优化
initial_merit = mf_editor.get_current_merit_value()
print(f"优化前评价函数值: {initial_merit:.6f}")
result = mf_editor.run_local_optimization()
if result['success']:
    print(f"优化后评价函数值: {result['final_merit']:.6f}")
```

-----

### **5. 光学分析与绘图: `ZOSAnalyzer` & `zosapi_plotting`**

**概述**: 当您的设计或优化完成后，可以使用这些模块来生成专业的光学性能分析图表。

```python
from zosapi_autoopt.zosapi_analysis import ZOSAnalyzer
from zosapi_autoopt.zosapi_plotting import plot_spots, plot_rayfan, plot_mtf, analyze_and_plot_system

analyzer = ZOSAnalyzer(zos_manager)

# --- 单项分析 ---

# 绘制点列图
plot_spots(zos_manager, analyzer, fields="all", wavelengths="all", save_path="./output/spots.png")

# 绘制光扇图
plot_rayfan(zos_manager, analyzer, fields="all", wavelengths="single", save_path="./output/rayfan.png")

# --- 一键生成全部分析报告 ---
# 这是最推荐、最便捷的方式
all_files = analyze_and_plot_system(zos_manager, output_dir="./output/full_report")
print("全部分析报告已生成:", all_files)
```

-----

### **6. 系统布局图: `ZOSLayoutAnalyzer`**

**概述**: `ZOSLayoutAnalyzer`专门用于从Zemax中导出高质量的2D和3D系统布局图。

```python
from zosapi_autoopt.zosapi_layout import ZOSLayoutAnalyzer

layout_analyzer = ZOSLayoutAnalyzer(zos_manager)

# 导出2D截面图
layout_analyzer.export_cross_section(
    save_path="./output/layout_2d.png",
    number_of_rays=15,          # 设置光线数量
    color_rays_by='Wavelength'  # 按波长给光线上色
)

# 导出3D着色模型图
layout_analyzer.export_shaded_model("./output/layout_3d.png")
```