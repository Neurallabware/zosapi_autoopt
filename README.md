
# ZOSAPI Auto-Opt

**厌倦了为Zemax编写上百行重复的分析和绘图代码？这个库让你回归光学设计本身。**

ZOSAPI Auto-Opt 是一个为Zemax OpticStudio深度定制的Python自动化引擎，它将复杂、繁琐的API调用封装成简单、直观的函数。无论是生成全套分析报告，还是执行多重优化策略，现在都只需一行代码。

-----

## 亮点功能 | Highlights

  - **一行代码，完整报告**: 调用`analyze_and_plot_system()`，立刻获得与Zemax风格一致的全套分析图表（MTF、点列图、光扇图等）。
  - **专业级优化引擎**: 内置“局部-全局-锤形”多重优化策略，将复杂的手动优化流程自动化。
  - **直观的评价函数**: 使用`Op.EFFL`, `Op.MNCG`等常量替代难记的操作数代码，像写公式一样构建评价函数。
  - **高质量布局导出**: 轻松导出现成的2D截面图和3D着色模型图，可直接用于论文或报告。

-----

## 效率对比 | Before vs. After

**传统方式 (手动编写, \>150行代码):**

```python
# 手动编写matplotlib代码进行MTF分析
mtf_analysis = system.Analyses.New_FftMtf()
# ... 30+ 行设置和绘图代码 ...

# 手动编写matplotlib代码进行点列图分析  
fig, axes = plt.subplots(...)
# ... 50+ 行子图、颜色、图例管理代码 ...

# 手动编写光线扇形图分析代码
# ... 另外50+ 行代码 ...
```

**使用本库 (1行代码):**

```python
# 一行搞定全部！
analyze_and_plot_system(zos_manager, "./results")
```

**结果：95%的代码减少！现在，您可以专注于光学设计，而不是调试绘图代码！**

-----

## 快速上手 | Quick Start

### 1\. 一键分析与绘图

这是展示本库核心价值的最快方式。

```python
from zosapi_autoopt.zosapi_core import ZOSAPIManager
from zosapi_autoopt.zosapi_plotting import ZOSPlotter # 实际调用的是 ZOSPlotter 里的方法

# 1. 连接到Zemax
zos = ZOSAPIManager()
zos.open_file("C:/.../your_lens_file.zos")

# 2. 创建绘图器
plotter = ZOSPlotter(zos)

# 3. 一键生成所有图表
saved_files = plotter.analyze_and_plot_system(output_dir="output/my_first_report")

print("分析报告已生成:", saved_files)
zos.close()
```

### 2\. 自动化优化

体验从设置变量到多重优化的强大流程。

```python
from zosapi_autoopt import ZOSAPIManager, LensDesignManager, MeritFunctionEditor

zos = ZOSAPIManager()
zos.open_file("C:/.../your_lens_file.zos")

# 1. 设置变量
lde = LensDesignManager(zos)
lde.set_variable(surface_pos=1, param_name='radius')
lde.set_variable(surface_pos=2, param_name='thickness')

# 2. 快速构建评价函数
mf = MeritFunctionEditor(zos)
mf.use_optimization_wizard('rms_spot') # 使用RMS光斑优化向导
mf.add_operand(mf.Operands.TOTR, target=80.0, weight=1.0) # 添加一个总长控制

# 3. 运行优化！
result = mf.run_local_optimization(timeout_seconds=60)
print(f"优化完成! 最终评价值: {result['final_merit']:.6f}")

zos.save_file("output/optimized_lens.zos")
zos.close()
```

-----

## 功能展示 | Showcase

### 专业的分析图表

所有图表均采用高DPI (300)输出，风格与Zemax保持一致，可直接用于正式报告。

  * **`system_mtf.png`**: 系统MTF曲线 (切向/弧矢，多视场)
  * **`multifield_spots.png`**: 多视场点列图 (物理尺寸精确，多波长叠加)
  * **`multifield_rayfan.png`**: 多视场光线扇形图 (X/Y方向)
  * **`field_curvature_distortion.png`**: 场曲与畸变图
  * **`comprehensive_analysis.png`**: 集成MTF、点列图、光扇图的综合分析大图

### 高质量系统布局

使用`ZOSLayoutAnalyzer`模块轻松导出。

```python
from zosapi_autoopt import ZOSLayoutAnalyzer

layout_analyzer = ZOSLayoutAnalyzer(zos)

# 导出2D截面图
layout_analyzer.export_cross_section(
    save_path="output/layout_2D.png",
    color_rays_by='Wavelength' # 按波长为光线上色
)

# 导出3D着色模型
layout_analyzer.export_shaded_model("output/layout_3D.png")
```

![05c6a72c23724665377b4607d17b6b5](https://pppppall.oss-cn-guangzhou.aliyuncs.com/undefined05c6a72c23724665377b4607d17b6b5.png)

-----

## 环境要求 | Requirements

  - **Python**: 3.8+
  - **核心库**: `pythonnet==2.5.2`, `matplotlib`, `numpy`
  - **Zemax OpticStudio**: 任何支持ZOS-API的版本 (需在后台运行)
  - **操作系统**: Windows