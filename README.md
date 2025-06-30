# ZOSAPI 自动化分析系统 ✨ | ZOSAPI Automation Analysis System

**Zemax OpticStudio Python 自动化分析与可视化系统**  
**Zemax OpticStudio Python Automation Analysis and Visualization System**

*完整的光学系统分析工具包，确保与原生Zemax结果完全一致*  
*Complete optical system analysis toolkit ensuring full consistency with native Zemax results*

---

## 🎯 主要特性 | Key Features

- ✅ **点列图分析 | Spot Diagram Analysis**: 多视场、多波长，物理尺寸和比例完全一致
  *Multi-field, multi-wavelength with consistent physical dimensions and proportions*
  
- ✅ **Ray Fan分析 | Ray Fan Analysis**: X/Y方向像差曲线，与Zemax原生结果完全一致
  *X/Y aberration curves perfectly consistent with native Zemax results*
  
- ✅ **MTF分析 | MTF Analysis**: 调制传递函数分析，支持多视场和多波长
  *Modulation transfer function analysis, supporting multiple fields and wavelengths*
  
- ✅ **场曲畸变分析 | Field Curvature & Distortion**: 支持多波长分析，与Zemax风格一致
  *Multi-wavelength analysis, consistent with Zemax style visualization*
  
- ✅ **综合分析 | Comprehensive Analysis**: 在一张图中集成MTF、点列图和光线扇形图
  *Integration of MTF, spot diagrams, and ray fans in a single comprehensive figure*
  
- ✅ **一键分析 | One-Click Analysis**: 一行代码生成所有分析类型的完整报告
  *Generate complete reports of all analysis types with a single line of code*

---

## 🚀 快速开始 | Quick Start

### ✨ 一行代码完成全部分析 | One Line for Complete Analysis

```python
from zosapi_core import ZOSAPIManager
from zosapi_plotting import analyze_and_plot_system

# 连接到Zemax | Connect to Zemax
zos_manager = ZOSAPIManager()

# 可选：加载系统文件 | Optional: Load system file
# zos_manager.open_file("your_system.zos")

# 一键分析图表 | One-click analysis and charts  
saved_files = analyze_and_plot_system(zos_manager, output_dir="analysis_results")
print("✅ 分析完成！| Analysis completed!", saved_files)
```

### 🎯 单独分析功能 | Individual Analysis Functions

```python
from zosapi_analysis import ZOSAnalyzer
from zosapi_plotting import plot_spots, plot_rayfan, plot_field_curvature_distortion

analyzer = ZOSAnalyzer(zos_manager)

# 点列图分析 | Spot diagram analysis
plot_spots(zos_manager, analyzer, 
           fields="all", wavelengths="all",
           save_path="spots.png")

# Ray Fan分析 | Ray fan analysis
plot_rayfan(zos_manager, analyzer,
            fields="all", wavelengths="single", 
            save_path="rayfan.png")
            
# 场曲和畸变分析 | Field curvature and distortion analysis
plot_field_curvature_distortion(zos_manager, analyzer,
                               wavelengths="all",
                               save_path="field_curvature.png")
```

---

## 🔧 特点与优化 | Features and Optimizations

### ✅ 专业点列图分析 | Professional Spot Diagram Analysis
- 使用 `constrained_layout=True` 确保所有子图物理尺寸一致
  *Using `constrained_layout=True` to ensure consistent physical dimensions for all subplots*
- 正确的 `aspect='equal'` 设置，真实反映光斑形状和大小
  *Proper `aspect='equal'` setting to accurately reflect spot shape and size*
- 支持多视场、多波长分析，颜色编码清晰
  *Support for multi-field, multi-wavelength analysis with clear color coding*

### ✅ 精确Ray Fan分析 | Precise Ray Fan Analysis
- 完整支持X/Y方向光线扇形图分析
  *Complete support for X/Y direction ray fan analysis*
- 数据提取和处理与Zemax原生结果完全一致
  *Data extraction and processing perfectly consistent with native Zemax results*
