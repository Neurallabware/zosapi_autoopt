# Zemax OpticStudio Python API 示例集合

本文件夹包含了使用 Zemax OpticStudio ZOS-API 进行光学系统设计和分析的 Python 示例代码。这些示例展示了如何通过 Python 编程接口与 Zemax OpticStudio 进行交互，实现光学系统的自动化设计、分析和优化。

## 环境要求

- Zemax OpticStudio (v242 或更高版本)
- Python 3.x
- .NET Framework
- 必要的 Python 包：
  - `matplotlib` (用于绘图)
  - `numpy` (用于数值计算)

## 文件功能说明

### 基础操作类示例

#### `PythonStandalone_01_new_file_and_quickfocus.py`
- **功能**: 演示如何创建新文件并执行快速对焦
- **主要内容**: 
  - 建立与 OpticStudio 的连接
  - 创建新的光学系统
  - 执行快速对焦功能
- **适用场景**: 初学者入门，了解基本的 API 连接和操作

#### `PythonStandalone_03_open_file_and_optimise.py`
- **功能**: 打开现有文件并执行光学系统优化
- **主要内容**:
  - 加载现有光学系统文件
  - 设置优化参数和目标函数
  - 执行 Hammer 优化算法
  - 添加像差约束（球差、彗差等）
- **适用场景**: 光学系统设计优化

### 非序列光线追迹 (NSC) 示例

#### `PythonStandalone_02_NSC_ray_trace.py`
- **功能**: 非序列光线追迹示例
- **主要内容**:
  - 打开非序列光学系统
  - 执行光线追迹分析
  - 使用 matplotlib 可视化结果
- **适用场景**: 照明系统设计、散射分析

#### `PythonStandalone_06_nsc_phase.py`
- **功能**: 非序列系统相位分析
- **主要内容**:
  - 创建非序列光学系统
  - 添加光学元件
  - 进行相位分析和可视化
- **适用场景**: 波前分析、干涉仪设计

#### `PythonStandalone_08_NSCEDetectorData.py`
- **功能**: 非序列探测器数据分析
- **主要内容**:
  - 设置非序列探测器
  - 获取探测器数据
  - 数据后处理和分析
- **适用场景**: 照明均匀性分析、光能分布分析

#### `PythonStandalone_09_NSC_CAD.py`
- **功能**: 非序列 CAD 文件导入和处理
- **主要内容**:
  - 导入 CAD 模型到非序列系统
  - 设置 CAD 对象参数
  - 光学分析
- **适用场景**: 复杂机械结构的光学分析

#### `PythonStandalone_10_NSC_ZRD_filter_string.py`
- **功能**: 非序列光线数据库文件过滤
- **主要内容**:
  - 读取 ZRD 光线数据文件
  - 应用过滤条件
  - 提取特定光线信息
- **适用场景**: 大量光线数据的筛选和分析

#### `PythonStandalone_17_NSC_BulkScatter.py`
- **功能**: 非序列体散射分析
- **主要内容**:
  - 设置体散射参数
  - 执行散射光线追迹
  - 分析散射光分布
- **适用场景**: 散射材料分析、杂散光分析

#### `PythonStandalone_24_nsc_detectors.py`
- **功能**: 非序列多探测器系统
- **主要内容**:
  - 设置多个探测器
  - 同时分析多个探测器数据
  - 比较不同位置的光强分布
- **适用场景**: 多通道光学系统设计

### 序列光学系统 (SEQ) 示例

#### `PythonStandalone_11_BASIC_SEQ.py`
- **功能**: 序列系统基础操作
- **主要内容**:
  - 创建基本序列光学系统
  - 设置透镜参数
  - 执行基础光学分析
  - 设置矩形光阑
- **适用场景**: 传统光学系统设计入门

#### `PythonStandalone_12_SEQ_SystemExplorer.py`
- **功能**: 序列系统探索器功能
- **主要内容**:
  - 系统数据管理
  - 波长和视场设置
  - 环境参数配置
  - 文件和单位管理
- **适用场景**: 系统参数批量设置和管理

#### `PythonStandalone_15_Seq_Optimization.py`
- **功能**: 序列系统优化
- **主要内容**:
  - 加载双高斯设计
  - 设置优化目标和约束
  - 执行多种优化算法
  - 分析优化结果
- **适用场景**: 复杂光学系统优化设计

#### `PythonStandalone_19_Surface_Properties.py`
- **功能**: 表面属性设置和管理
- **主要内容**:
  - 设置表面曲率和厚度
  - 材料属性配置
  - 坐标变换操作
- **适用场景**: 精细的光学元件参数控制

