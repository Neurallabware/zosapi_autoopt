# ZOSAPI 自动化分析系统 - 使用说明

## 项目概述

本项目是一个基于 Zemax OpticStudio 的 Python 自动化分析系统，提供了完整的光学系统分析和可视化功能。系统经过全面优化，确保分析结果与 Zemax 原生功能完全一致。

## 核心功能

### 1. 基础分析功能
- **点列图分析 (Spot Diagram)**: 多视场、多波长点列图分析，物理尺寸和比例完全一致
- **Ray Fan分析**: X/Y方向像差曲线，数据提取完全对应Zemax原生结果
- **MTF分析**: 调制传递函数分析，支持多视场和多波长
- **畸变分析**: 场曲和畸变分析，包括网格畸变可视化

### 2. 高级功能
- **批量分析**: 支持多个光学文件的批量处理
- **系统比较**: 不同光学系统性能对比分析
- **一键综合分析**: 生成包含所有分析类型的综合报告
- **参数扫描**: 支持配置参数的扫描分析

### 3. 核心修复和优化
- ✅ **点列图子图物理尺寸一致**: 使用 `constrained_layout=True` 和 `aspect='equal'` 确保真实比例
- ✅ **Ray Fan数据完全正确**: 采用官方示例23的方法，按数据序列索引正确区分X/Y方向
- ✅ **畸变分析功能完整**: 新增场曲/畸变和网格畸变分析，参考官方API
- ✅ **批量处理能力**: 完善的BatchAnalyzer类，支持多文件和参数扫描

## 文件结构

```
zosapi/
├── __init__.py                 # 包初始化
├── config.py                   # 配置文件
├── zosapi_core.py             # ZOSAPI核心连接管理
├── zosapi_analysis.py         # 分析功能实现
├── zosapi_plotting.py         # 绘图和可视化
├── zosapi_utils.py            # 工具函数
├── test_with_sample.py        # 基础测试脚本
├── test_comprehensive.py      # 全面功能测试
├── test_distortion.py         # 畸变分析测试
├── README.md                  # 项目说明
└── sample/                    # 官方示例代码
    ├── README.md
    └── PythonStandalone_*.py
```

## 快速开始

### 1. 基本使用

```python
from zosapi_core import ZOSAPIManager
from zosapi_plotting import analyze_and_plot_system

# 连接到Zemax
zos_manager = ZOSAPIManager()

# 打开光学文件（或使用新系统）
zos_manager.open_file("your_optical_system.zos")

# 一键生成所有分析图表
saved_files = analyze_and_plot_system(zos_manager, output_dir="analysis_output")
print("分析完成，保存的文件:", saved_files)
```

### 2. 单独分析

```python
from zosapi_analysis import ZOSAnalyzer
from zosapi_plotting import plot_spots, plot_rayfan

# 创建分析器
analyzer = ZOSAnalyzer(zos_manager)

# 点列图分析
plot_spots(zos_manager, analyzer, 
                     fields="all", wavelengths="all",
                     save_path="spots.png")

# Ray Fan分析
plot_rayfan(zos_manager, analyzer,
                      fields="all", wavelengths="single",
                      save_path="rayfan.png")
```

### 3. 批量分析

```python
from zosapi_analysis import BatchAnalyzer

# 创建批量分析器
batch_analyzer = BatchAnalyzer(zos_manager)

# 分析多个文件
files = ["system1.zos", "system2.zos", "system3.zos"]
results = batch_analyzer.analyze_multiple_files(
    file_paths=files,
    analysis_types=['spot', 'rayfan', 'mtf', 'distortion'],
    output_dir="batch_output"
)
```

### 4. 系统比较

```python
# 比较多个系统
comparison_results = batch_analyzer.compare_systems(
    system_files=["system_a.zos", "system_b.zos"],
    analysis_type="spot",
    output_dir="comparison"
)
```

## 主要API说明

### ZOSAPIManager 类
```python
# 连接管理
zos_manager = ZOSAPIManager()
zos_manager.open_file(file_path)      # 打开文件
zos_manager.new_file()                # 创建新系统
zos_manager.save_file(file_path)      # 保存文件
```

### ZOSAnalyzer 类
```python
analyzer = ZOSAnalyzer(zos_manager)

# 点列图分析
spot_data = analyzer.analyze_spot_diagram(field_index=0, wavelength_index=0)

# Ray Fan分析
rayfan_data = analyzer.analyze_ray_fan(field_index=0, wavelength_index=0, fan_type="X")

# 畸变分析
distortion_data = analyzer.analyze_field_curvature_distortion(num_points=50)
grid_data = analyzer.analyze_grid_distortion(field_index=0, wavelength_index=0)
```