- 支持不同视场、波长的组合分析
  *Support for combined analysis of different fields and wavelengths*

### ✅ 场曲与畸变分析 | Field Curvature & Distortion Analysis
- 支持多波长场曲分析，色彩区分不同波长
  *Multi-wavelength field curvature analysis with color differentiation*
- 切向/弧矢场曲使用实线/虚线区分
  *Tangential/Sagittal field curvatures distinguished by solid/dashed lines*
- Zemax风格的坐标系与显示方式
  *Zemax-style coordinate system and display method*

### ✅ 全面的系统分析 | Comprehensive System Analysis
- 一键生成包含MTF、点列图、光线扇形图的综合分析
  *One-click generation of comprehensive analysis including MTF, spot diagrams, and ray fans*
- 专业的图表样式与标签，适合论文和报告
  *Professional chart style and labeling suitable for papers and reports*
- 高DPI输出（300 DPI），图像质量优秀
  *High DPI output (300 DPI) with excellent image quality*

---

## 🧪 使用示例 | Usage Examples

### 🔍 全面系统分析 | Comprehensive System Analysis
```python
from zosapi_core import ZOSAPIManager
from zosapi_plotting import analyze_and_plot_system

# 初始化 | Initialize
zos_manager = ZOSAPIManager()
zos_manager.open_file("your_optical_system.zos")

# 全面分析 | Comprehensive analysis
results = analyze_and_plot_system(zos_manager, "output_folder")

# 输出结果 | Output results
print("生成的文件 | Generated files:")
for analysis_type, path in results.items():
    print(f"- {analysis_type}: {path}")
```

### 🎛️ 自定义分析参数 | Custom Analysis Parameters
```python
from zosapi_analysis import ZOSAnalyzer
from zosapi_plotting import plot_spots, plot_rayfan, plot_mtf

analyzer = ZOSAnalyzer(zos_manager)

# 特定视场与波长 | Specific fields and wavelengths
plot_spots(zos_manager, analyzer,
          fields=[0, 2], wavelengths=[1],  # 特定视场和波长索引 | Specific field and wavelength indices
          save_path="custom_spots.png")

# 主波长的Ray Fan | Ray fan for primary wavelength
plot_rayfan(zos_manager, analyzer,
           fields="all", wavelengths="single",
           save_path="primary_rayfan.png")

# 自定义MTF频率范围 | Custom MTF frequency range
plot_mtf(zos_manager,
        max_frequency=150,  # 自定义最大空间频率 | Custom maximum spatial frequency
        save_path="extended_mtf.png")
```

---

## 📊 功能详解 | Function Details

### 1. 点列图分析 | Spot Diagram Analysis
```python
# 多视场多波长点列图 | Multi-field, multi-wavelength spot diagrams
plot_spots(zos_manager, analyzer, 
           fields="all",         # "all", "single", [0,1,2]
           wavelengths="all",    # "all", "single", [0,1,2]
           save_path="spots.png")
```

### 2. Ray Fan分析 | Ray Fan Analysis
```python  
# X/Y方向像差曲线 | X/Y aberration curves
plot_rayfan(zos_manager, analyzer,
           fields="all", 
           wavelengths="single",
           save_path="rayfan.png")
```

### 3. MTF分析 | MTF Analysis
```python
# 调制传递函数分析 | Modulation transfer function analysis
plot_mtf(zos_manager, 
        fields="all", 
        wavelengths="all", 
        max_frequency=100,
        save_path="mtf.png")
```

### 4. 场曲与畸变分析 | Field Curvature & Distortion Analysis
```python
# 场曲和畸变 | Field curvature and distortion
plot_field_curvature_distortion(zos_manager, analyzer,
                               wavelengths="all",  # 支持多波长分析 | Supports multi-wavelength analysis
                               save_path="field_curvature.png")
```

### 5. 综合分析 | Comprehensive Analysis
```python
# 综合分析图表 | Comprehensive analysis chart
plot_mtf_spot_ranfan(zos_manager, analyzer,
                    fields="all", 
                    wavelengths="all",
                    save_path="comprehensive.png")
```

