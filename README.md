# Zemax OpticStudio Python API 自动化封装库

这是一个为 Zemax OpticStudio Python API 提供简化接口的专业封装库，严格按照官方例程标准实现，专为高效光学分析和优化而设计。

## 🎯 最新更新 (2025-06-29)

**重大改进**：
- ✅ **API修正**：严格对照官方例程4（MTF）、22（点列图）、23（光线扇形图）重构分析方法
- ✅ **全英文界面**：移除所有中文显示，避免字体兼容性问题
- ✅ **兼容性增强**：增加完善的API版本兼容性处理
- ✅ **质量保证**：所有分析结果与官方例程一致

## 🌟 功能特点

- **严格的官方标准**: 分析方法完全按照 Zemax 官方例程实现
- **专业英文界面**: 所有标签、图表、文档均为英文，确保跨平台兼容
- **简化的连接管理**: 自动处理 ZOSAPI 初始化和连接
- **模块化设计**: 将常用功能分类封装为独立模块
- **丰富的分析功能**: 点列图、波前、MTF、光线扇形图、场曲畸变等
- **高质量绘图**: 内置专业级光学图表绘制功能（300 DPI输出）
- **批量处理**: 支持多视场、多波长批量分析
- **自动优化**: 集成系统优化和快速聚焦功能
- **健壮设计**: 完善的错误处理和兼容性逻辑

## 🚀 超级简化用法 - HIGH-LEVEL FUNCTIONS

### ✨ 一行代码完成所有分析 (Ultimate One-Liner)
```python
from zosapi_core import ZOSAPIManager
from zosapi_plotting import analyze_and_plot_system

# 连接到Zemax
zos_manager = ZOSAPIManager()

# 加载系统 (或使用当前系统)
# zos_manager.load_file("your_system.zmx")

# 🎯 一行代码完成：MTF + 点列图 + 光线扇形图 + 综合分析！
saved_files = analyze_and_plot_system(zos_manager, output_dir="./results")

# 就这样！🎉 所有分析图表已生成
```

### 🎨 高级绘图函数 (4行搞定)
```python
from zosapi_analysis import ZOSAnalyzer
from zosapi_plotting import plot_system_mtf, plot_multifield_spots, plot_multifield_rayfan, plot_comprehensive_analysis

analyzer = ZOSAnalyzer(zos_manager)

# 每个函数自动处理所有视场和波长
plot_system_mtf(zos_manager, "mtf.png")                                      # MTF分析
plot_multifield_spots(zos_manager, analyzer, "spots.png")                    # 点列图  
plot_multifield_rayfan(zos_manager, analyzer, "rayfan.png")                 # 光线扇形图
plot_comprehensive_analysis(zos_manager, analyzer, "comprehensive.png")      # 综合分析图
```

### 📊 代码复杂度对比

**🔴 传统方式 (150+ 行):**
```python
# 手写matplotlib代码做MTF分析
mtf_analysis = system.Analyses.New_FftMtf()
# ... 30+ 行设置和绘图代码 ...

# 手写matplotlib代码做点列图  
fig, axes = plt.subplots(n_rows, n_cols, figsize=(...))
# ... 50+ 行子图管理代码 ...

# 手写matplotlib代码做光线扇形图
# ... 另外50+ 行 ...

# 手写综合分析图
# ... 再50+ 行 ...
```

**🟢 新方式 (1-4 行):**
```python
# 一行搞定全部！
analyze_and_plot_system(zos_manager, "./results")

# 或者分别调用
plot_system_mtf(zos_manager, "mtf.png")
plot_multifield_spots(zos_manager, analyzer, "spots.png") 
plot_multifield_rayfan(zos_manager, analyzer, "rayfan.png")
plot_comprehensive_analysis(zos_manager, analyzer, "comprehensive.png")
```

**结果: 95% 代码减少！🎯 现在可以专注于光学设计而不是绘图代码！**

## 📁 模块结构

```
zosapi/
├── __init__.py                      # 包初始化文件
├── zosapi_core.py                   # 核心连接和管理
├── zosapi_utils.py                  # 数据处理工具
├── zosapi_plotting.py               # 专业绘图功能（全英文）
├── zosapi_analysis.py               # 光学分析（基于官方例程）
├── auto_optimizer.py                # 自动优化工具
├── config.py                        # 配置文件
├── example_usage.py                 # 使用示例
├── test_basic.py                    # 基础功能测试
├── single_lens_test.py              # 单透镜建模优化测试
├── test_plotting_standalone.py     # 独立绘图功能测试
├── CORRECTIONS_SUMMARY.md          # 修正内容详细说明
└── README.md                        # 说明文档
```

## 🚀 快速开始

### 1. 基础连接和分析

```python
from zosapi_core import ZOSAPIManager
from zosapi_analysis import ZOSAnalyzer
from zosapi_plotting import ZOSPlotter

# 连接到 OpticStudio
zos_manager = ZOSAPIManager()
if zos_manager.connect():
    print("✅ Connected to Zemax OpticStudio")
    
    # 打开文件
    zos_manager.open_file("your_file.zos")
    
    # 创建分析器
    analyzer = ZOSAnalyzer(zos_manager)
    
    # 分析点列图 (基于官方例程22)
    spot_data = analyzer.analyze_spot_diagram(field_index=0, wavelength_index=0)
    print(f"RMS Radius: {spot_data['rms_radius']:.6f} mm")
    
    # 分析MTF (基于官方例程4)
    mtf_data = analyzer.analyze_mtf(field_index=0, max_frequency=50)
    print(f"MTF at Nyquist: {mtf_data['mtf_tangential'][-1]:.3f}")
    
    # 绘制专业图表 (全英文标签)
    plotter = ZOSPlotter()
    fig = plotter.plot_spot_diagram(
        spot_data['x_coords'], spot_data['y_coords'],
        title="Spot Diagram Analysis",
        save_path="spot_diagram.png"
    )
        spot_data['x_coords'], 
        spot_data['y_coords'],
        title="点列图",
        save_path="spot.png"
    )
```