#### `PythonStandalone_22_seq_spot_diagram.py`
- **功能**: 序列系统点图分析
- **主要内容**:
  - 生成点图分析
  - 设置光线密度参数
  - 点图数据提取和可视化
- **适用场景**: 成像质量评估

#### `PythonStandalone_23_ray_fan_native_manual_comparison.py`
- **功能**: 光线扇图原生与手动计算对比
- **主要内容**:
  - 执行光线扇图分析
  - 手动光线追迹计算
  - 结果对比验证
- **适用场景**: 算法验证、深入理解光线追迹原理

### 数据分析示例

#### `PythonStandalone_04_pull_data_from_FFTMTF.py`
- **功能**: FFT MTF 数据提取和分析
- **主要内容**:
  - 执行 FFT MTF 分析
  - 提取调制传递函数数据
  - 使用 matplotlib 绘制 MTF 曲线
- **适用场景**: 成像系统质量评估

#### `PythonStandalone_05_Read_ZRD_File.py`
- **功能**: 光线数据库文件读取
- **主要内容**:
  - 生成和保存 ZRD 文件
  - 逐光线读取数据
  - 提取光线段详细信息
- **适用场景**: 详细光线路径分析

#### `PythonStandalone_25_source_spectrum_diffraction_grating.py`
- **功能**: 光源光谱和衍射光栅分析
- **主要内容**:
  - 设置宽光谱光源
  - 建立衍射光栅模型
  - 分析光谱分散特性
- **适用场景**: 光谱仪器设计

### 高级功能示例

#### `PythonStandalone_07_TiltDecenterAndMFOperand.py`
- **功能**: 倾斜偏心和优化函数操作
- **主要内容**:
  - 设置表面倾斜和偏心
  - 使用优化函数操作数
  - 公差分析相关操作
- **适用场景**: 公差分析、装配误差影响研究

#### `PythonStandalone_14_Seq_Tolerance.py`
- **功能**: 序列系统公差分析
- **主要内容**:
  - 设置公差参数
  - 执行蒙特卡洛公差分析
  - 统计分析结果
- **适用场景**: 制造公差对系统性能影响评估

#### `PythonStandalone_18_SetMultiConfiguration.py`
- **功能**: 多配置系统设置
- **主要内容**:
  - 创建多配置系统
  - 设置配置间参数变化
  - 热效应建模
- **适用场景**: 变焦系统、多工作条件系统设计

#### `PythonStandalone_20_export_CAD_File.py`
- **功能**: CAD 文件导出
- **主要内容**:
  - 将光学系统导出为 CAD 格式
  - 设置导出参数
  - 机械接口设计
- **适用场景**: 光机集成设计

#### `PythonStandalone_21_White_LED_Phosphor.py`
- **功能**: 白光 LED 荧光粉建模
- **主要内容**:
  - LED 光源建模
  - 荧光粉转换过程模拟
  - 白光光谱分析
- **适用场景**: 照明系统设计、LED 封装设计

### 系统配置示例

#### `PythonStandalone_26_modify_opticstudio_preferences.py`
- **功能**: 修改 OpticStudio 软件偏好设置
- **主要内容**:
  - 读取和修改软件全局设置
  - 日期时间格式配置
  - 文件编码设置
- **适用场景**: 批量软件配置管理

#### `PythonStandalone_26_modify_project_preferences.py`
- **功能**: 修改项目偏好设置
- **主要内容**:
  - 项目级别参数设置
  - 环境参数配置
  - 用户偏好管理
- **适用场景**: 项目级别的标准化设置

## 使用方法

1. **环境准备**: 确保已安装 Zemax OpticStudio 和 Python 环境
2. **路径配置**: 根据实际安装路径修改代码中的 OpticStudio 路径
3. **运行示例**: 选择相应的示例文件，使用 Python 直接运行
4. **结果分析**: 大多数示例会生成图表或输出数据文件

## 代码结构

所有示例都采用相似的结构：
- `PythonStandaloneApplication` 类：处理与 OpticStudio 的连接
- 主函数：实现具体的光学分析功能
- 数据处理函数：用于结果的后处理和可视化

## 注意事项

1. 运行前请确保 Zemax OpticStudio 许可证有效
2. 某些示例需要特定的示例文件，确保 OpticStudio 示例文件完整
3. 建议按数字顺序学习，从基础示例开始
4. 运行完成后程序会自动清理连接，释放 OpticStudio 资源

## 技术支持

这些示例代码展示了 ZOS-API 的强大功能，可作为自动化光学设计和分析的起点。更多技术细节请参考 Zemax OpticStudio 官方文档和 ZOS-API 帮助文件。