### 6. 一键完成所有分析 | One-Click Complete Analysis
```python
# 一行代码完成所有分析 | All analyses with one line of code
saved_files = analyze_and_plot_system(zos_manager, 
                                     output_dir="results",
                                     fields="all",
                                     wavelengths="all")
```

---

## 📁 项目结构 | Project Structure

```
zosapi/
├── 📄 zosapi_core.py          # ZOSAPI连接管理 | ZOSAPI connection management
├── 🔬 zosapi_analysis.py      # 分析功能实现 | Analysis functionality implementation
├── 📊 zosapi_plotting.py      # 绘图和可视化 | Plotting and visualization
├── 🛠️ zosapi_utils.py         # 工具函数 | Utility functions
├── 📑 config.py               # 配置文件 | Configuration
├── 📝 __init__.py             # 包初始化 | Package initialization
├── 📚 USAGE_GUIDE.md          # 详细使用说明 | Detailed usage guide
├── 📋 README.md               # 项目说明（本文件）| Project description (this file)
├── 📂 zosapi_output/          # 输出目录 | Output directory
│   ├── comprehensive_analysis.png
│   ├── field_curvature_distortion.png
│   ├── multifield_rayfan.png
│   ├── multifield_spots.png
│   └── system_mtf.png
└── 📂 sample/                 # 官方示例代码 | Official sample code
    ├── PythonStandalone_22_seq_spot_diagram.py
    ├── PythonStandalone_23_ray_fan_native_manual_comparison.py
    └── ...
```

---

## 📸 输出示例 | Output Examples

分析完成后自动生成以下文件 | After analysis, the following files are automatically generated:

- `multifield_spots.png` - 多视场点列图 | Multi-field spot diagrams
  *物理尺寸一致，清晰显示不同视场和波长下的光斑分布*
  *Consistent physical dimensions, clearly showing spot distributions across different fields and wavelengths*

- `multifield_rayfan.png` - 多视场光线扇形图 | Multi-field ray fan plots
  *X/Y方向像差曲线，与Zemax原生结果完全一致*
  *X/Y aberration curves, perfectly consistent with native Zemax results*

- `system_mtf.png` - 系统MTF曲线 | System MTF curves
  *切向/弧矢MTF分析，包含所有视场点*
  *Tangential/Sagittal MTF analysis, including all field points*

- `field_curvature_distortion.png` - 场曲和畸变分析 | Field curvature and distortion analysis
  *支持多波长分析，采用Zemax风格坐标系*
  *Multi-wavelength analysis with Zemax-style coordinate system*

- `comprehensive_analysis.png` - 综合分析图 | Comprehensive analysis
  *集成MTF、点列图和光线扇形图的综合分析*
  *Integrated analysis of MTF, spot diagrams, and ray fans*

---

## 🔬 技术特点 | Technical Features

### 🎯 数据精度 | Data Accuracy
- 所有分析结果与Zemax原生功能完全一致
  *All analysis results fully consistent with native Zemax functionality*
- 严格按照Zemax数据提取API实现
  *Strictly implemented according to Zemax data extraction API*
- 完善的数据验证与错误处理机制
  *Comprehensive data validation and error handling mechanisms*

### 🖼️ 图像质量 | Image Quality
- 高DPI输出（300 DPI），适合论文和报告
  *High DPI output (300 DPI), suitable for papers and reports*
- 专业的图表样式、布局和标签
  *Professional chart styles, layouts and labels*
- 物理尺寸和比例完全准确
  *Physically accurate dimensions and proportions*

### 💻 代码质量 | Code Quality
- 模块化设计，易于扩展和维护
  *Modular design for easy extension and maintenance*
- 完整的类型注解和文档字符串
  *Complete type annotations and docstrings*
- 详细的日志记录和错误处理
  *Detailed logging and error handling*

### 🌐 用户友好 | User Friendly
- 简单直观的API，一行代码完成复杂分析
  *Simple intuitive API, complex analysis with one line of code*