### 2. 批量分析

```python
from zosapi import quick_connect, BatchAnalyzer

with quick_connect() as zos:
    zos.open_file("your_file.zmx")
    
    # 创建批量分析器
    batch_analyzer = BatchAnalyzer(zos)
    
    # 分析所有视场的点列图
    all_spots = batch_analyzer.analyze_all_fields_spots()
    
    # 分析所有波长的 MTF
    all_mtf = batch_analyzer.analyze_all_wavelengths_mtf()
```

### 3. 系统优化

```python
from zosapi import quick_connect, ZOSAnalyzer

with quick_connect() as zos:
    zos.open_file("your_file.zmx")
    
    analyzer = ZOSAnalyzer(zos)
    
    # 快速聚焦
    focus_result = analyzer.quick_focus()
    
    # 系统优化
    opt_result = analyzer.optimize_system(max_iterations=100)
    print(f"优化改善: {opt_result['improvement']*100:.2f}%")
```

## 核心类说明

### ZOSAPIManager
核心连接管理器，处理与 OpticStudio 的连接和基础操作。

**主要方法:**
- `connect()`: 连接到 OpticStudio
- `disconnect()`: 断开连接
- `open_file()`: 打开光学系统文件
- `save_file()`: 保存文件
- `get_system_info()`: 获取系统信息

### ZOSAnalyzer
光学分析器，提供各种光学分析功能。

**主要方法:**
- `analyze_spot_diagram()`: 点列图分析
- `analyze_wavefront()`: 波前分析
- `analyze_mtf()`: MTF 分析
- `analyze_ray_fan()`: 光线扇形图分析
- `optimize_system()`: 系统优化
- `quick_focus()`: 快速聚焦

### ZOSPlotter
绘图器，提供各种光学图表的绘制功能。

**主要方法:**
- `plot_spot_diagram()`: 绘制点列图
- `plot_wavefront()`: 绘制波前图
- `plot_mtf_curve()`: 绘制 MTF 曲线
- `plot_ray_fan()`: 绘制光线扇形图
- `plot_multiple_curves()`: 绘制多曲线图

### BatchAnalyzer
批量分析器，支持多视场、多波长的批量分析。

**主要方法:**
- `analyze_all_fields_spots()`: 分析所有视场的点列图
- `analyze_all_wavelengths_mtf()`: 分析所有波长的 MTF

## 配置说明

可以通过修改 `config.py` 文件来调整各种默认设置：

- **路径配置**: Zemax 安装路径、输出目录
- **分析参数**: 默认的分析设置
- **绘图设置**: 图表样式、颜色、尺寸等
- **优化参数**: 优化算法设置
- **功能开关**: 启用/禁用特定功能

## 依赖要求

- Python 3.7+
- Zemax OpticStudio (支持 Python API)
- matplotlib (绘图)
- numpy (数值计算)
- pandas (数据处理)
- scipy (可选，用于高级数据处理)

## 安装依赖

```bash
pip install matplotlib numpy pandas scipy
```

## 使用注意事项

1. **许可证要求**: 需要有效的 Zemax OpticStudio 许可证且支持 API 使用
2. **路径设置**: 确保 Zemax OpticStudio 正确安装且路径可访问
3. **文件权限**: 确保对输出目录有写入权限
4. **内存管理**: 处理大型分析时注意内存使用
5. **异常处理**: 建议使用 try-except 块处理可能的异常

## 示例文件

运行 `example_usage.py` 可以查看完整的使用示例：

```bash
python example_usage.py
```

示例包括：
- 基础分析操作
- 绘图功能演示
- 批量分析示例
- 系统优化流程
- 自定义分析案例

## 扩展开发

### 添加新的分析功能

1. 在 `ZOSAnalyzer` 类中添加新方法
2. 在 `ZOSPlotter` 类中添加对应的绘图方法
3. 更新配置文件中的默认参数
4. 编写测试用例

### 自定义绘图样式

1. 修改 `config.py` 中的 `PLOT_SETTINGS`
2. 在 `ZOSPlotter` 类中添加新的绘图方法
3. 使用 matplotlib 的样式系统

## 故障排除

### 常见问题

1. **连接失败**: 检查 Zemax OpticStudio 是否正确安装
2. **许可证错误**: 确认许可证支持 API 使用
3. **路径错误**: 检查文件路径是否正确
4. **内存不足**: 减少分析数据的采样密度

### 日志查看

启用详细日志记录：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 版本历史

- **v1.0.0**: 初始版本，包含核心功能

## 作者信息

- 作者: Your Name
- 日期: 2025-06-29
- 版本: 1.0.0

## 许可证

本项目仅供学习和研究使用。

---

**提示**: 这个封装库大大简化了 Zemax OpticStudio Python API 的使用，让您可以专注于光学分析和优化，而不用重复编写基础代码。建议先运行示例文件熟悉各个功能，然后根据您的具体需求进行定制开发。