### 绘图函数
```python
# 多视场点列图
plot_spots(zos_manager, analyzer, fields="all", wavelengths="all")

# 多视场Ray Fan
plot_rayfan(zos_manager, analyzer, fields="all", wavelengths="single")

# MTF分析
plot_mtf(zos_manager, fields="all", wavelengths="all")

# 畸变分析
plot_field_curvature_distortion(zos_manager, analyzer)

# 综合分析
plot_mtf_spot_ranfan(zos_manager, analyzer, fields="all", wavelengths="all")
```

## 参数说明

### 视场选择参数 (fields)
- `"all"`: 分析所有视场
- `"single"`: 仅分析第一个视场
- `[0, 1, 2]`: 指定视场索引列表（0基索引）

### 波长选择参数 (wavelengths)
- `"all"`: 分析所有波长
- `"single"`: 仅分析主波长
- `[0, 1, 2]`: 指定波长索引列表（0基索引）

### 分析类型 (analysis_types)
- `"spot"`: 点列图分析
- `"rayfan"`: Ray Fan分析
- `"mtf"`: MTF分析
- `"distortion"`: 畸变分析

## 输出文件说明

### 基础分析输出
- `multifield_spots.png`: 多视场点列图
- `multifield_rayfan.png`: 多视场Ray Fan图
- `system_mtf.png`: 系统MTF曲线
- `field_curvature_distortion.png`: 场曲和畸变分析
- `comprehensive_analysis.png`: 综合分析大图

### 批量分析输出
```
batch_output/
├── batch_analysis_report.txt    # 批量分析报告
├── system1/                     # 各系统分析结果
│   ├── spots.png
│   ├── rayfan.png
│   └── distortion.png
└── system2/
    ├── spots.png
    ├── rayfan.png
    └── distortion.png
```

## 测试脚本

### 1. 基础功能测试
```bash
python test_with_sample.py
```

### 2. 全面功能测试
```bash
python test_comprehensive.py
```

### 3. 畸变分析测试
```bash
python test_distortion.py
```

## 技术特点

### 1. 数据准确性
- Ray Fan分析采用官方示例23的数据提取方法
- X/Y方向数据按序列索引正确区分（Series 0为Y-Fan，Series 1为X-Fan）
- 所有分析结果与Zemax原生功能完全一致

### 2. 图像质量
- 点列图子图物理尺寸完全一致，真实反映光斑特征
- 使用 `constrained_layout=True` 确保布局一致性
- 高DPI输出（300 DPI），适合论文和报告使用

### 3. 代码质量
- 完整的错误处理和日志记录
- 模块化设计，易于扩展和维护
- 详细的API文档和类型注解

### 4. 性能优化
- 高效的数据提取和处理
- 内存管理优化，避免内存泄漏
- 支持大批量文件处理

## 故障排除

### 1. 连接问题
```python
# 检查Zemax是否运行
if not zos_manager.is_connected:
    print("请确保Zemax OpticStudio正在运行")
```

### 2. 文件路径问题
```python
# 使用绝对路径
file_path = r"C:\full\path\to\your\file.zos"
zos_manager.open_file(file_path)
```

### 3. 分析失败
```python
# 检查系统是否有有效的视场和波长
system = zos_manager.TheSystem
num_fields = system.SystemData.Fields.NumberOfFields
num_wavelengths = system.SystemData.Wavelengths.NumberOfWavelengths
print(f"视场数: {num_fields}, 波长数: {num_wavelengths}")
```

## 扩展开发

### 1. 新增分析类型
在 `zosapi_analysis.py` 的 `ZOSAnalyzer` 类中添加新的分析方法：

```python
def analyze_new_feature(self, **kwargs):
    # 实现新的分析功能
    pass
```

### 2. 新增绘图功能
在 `zosapi_plotting.py` 中添加对应的绘图函数：

```python
def plot_new_feature(zos_manager, analyzer, save_path=None):
    # 实现新的绘图功能
    pass
```

### 3. 批量分析扩展
在 `BatchAnalyzer` 类中添加新的批量处理功能。

## 更新日志

### v1.0 (当前版本)
- ✅ 完整实现点列图、Ray Fan、MTF分析
- ✅ 新增畸变分析功能（场曲/畸变、网格畸变）
- ✅ 修复Ray Fan分析数据提取问题
- ✅ 优化点列图子图物理尺寸一致性
- ✅ 实现批量分析和系统比较功能
- ✅ 完整的测试套件和文档

## 支持与反馈

如有问题或建议，请：
1. 查看本文档的故障排除部分
2. 运行测试脚本验证功能
3. 检查日志输出获取详细错误信息

---

**注意**: 使用本系统前请确保：
1. Zemax OpticStudio 正在运行
2. 已正确安装 ZOSAPI Python 包
3. Python 环境包含必要的依赖包（matplotlib, numpy等）