- 灵活的参数控制，支持自定义分析
  *Flexible parameter control, supporting customized analysis*
- 详尽的文档和使用示例
  *Comprehensive documentation and usage examples*

---

## 📚 详细文档 | Detailed Documentation

👉 **[查看完整使用指南 | View Complete Usage Guide](USAGE_GUIDE.md)** 获取 | to get:
- 详细的API文档和参数说明
  *Detailed API documentation and parameter descriptions*
- 完整的使用示例和最佳实践
  *Complete usage examples and best practices*
- 故障排除指南和常见问题
  *Troubleshooting guide and FAQ*
- 函数与方法的详细说明
  *Detailed descriptions of functions and methods*

---

## 🛠️ 环境要求 | Environment Requirements

- **Python**: 3.7+ 
- **Zemax OpticStudio**: 需要运行中，支持ZOSAPI
  *Must be running with ZOSAPI support*
- **Python包 | Python packages**: matplotlib, numpy, logging
- **操作系统 | Operating system**: Windows (Zemax requirement)

---

## 📈 版本历史 | Version History

### 🎉 v1.0 (当前版本 | Current version) - 2025年6月30日
- ✅ **完整实现 | Complete implementation**: 点列图、光线扇形图、MTF和场曲分析功能
  *Spot diagrams, ray fans, MTF and field curvature analysis functionality*
- ✅ **特色功能 | Special features**: 多波长场曲分析，与Zemax风格一致的显示
  *Multi-wavelength field curvature analysis, Zemax-style visualization*
- ✅ **优化改进 | Optimizations**: 点列图物理尺寸一致性，专业的图表布局
  *Consistent physical dimensions for spot diagrams, professional chart layouts*
- ✅ **综合分析 | Comprehensive analysis**: 一键生成完整的光学系统分析报告
  *One-click generation of complete optical system analysis reports*
- ✅ **文档完善 | Documentation**: 中英文双语文档，详细的API参考
  *Bilingual documentation in Chinese and English, detailed API reference*

---

## 🎯 开始使用 | Getting Started

1. **连接Zemax | Connect to Zemax**: 创建`ZOSAPIManager`实例
   *Create a `ZOSAPIManager` instance*
2. **快速分析 | Quick analysis**: 使用`analyze_and_plot_system()`一键分析
   *Use `analyze_and_plot_system()` for one-click analysis*
3. **自定义分析 | Custom analysis**: 使用单独的分析函数，如`plot_spots()`，`plot_rayfan()`等
   *Use individual analysis functions like `plot_spots()`, `plot_rayfan()`, etc.*
4. **查看结果 | View results**: 分析结果保存在指定目录，包含专业图表
   *Analysis results are saved in the specified directory, including professional charts*

**立即开始 | Start now**: 🚀 `from zosapi_plotting import analyze_and_plot_system`

---

## 🚀 参数说明 | Parameter Guide

### 🔍 通用参数 | Common Parameters

所有分析函数共享以下参数模式 | All analysis functions share the following parameter patterns:

**视场选择 | Field Selection:**
- `"all"` - 所有视场 | All fields
- `"single"` - 单视场(第一个) | Single field (first)
- `[0, 1, 2]` - 自定义视场索引 | Custom field indices (0-based)

**波长选择 | Wavelength Selection:**
- `"all"` - 所有波长 | All wavelengths
- `"single"` - 主波长 | Primary wavelength
- `[0, 1, 2]` - 自定义波长索引 | Custom wavelength indices (0-based)

**示例 | Example:**
```python
# 选择特定视场和波长 | Select specific fields and wavelengths
plot_spots(zos_manager, analyzer,
          fields=[0, 2],          # 第1和第3视场 | 1st and 3rd fields
          wavelengths="single",   # 主波长 | Primary wavelength
          save_path="custom_spots.png")
```

### 📊 函数特有参数 | Function-Specific Parameters

