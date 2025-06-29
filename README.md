# Zemax OpticStudio Python API 自动化分析库 | ZOSAPI Automation Library

**专业光学系统分析与优化封装，严格对照官方例程，支持多视场多波长分析**  
*Professional optical analysis and optimization toolkit based on official Zemax examples*

---

## 🎯 核心功能 | Core Features

- **📈 一行式分析** | One-Line Analysis: 完整的多视场多波长分析，仅需一行代码
- **📊 专业绘图** | Professional Plotting: 高质量光学图表，英文标签，300 DPI输出
- **🎛️ 智能控制** | Smart Control: 支持全视场/单视场/自定义视场和波长选择
- **⚡ 官方标准** | Official Standards: 严格按照官方例程22(Spot)、23(Ray Fan)、4(MTF)实现
- **🔧 模块化设计** | Modular Design: 独立的连接、分析、绘图模块，易于扩展

---

## 🚀 极简用法 | Ultra-Simple Usage

### ✨ 一行代码完成全部分析 | Complete Analysis in One Line

```python
from zosapi_core import ZOSAPIManager
from zosapi_plotting import analyze_and_plot_system

# 连接Zemax | Connect to Zemax
zos_manager = ZOSAPIManager()

# 可选：加载系统文件 | Optional: Load system file
# zos_manager.open_file("your_system.zmx")

# 🎯 一行搞定：MTF + 点列图 + 光线扇形图 + 综合分析！
# One line: MTF + Spot + Ray Fan + Comprehensive Analysis!
saved_files = analyze_and_plot_system(zos_manager, "./results")
```

### 📊 自动生成内容 | Auto-Generated Content

- **MTF曲线** | MTF Curves: 所有视场和波长的调制传递函数
- **点列图** | Spot Diagrams: 所有视场和波长的光线点列分布  
- **光线扇形图** | Ray Fan Plots: 子午/弧矢光线扇形分析
- **综合分析** | Comprehensive Analysis: 多种分析结果的汇总图表
- **专业格式** | Professional Format: 英文标签、图例、300 DPI高清输出

---

## 🎨 高级绘图函数 | Advanced Plotting Functions

```python
from zosapi_analysis import ZOSAnalyzer
from zosapi_plotting import (plot_system_mtf, plot_multifield_spots, 
                            plot_multifield_rayfan, plot_comprehensive_analysis)

analyzer = ZOSAnalyzer(zos_manager)

# 🌈 多视场多波长分析 | Multi-field Multi-wavelength Analysis
plot_multifield_spots(zos_manager, analyzer, 
                     fields="all", wavelengths="all",      # 全视场全波长
                     save_path="spots_all.png")

plot_multifield_rayfan(zos_manager, analyzer, 
                      fields="all", wavelengths="all",     # 全视场全波长  
                      save_path="rayfan_all.png")

plot_system_mtf(zos_manager, 
               fields="all", wavelengths="all",           # 全视场全波长
               save_path="mtf_all.png")

# 🎯 灵活选择控制 | Flexible Selection Control
plot_multifield_spots(zos_manager, analyzer, 
                     fields="single",      # 单视场 | Single field
                     wavelengths="all",    # 全波长 | All wavelengths
                     save_path="spots_single_field.png")

plot_multifield_spots(zos_manager, analyzer, 
                     fields=[0, 1, 2],     # 指定视场索引 | Custom field indices
                     wavelengths=[0, 2],   # 指定波长索引 | Custom wavelength indices
                     save_path="spots_custom.png")
```

### 🎛️ 参数控制说明 | Parameter Control Guide

**视场选择 | Field Selection:**
- `"all"` - 所有视场 | All fields
- `"single"` - 单视场(第一个) | Single field (first)
- `[0, 1, 2]` - 自定义视场索引 | Custom field indices (0-based)

**波长选择 | Wavelength Selection:**
- `"all"` - 所有波长 | All wavelengths
- `"single"` - 主波长 | Primary wavelength
- `[0, 1, 2]` - 自定义波长索引 | Custom wavelength indices (0-based)
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
plot_system_mtf(zos_manager, fields="all", wavelengths="all", save_path="mtf.png")
plot_multifield_spots(zos_manager, analyzer, fields="all", wavelengths="all", save_path="spots.png")
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

- `plot_multifield_spots()` - 多视场点列图 | Multi-field spot diagrams
- `plot_multifield_rayfan()` - 多视场光线扇形图 | Multi-field ray fans
- `plot_system_mtf()` - 系统MTF分析 | System MTF analysis
- `plot_comprehensive_analysis()` - 综合分析图 | Comprehensive analysis
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