**场曲与畸变分析 | Field Curvature & Distortion Analysis:**
```python
# 场曲和畸变分析支持多波长，并使用Zemax风格坐标系
# Field curvature and distortion analysis supports multiple wavelengths and uses Zemax-style coordinate system
plot_field_curvature_distortion(zos_manager, analyzer,
                               wavelengths="all",  # 分析所有波长 | Analyze all wavelengths
                               save_path="field_curves.png")
```

**MTF分析 | MTF Analysis:**
```python
# MTF分析允许设置最大空间频率
# MTF analysis allows setting maximum spatial frequency
plot_mtf(zos_manager,
        fields="all",
        wavelengths="all",
        max_frequency=150,  # 设置最大空间频率 | Set maximum spatial frequency
        save_path="high_freq_mtf.png")
```

## 📈 实际应用示例 | Practical Application Examples

### 📋 完整光学系统分析 | Complete Optical System Analysis

```python
from zosapi_core import ZOSAPIManager
from zosapi_plotting import analyze_and_plot_system

# 初始化连接 | Initialize connection
zos_manager = ZOSAPIManager()

# 加载光学设计文件 | Load optical design file
zos_manager.open_file("your_optical_design.zos")

# 一键分析并生成所有结果 | One-click analysis and generate all results
results = analyze_and_plot_system(zos_manager, "./analysis_results")
print("📊 分析完成！| Analysis complete!")

# 输出生成的文件路径 | Output generated file paths
for analysis_type, file_path in results.items():
    print(f"- {analysis_type}: {file_path}")
```

*🌟 如果这个项目对您有帮助，欢迎分享和贡献！| If this project is helpful to you, please feel free to share and contribute!*
---

## 📊 效率对比 | Efficiency Comparison

### 🔴 传统方式 | Traditional Way (150+ 行代码)
```python
# 手动编写matplotlib代码进行MTF分析
# Manual matplotlib code for MTF analysis
mtf_analysis = system.Analyses.New_FftMtf()
# ... 30+ 行设置和绘图代码 | 30+ lines setup & plotting ...

# 手动编写matplotlib代码进行点列图分析  
# Manual matplotlib code for spot diagram analysis
fig, axes = plt.subplots(n_rows, n_cols, figsize=(...))
# ... 50+ 行子图管理代码 | 50+ lines subplot management ...
# ... 需要手动处理多波长循环 | Manual multi-wavelength loops ...
# ... 需要手动管理颜色和图例 | Manual color & legend management ...

# 手动编写光线扇形图分析代码
# Manual ray fan analysis code
# ... 另外50+ 行 | Another 50+ lines ...
```

### 🟢 新方式 | New Way (1 行代码)
```python
# 一行搞定全部！| One line for everything!
analyze_and_plot_system(zos_manager, "./results", "all", "all")

# 或分别调用 | Or call individually:
plot_mtf(zos_manager, fields="all", wavelengths="all", save_path="mtf.png")
plot_spots(zos_manager, analyzer, fields="all", wavelengths="all", save_path="spots.png")
```

**结果：95%代码减少！现在可以专注于光学设计而不是绘图代码！**  
*Result: 95% code reduction! Focus on optical design, not plotting code!*

---

## 📁 模块结构 | Module Structure

```
zosapi/
├── zosapi_core.py           # 核心连接管理 | Core connection management
├── zosapi_analysis.py       # 光学分析 | Optical analysis (based on official examples)
├── zosapi_plotting.py       # 专业绘图 | Professional plotting (English interface)
├── zosapi_utils.py          # 数据处理工具 | Data processing utilities
├── auto_optimizer.py        # 自动优化工具 | Auto optimization tools
├── config.py                # 配置文件 | Configuration
├── test_with_sample.py      # 极简测试 | Ultra-simple test (65 lines)
└── sample/                  # 官方例程 | Official examples
    ├── PythonStandalone_22_seq_spot_diagram.py
    ├── PythonStandalone_23_ray_fan_native_manual_comparison.py
    └── PythonStandalone_04_pull_data_from_FFTMTF.py
```

---

## 🚀 快速开始 | Quick Start

### 1. 基础连接和分析 | Basic Connection & Analysis

```python
from zosapi_core import ZOSAPIManager
from zosapi_analysis import ZOSAnalyzer

# 连接到 OpticStudio | Connect to OpticStudio
zos_manager = ZOSAPIManager()
print("✅ Connected to Zemax OpticStudio")

# 可选：打开文件 | Optional: Open file
# zos_manager.open_file("your_file.zos")

# 创建分析器 | Create analyzer
analyzer = ZOSAnalyzer(zos_manager)

# 分析点列图 (基于官方例程22) | Spot analysis (based on official example 22)
spot_data = analyzer.analyze_spot_diagram(field_index=0, wavelength_index=0)
print(f"RMS Radius: {spot_data['rms_radius']:.6f} mm")

# 分析MTF (基于官方例程4) | MTF analysis (based on official example 4)
mtf_data = analyzer.analyze_mtf(field_index=0, max_frequency=50)
print(f"MTF at Nyquist: {mtf_data['mtf_tangential'][-1]:.3f}")
```

### 2. 批量分析 | Batch Analysis

```python
from zosapi_plotting import analyze_and_plot_system

# 一行式全自动分析 | One-line automated analysis
saved_files = analyze_and_plot_system(zos_manager, "./output")

print("Analysis completed! Generated plots:")
for analysis_type, file_path in saved_files.items():
    print(f"  - {analysis_type}: {file_path}")
```

---

## 🔧 核心分析功能 | Core Analysis Functions

### ZOSAnalyzer 主要方法 | Main Methods

- `analyze_spot_diagram()` - 点列图分析 | Spot diagram analysis
- `analyze_mtf()` - MTF分析 | MTF analysis  
- `analyze_ray_fan()` - 光线扇形图分析 | Ray fan analysis
- `analyze_wavefront()` - 波前分析 | Wavefront analysis
- `optimize_system()` - 系统优化 | System optimization
- `quick_focus()` - 快速聚焦 | Quick focus

### 高级绘图函数 | Advanced Plotting Functions

- `plot_spots()` - 多视场点列图 | Multi-field spot diagrams
- `plot_rayfan()` - 多视场光线扇形图 | Multi-field ray fans
- `plot_mtf()` - 系统MTF分析 | System MTF analysis
- `plot_mtf_spot_ranfan()` - 综合分析图 | Comprehensive analysis
- `analyze_and_plot_system()` - 一键全分析 | One-click complete analysis

---

## ⚙️ 依赖要求 | Requirements

- **Python <=3.8,pythonnet==2.5.2**
- **Zemax OpticStudio** (支持Python API | with Python API support)
- **matplotlib** (绘图 | plotting)
- **numpy** (数值计算 | numerical computation)

```bash
pip install matplotlib numpy
```

---

## 📝 使用注意事项 | Important Notes

1. **许可证要求** | License: 需要有效的Zemax OpticStudio许可证且支持API使用
2. **路径设置** | Path: 确保Zemax OpticStudio正确安装且路径可访问
3. **真实数据** | Real Data: 所有分析均基于真实Zemax计算，无仿真数据
4. **英文界面** | English Interface: 所有图表、标签、输出均为英文

---

## 🎯 设计理念 | Design Philosophy

**"让复杂的光学分析变得像调用一个函数一样简单"**  
*"Make complex optical analysis as simple as calling a function"*

- ✅ **极简接口** | Minimal Interface: 一行代码完成复杂分析
- ✅ **专业输出** | Professional Output: 高质量图表，符合工程标准
- ✅ **官方兼容** | Official Compatibility: 严格按照官方例程实现
- ✅ **模块化设计** | Modular Design: 易于扩展和维护
- ✅ **无仿真数据** | No Simulation: 100%真实Zemax分析结果

---

**现在您可以专注于光学设计本身，而不是繁琐的代码编写！**  
*Now you can focus on optical design itself, not tedious code writing!*

