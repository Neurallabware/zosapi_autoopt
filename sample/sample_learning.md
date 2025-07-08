# 官方例程学习

zosapi是根植于.net库的编程
环境：`python3.8`、`pythonnet = 2.5.2`

## 例程1 
### PythonStandaloneApplication类
```python
class PythonStandaloneApplication(object):
    class LicenseException(Exception):
        pass
    class ConnectionException(Exception):
        pass
    class InitializationException(Exception):
        pass
    class SystemNotPresentException(Exception):
        pass

    def __init__(self, path=None):
        # determine location of ZOSAPI_NetHelper.dll & add as reference
        aKey = winreg.OpenKey(winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER), r"Software\Zemax", 0, winreg.KEY_READ)
        zemaxData = winreg.QueryValueEx(aKey, 'ZemaxRoot')
        NetHelper = os.path.join(os.sep, zemaxData[0], r'ZOS-API\Libraries\ZOSAPI_NetHelper.dll')
        winreg.CloseKey(aKey)
        clr.AddReference(NetHelper)
        import ZOSAPI_NetHelper
        
        # Find the installed version of OpticStudio
        if path is None:
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize()
        else:
            # Note -- uncomment the following line to use a custom initialization path
            isInitialized = ZOSAPI_NetHelper.ZOSAPI_Initializer.Initialize(path)
        
        # determine the ZOS root directory
        if isInitialized:
            dir = ZOSAPI_NetHelper.ZOSAPI_Initializer.GetZemaxDirectory()
        else:
            raise PythonStandaloneApplication.InitializationException("Unable to locate Zemax OpticStudio.  Try using a hard-coded path.")

        # add ZOS-API referencecs
        clr.AddReference(os.path.join(os.sep, dir, "ZOSAPI.dll"))
        clr.AddReference(os.path.join(os.sep, dir, "ZOSAPI_Interfaces.dll"))
        import ZOSAPI

        # create a reference to the API namespace
        self.ZOSAPI = ZOSAPI

        # create a reference to the API namespace
        self.ZOSAPI = ZOSAPI

        # Create the initial connection class
        self.TheConnection = ZOSAPI.ZOSAPI_Connection()

        if self.TheConnection is None:
            raise PythonStandaloneApplication.ConnectionException("Unable to initialize .NET connection to ZOSAPI")

        self.TheApplication = self.TheConnection.CreateNewApplication()
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException("Unable to acquire ZOSAPI application")

        if self.TheApplication.IsValidLicenseForAPI == False:
            raise PythonStandaloneApplication.LicenseException("License is not valid for ZOSAPI use")

        self.TheSystem = self.TheApplication.PrimarySystem
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException("Unable to acquire Primary system")

    def __del__(self):
        if self.TheApplication is not None:
            self.TheApplication.CloseApplication()
            self.TheApplication = None
        
        self.TheConnection = None
    
    def OpenFile(self, filepath, saveIfNeeded):
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException("Unable to acquire Primary system")
        self.TheSystem.LoadFile(filepath, saveIfNeeded)

    def CloseFile(self, save):
        if self.TheSystem is None:
            raise PythonStandaloneApplication.SystemNotPresentException("Unable to acquire Primary system")
        self.TheSystem.Close(save)

    def SamplesDir(self):
        if self.TheApplication is None:
            raise PythonStandaloneApplication.InitializationException("Unable to acquire ZOSAPI application")

        return self.TheApplication.SamplesDir

    def ExampleConstants(self):
        if self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusType.PremiumEdition:
            return "Premium"
        elif self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusTypeProfessionalEdition:
            return "Professional"
        elif self.TheApplication.LicenseStatus == self.ZOSAPI.LicenseStatusTypeStandardEdition:
            return "Standard"
        else:
            return "Invalid"
    
    def reshape(self, data, x, y, transpose = False):
        """Converts a System.Double[,] to a 2D list for plotting or post processing
        
        Parameters
        ----------
        data      : System.Double[,] data directly from ZOS-API 
        x         : x width of new 2D list [use var.GetLength(0) for dimension]
        y         : y width of new 2D list [use var.GetLength(1) for dimension]
        transpose : transposes data; needed for some multi-dimensional line series data
        
        Returns
        -------
        res       : 2D list; can be directly used with Matplotlib or converted to
                    a numpy array using numpy.asarray(res)
        """
        if type(data) is not list:
            data = list(data)
        var_lst = [y] * x;
        it = iter(data)
        res = [list(islice(it, i)) for i in var_lst]
        if transpose:
            return self.transpose(res);
        return res
    
    def transpose(self, data):
        """Transposes a 2D list (Python3.x or greater).  
        
        Useful for converting mutli-dimensional line series (i.e. FFT PSF)
        
        Parameters
        ----------
        data      : Python native list (if using System.Data[,] object reshape first)    
        
        Returns
        -------
        res       : transposed 2D list
        """
        if type(data) is not list:
            data = list(data)
        return list(map(list, zip(*data)))
```

### 初始化与连接
```python
if __name__ == '__main__':
    zos = PythonStandaloneApplication() # Use the default path
    
    # load local variables
    ZOSAPI = zos.ZOSAPI
    TheApplication = zos.TheApplication
    TheSystem = zos.TheSystem
    
    # creates a new API directory
    if not os.path.exists(TheApplication.SamplesDir + "\\API\\Python"):
        os.makedirs(TheApplication.SamplesDir + "\\API\\Python")
    
    # Set up primary optical system
    sampleDir = TheApplication.SamplesDir
```

### 创建系统
```python
# Make new file
testFile = os.path.join(os.sep, sampleDir, r'API\Python\e01_new_file_and_quickfocus.zos')
TheSystem.New(False)
TheSystem.SaveAs(testFile)
```

### 设置参数
```python
TheSystem.SystemData.MaterialCatalogs.AddCatalog('SCHOTT')

# Aperture
TheSystemData = TheSystem.SystemData
TheSystemData.Aperture.ApertureValue = 40

# Fields
Field_1 = TheSystemData.Fields.GetField(1)
NewField_2 = TheSystemData.Fields.AddField(0, 5.0, 1.0)

# Wavelength preset
slPreset = TheSystemData.Wavelengths.SelectWavelengthPreset(ZOSAPI.SystemData.WavelengthPreset.d_0p587)
```

### 镜头数据
```python
# Lens data
TheLDE = TheSystem.LDE
TheLDE.InsertNewSurfaceAt(2)
TheLDE.InsertNewSurfaceAt(2)
Surface_1 = TheLDE.GetSurfaceAt(1)
Surface_2 = TheLDE.GetSurfaceAt(2)
Surface_3 = TheLDE.GetSurfaceAt(3)

# Changes surface cells in LDE
Surface_1.Thickness = 50.0
Surface_2.Radius = 100.0
Surface_2.Material = 'N-BK7'

```

### Solver
```python
# Solver
Solver = Surface_3.RadiusCell.CreateSolveType(ZOSAPI.Editors.SolveType.FNumber)
SolverFNumber = Solver._S_FNumber
SolverFNumber.FNumber = 10
Surface_3.RadiusCell.SetSolveData(Solver)
```

### Quick Focus
```python
# QuickFocus
quickFocus = TheSystem.Tools.OpenQuickFocus()
quickFocus.Criterion = ZOSAPI.Tools.General.QuickFocusCriterion.SpotSizeRadial
quickFocus.UseCentroid = True
quickFocus.RunAndWaitForCompletion()
quickFocus.Close()
```

### Save and del
```python
# Save and close
TheSystem.Save()

del zos
zos = None
```

## 例程2
非序列 暂时跳过

## 例程3
主要讲如何设置operand和变量

### 设置变量
```python
Surface_1.ThicknessCell.MakeSolveVariable()
```

### operand
```python
# 获取MFE对象
TheMFE = TheSystem.MFE

# 方法1: 获取已存在的操作数
Operand_1 = TheMFE.GetOperandAt(1)

# 方法2: 插入一个新操作数
Operand_2 = TheMFE.InsertNewOperandAt(2)

# 方法3: 在末尾追加一个新操作数 (最常用)
Operand_3 = TheMFE.AddOperand()

# 更改操作数类型
Operand_1.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.ASTI)

# 设置基本属性
Operand_1.Target = 0.0
Operand_1.Weight = 10.0

# 将第3个操作数类型设为MNCA
Operand_3.ChangeType(ZOSAPI.Editors.MFE.MeritOperandType.MNCA)

# 设置它的参数：计算面1到面3之间的最小空气厚度
Operand_3.GetCellAt(2).IntegerValue = 1
Operand_3.GetCellAt(3).IntegerValue = 3 #GetCellAt是参数单元格的索引规则
```

### 优化器
```python
print('Running Local Optimization') LocalOpt = TheSystem.Tools.OpenLocalOptimization() LocalOpt.Algorithm = ZOSAPI.Tools.Optimization.OptimizationAlgorithm.DampedLeastSquares LocalOpt.Cycles = ZOSAPI.Tools.Optimization.OptimizationCycles.Automatic LocalOpt.RunAndWaitForCompletion() LocalOpt.Close()
```

## 例程4
### MTF
标准分析流程：****`New_...` -> `GetSettings` -> `Apply` -> `GetResults` -> `GetDataSeries`** 
```python
# 1.创建分析窗口
TheAnalyses = TheSystem.Analyses
newWin = TheAnalyses.New_FftMtf()

# 2.配置分析参数
# Settings
newWin_Settings = newWin.GetSettings()
newWin_Settings.MaximumFrequency = 50
newWin_Settings.SampleSize = ZOSAPI.Analysis.SampleSizes.S_256x256

# 3.运行分析
newWin.ApplyAndWaitForCompletion()

# 4.获取分析数据
newWin_Results = newWin.GetResults()

# 5.提取并处理数据
# Read and plot data series
colors = ('b','g','r','c', 'm', 'y', 'k')
for seriesNum in range(0,newWin_Results.NumberOfDataSeries, 1):
    data = newWin_Results.GetDataSeries(seriesNum)
    
    # get raw .NET data
    xRaw = data.XData.Data
    yRaw = data.YData.Data

    x = list(xRaw)
    y = zos.reshape(yRaw, yRaw.GetLength(0), yRaw.GetLength(1), True)
    
    plt.plot(x,y[0],color=colors[seriesNum])
    plt.plot(x,y[1],linestyle='--',color=colors[seriesNum])        
```

## 例程5、6
均为序列模式

## 例程7
### GetOperandValue()
```python
# 目标：获取面5的3x3全局旋转矩阵

# 1. 从计算器上选择我们要用的功能键："GLCR"
GLCR = ZOSAPI.Editors.MFE.MeritOperandType.GLCR

# 2. 准备一个空的3x3数组，用来存放计算结果
RotationMatrix = np.zeros([3, 3])

# 3. 循环9次，依次按下计算器的按键
i = 1
for x in range(0, 3):
    for y in range(0, 3):
        
        # 这就是按下等号键的操作！
        RotationMatrix[x][y] = TheSystem.MFE.GetOperandValue(GLCR, 5, i, 0, 0, 0, 0, 0, 0)
        
        i = i + 1
```

## 例程8、9、10

非序列模式

## 例程11
### 切趾(Apodization)
```image-layout-a
![image.png](https://pppppall.oss-cn-guangzhou.aliyuncs.com/undefined20250627203936.png)

![image.png](https://pppppall.oss-cn-guangzhou.aliyuncs.com/undefined20250627203943.png)

```

左图有apodization，右图没有，本质上就是光瞳位置是否均匀照明
```python
# Set Apodization Type to Gaussian, and set apodization factor to 1
TheSystemData.Aperture.ApodizationType = 1  # 0=uniform; 1=gaussian; 2=Cosine Cubed
TheSystemData.Aperture.ApodizationFactor = 1
```

### ScaleLens
```python
# Set system lens units to inches, scale all values with Scale Lens tool
ScaleLens = TheSystem.Tools.OpenScale()  # Open Scale Lens tool
# Apply Tool Settings
ScaleLens.ScaleByUnits = True
ScaleLens.ScaleToUnit = 2  # 0=mm; 1=cm; 2=in; 3=m
ScaleLens.RunAndWaitForCompletion()
ScaleLens.Close()
```

### 设置表面特定光圈
```python
# Add Rectangular Aperture to Surface 1
Surf_1 = TheSystem.LDE.GetSurfaceAt(1)
# 1. 创建光圈设置“模板”
rAperture = Surf_1.ApertureData.CreateApertureTypeSettings(ZOSAPI.Editors.LDE.SurfaceApertureTypes.RectangularAperture)
# 2. 投射到具体类型并修改参数
rAperture._S_RectangularAperture.XHalfWidth = .1
rAperture._S_RectangularAperture.YHalfWidth = .1
# 3. 应用设置
Surf_1.ApertureData.ChangeApertureTypeSettings(rAperture)
```
- **`CreateApertureTypeSettings()`**: 先创建一个您想要的光圈类型的“设置模板”，这里是`RectangularAperture`。
- **`_S_RectangularAperture`**: 将返回的通用设置对象“投射”到具体的矩形光圈类型，这样才能访问它独有的属性，如 `XHalfWidth`。
- **`ChangeApertureTypeSettings()`**: 将配置好的 `rAperture` 对象应用回表面。

## 例程12 
- 用**高斯求积(Gaussian Quadrature)**方法定义波长。
  
- 更改**视场(Field)**的定义类型。
  
- 设置系统的**偏振(Polarization)**参数。
  
- 动态地添加和移除**材料库(Material Catalogs)**。
  
- 为文件添加**标题和注释(Title/Notes)**。
  
- 指定系统默认的**外部文件(Files)**，如镀膜和散射文件。
  
- 直接更改系统的**镜头单位(Lens Units)**。
### SystemData
可以理解成系统的 控制面板，对象下有aperture、wavelength、fields等参数
### 高斯求积设置波长
```python
# 高斯求积设置波长
# Select 6 wavelengths with Gaussian Quadrature algorithm
sysWave = TheSystem.SystemData.Wavelengths
sysWave.GaussianQuadrature(0.45, 0.65, ZOSAPI.SystemData.QuadratureSteps.S6)
# 一种智能的波长采样方法。当您需要计算一个连续光谱范围（这里是0.45-0.65μm）内的平均光学性能（如平均RMS光斑）时，它会根据高斯求积算法，自动为您选择最佳的几个波长点（这里是6个点）和它们对应的权重，使得计算出的平均值最接近真实积分结果。
```
### 更改视场定义
```python
# Define fields using Paraxial Image Height
sysField = TheSystem.SystemData.Fields
sysField.SetFieldType(ZOSAPI.SystemData.FieldType.ParaxialImageHeight)

# ...
s1 = TheSystem.LDE.GetSurfaceAt(1)
s1_type = s1.GetSurfaceTypeSettings(ZOSAPI.Editors.LDE.SurfaceType.Paraxial)
s1.ChangeType(s1_type)```

### 添加/移除材料库
```python
# Add Corning Catalog and remove Schott Catalog
sysCat = TheSystem.SystemData.MaterialCatalogs
sysCat.AddCatalog("Corning")
sysCat.RemoveCatalog("Schott")
```

### 设置默认膜层文件
```python
# As default Files choose: COATING.DAT, SCATTER_PROFILE.DAT, AGB_DATA.DAT
sysFiles = TheSystem.SystemData.Files
sysFiles.CoatingFile = "COATING.DAT"
sysFiles.ScatterProfile = "SCATTER_PROFILE.DAT"

sysFiles.ReloadFiles()
```

### 直接更改镜头单位
```python
# Change lens units to inches
sysUnits = TheSystem.SystemData.Units
sysUnits.LensUnits = ZOSAPI.SystemData.ZemaxSystemUnits.Inches

# 镜头转换的另一个工具 Scale Lens
```
## 例程15
其详细流程包括：
1. 加载一个双高斯镜头文件。 
2. 设置系统参数（视场、波长等）。
3. 演示一种更安全的修改分析设置的方法（使用临时配置文件）。
4. 批量添加和移除变量，并设置拾取求解。
5. **使用“优化向导”来自动生成一个完整的、用于RMS光斑优化的评价函数**。
6. 依次运行**局部优化(Local Optimization)**、**全局搜索(Global Search)和锤形优化(Hammer Optimization)**，并对它们的功能和结果进行展示。

### 使用临时文件修改分析设置
```python
# Open a shaded model
analysis = TheSystem.Analyses.New_Analysis(ZOSAPI.Analysis.AnalysisIDM.ShadedModel)
analysis.Terminate() # 立即终止分析，我们只关心设置
analysis.WaitForCompletion()
analysisSettings = analysis.GetSettings()
# 在系统的Temp文件夹下创建CFG文件路径
cfgFile = os.environ.get('Temp') + '\\sha.cfg' 
# 保存当前设置到这个临时文件中
analysisSettings.SaveTo(cfgFile)
# ... 对临时文件进行修改 ...
analysisSettings.ModifySettings(cfgFile, 'SHA_ROTX', '90')
# 从修改后的临时文件加载设置
analysisSettings.LoadFrom(cfgFile)
# ...
# 删除用完的临时文件
if os.path.exists(cfgFile):
    os.remove(cfgFile)
analysis.ApplyAndWaitForCompletion()
```

### 批量设置变量与求解
```python
tools = TheSystem.Tools
tools.RemoveAllVariables()

tools.SetAllRadiiVariable()

# Thickness 10 pick up from 1(Pick_up)
Solver = Surface10.ThicknessCell.CreateSolveType(ZOSAPI.Editors.SolveType.SurfacePickup)
```

### 使用优化向导

```python
    TheMFE = TheSystem.MFE
    OptWizard = TheMFE.SEQOptimizationWizard

    # Optimize for smallest RMS Spot, which is "Data" = 1
    OptWizard.Data = 1
    OptWizard.OverallWeight = 1
    # Gaussian Quadrature with 3 rings (refers to index number = 2)
    OptWizard.Ring = 2
    # Set air & glass boundaries
    OptWizard.IsGlassUsed = True
    OptWizard.GlassMin = 3.0
    OptWizard.GlassMax = 15.0
    OptWizard.GlassEdge = 3.0
    OptWizard.IsAirUsed = True
    OptWizard.AirMin = 0.5
    OptWizard.AirMax = 1000.0
    OptWizard.AirEdge = 0.5
    # And click OK!
    OptWizard.Apply()
```

### 三种优化对比
#### Local optimization
```python
# Run local optimization and measure time
t = time.time() # 记录开始时间

# 1. 打开局部优化工具
LocalOpt = TheSystem.Tools.OpenLocalOptimization()

# 2. 检查工具是否成功打开 (防御性编程)
if (LocalOpt != None):

    # 3. 配置优化参数
    LocalOpt.Algorithm = ZOSAPI.Tools.Optimization.OptimizationAlgorithm.DampedLeastSquares
    LocalOpt.Cycles = ZOSAPI.Tools.Optimization.OptimizationCycles.Automatic
    LocalOpt.NumberOfCores = 8

    # 4. 打印优化前的信息
    print('Local Optimization...')
    print('Initial Merit Function ', LocalOpt.InitialMeritFunction)
    
    # 5. 执行优化，并等待其完成
    LocalOpt.RunAndWaitForCompletion()

    # 6. 打印优化后的结果
    print('Final Merit Function   ', LocalOpt.CurrentMeritFunction)
    LocalOpt.Close()

# 7. 计算并打印耗时
elapsed = time.time() - t
print('Time elapsed            ' + str(round(elapsed,3)) + 's')
```

### globalOpt
指定时间停止
```python
GlobalOptimTimeInSeconds = 5
GlobalOpt = TheSystem.Tools.OpenGlobalOptimization()

if (GlobalOpt != None):
    # ... (Algorithm, NumberOfCores 设置与局部优化类似) ...

    # 1. 打印优化前信息
    print('Global Optimization for ' + str(GlobalOptimTimeInSeconds) + ' seconds...')
    print('Initial Merit Function ', GlobalOpt.InitialMeritFunction)

    # 2. 设置要保存的优秀结果数量
    GlobalOpt.NumberToSave = ZOSAPI.Tools.Optimization.OptimizationSaveCount.Save_10
    
    # 3. 执行优化，并在指定时间后停止
    GlobalOpt.RunAndWaitWithTimeout(1 * GlobalOptimTimeInSeconds)

    # 4. 循环读取“排行榜”
    for j in range(1, 11):
        print(str(int(j)) + ': ' + str(GlobalOpt.CurrentMeritFunction(j)))
        
    # 5. 标准的停止流程
    GlobalOpt.Cancel()
    GlobalOpt.WaitForCompletion()
    GlobalOpt.Close()
```

### Hammer Optimization
```python
# run hammer optimization
HammerOptimTimeInSeconds = 5
HammerOpt = TheSystem.Tools.OpenHammerOptimization()

if (HammerOpt != None):
    # ... (Algorithm, NumberOfCores 设置类似) ...
    print('Hammer Optimization for ' + str(HammerOptimTimeInSeconds) + ' seconds...')
    print('Initial Merit Function ', HammerOpt.InitialMeritFunction)
    
    # 1. 执行优化，并在指定时间后停止
    HammerOpt.RunAndWaitWithTimeout(1 * HammerOptimTimeInSeconds)

    # 2. 读取最终结果
    print('Final Merit Function ', HammerOpt.CurrentMeritFunction)

    # 3. 标准的停止流程
    HammerOpt.Cancel()
    HammerOpt.WaitForCompletion()
    HammerOpt.Close()
```

## 例程18
这个例程的核心是掌握**多重结构编辑器 (Multi-Configuration Editor, MCE)** 的API接口。
1. **MCE是“系统状态管理器”**: 您可以把MCE想象成一个强大的状态控制表。
    - **行 (Rows)** 是**操作数(Operands)**，代表了您希望在不同状态下进行改变的系统参数（如厚度`THIC`、温度`TEMP`等）。
    - **列 (Columns)** 是**结构(Configurations)**，代表了系统的每一种特定状态（如“长焦端”、“20摄氏度”）。
2. **MCE的对象层级**: 其API结构与评价函数编辑器(MFE)非常相似：`MCE` -> `Operand` -> `Cell`。
3. **切换当前系统状态**: **`TheMCE.SetCurrentConfiguration(j)`** 是一个至关重要的命令。它告诉OpticStudio：“现在，请让整个光学系统**立即采用第j个结构列中定义的所有参数**”。
4. **MCE专属求解**: 为了实现结构间的智能关联，MCE拥有一些专属的求解类型，如`ThermalPickup` 和 `ConfigPickup`。

代码暂时用不到，省略


## 例程19
这个例程的核心是让我们掌握对LDE中表面进行精细化、批量化操作的能力。
1. **表面属性接口**: 除了直接读写LDE单元格（如`.Radius`, `.Thickness`），ZOSAPI还为“表面属性”对话框中的复杂设置提供了专门的接口。本例中的新成员是 **`...TiltDecenterData`**，它让我们可以直接控制倾斜/偏心，而无需插入坐标断点。
2. **更易读的单元格访问**: 本例介绍了一种访问LDE单元格的新方法：**`GetSurfaceCell(SurfaceColumn.Par1)`**。与之前使用数字索引的`GetCellAt(12)`相比，这种使用**枚举(Enumeration)**的方式代码可读性更强，也更健壮。
3. **高级拾取与求解**:
    **光圈拾取**: `ApertureData.PickupFrom` 让我们能将一个表面的光圈设置与另一个表面关联起来，实现一改全改。        
    **主光线法线求解**: `PickupChiefRay` 求解可以自动调整一个表面的姿态，使其始终垂直于主光线，这在放置探测器或进行光路折转时非常有用。        
4. **LDE批量操作**: 这是ZOSAPI自动化能力的集中体现。
    **`CopySurfaces()`**: 复制并粘贴一组连续的表面，用于快速创建重复性结构。        
    **`RunTool_ConvertLocalToGlobalCoordinates()`**: 将一系列“相对于前一个面”定义的表面，一键转换为“相对于某个绝对参考面”定义，便于与CAD模型整合或进行绝对位置分析。

### TheSystem
```python
# ISystemData represents the System Explorer in GUI.
# We access options in System Explorer through ISystemData in ZOS-API
TheSystemData = TheSystem.SystemData
TheSystemData.Aperture.ApertureValue = 10
TheSystemData.Aperture.AFocalImageSpace = True
TheSystemData.Wavelengths.GetWavelength(1).Wavelength = 0.55
```

### Tilt
```python
# GetSurfaceAt(surface number shown in LDE) will return an interface ILDERow
# Through property TiltDecenterData of each interface ILDERow, we can modify data in Surface Properties > Tilt/Decenter section
TheLDE.GetSurfaceAt(2).TiltDecenterData.BeforeSurfaceOrder = ZOSAPI.Editors.LDE.TiltDecenterOrderType.Decenter_Tilt
TheLDE.GetSurfaceAt(2).TiltDecenterData.BeforeSurfaceTiltX = 15
TheLDE.GetSurfaceAt(2).TiltDecenterData.AfterSurfaceTiltX = -15
TheLDE.GetSurfaceAt(3).TiltDecenterData.BeforeSurfaceTiltX = -15
TheLDE.GetSurfaceAt(3).TiltDecenterData.AfterSurfaceTiltX = 15
```

### aperture pickup
```python
# To specify an aperture to a surface, we need to first create an ISurfaceApertureType and then assign it.

# 创建-配置-应用三部曲
Rect_Aper = TheLDE.GetSurfaceAt(2).ApertureData.CreateApertureTypeSettings(ZOSAPI.Editors.LDE.SurfaceApertureTypes.RectangularAperture)
Rect_Aper._S_RectangularAperture.XHalfWidth = 10
Rect_Aper._S_RectangularAperture.YHalfWidth = 10
TheLDE.GetSurfaceAt(2).ApertureData.ChangeApertureTypeSettings(Rect_Aper)

# 光圈pickup
TheLDE.GetSurfaceAt(3).ApertureData.PickupFrom = 2
```

### chief ray solve
```python
# Set Chief Ray solves to surface 4, which is Coordinate Break
# To set a solve to a cell in editor, we need to first create a ISolveData and then assign it.
Solve_ChiefNormal = TheLDE.GetSurfaceAt(4).GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par1).CreateSolveType(ZOSAPI.Editors.SolveType.PickupChiefRay)
TheLDE.GetSurfaceAt(4).GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par1).SetSolveData(Solve_ChiefNormal)
TheLDE.GetSurfaceAt(4).GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par2).SetSolveData(Solve_ChiefNormal)
TheLDE.GetSurfaceAt(4).GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par3).SetSolveData(Solve_ChiefNormal)
TheLDE.GetSurfaceAt(4).GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par4).SetSolveData(Solve_ChiefNormal)
TheLDE.GetSurfaceAt(4).GetSurfaceCell(ZOSAPI.Editors.LDE.SurfaceColumn.Par5).SetSolveData(Solve_ChiefNormal)
```

### copy surfaces
```python
# Copy 3 surfaces starting from surface number 2 in LDE and paste to surface number 5, which will become surface number 8 after pasting.
for i in range(10):
    TheLDE.CopySurfaces(2, 3, 5)
# Save file
TheSystem.SaveAs(TheApplication.SamplesDir + '\\API\\Python\\e19_Sample_Prism_Chain.zos')
```

### Convert Local To Global Coordinates
坐标批量转换
```python
# Run tool Convert Local To Global Coordinates to convert surface #2 to surface #35 to be globally referenced to surface #1
TheLDE.RunTool_ConvertLocalToGlobalCoordinates(2, 35, 1)
TheSystem.SaveAs(TheApplication.SamplesDir + '\\API\\Python\\e19_Sample_Prism_Chain_GlobalCoordinate.zos')
```

## 例程22
此脚本的核心目标是：演示ZOSAPI中最基本、最底层的光线追迹方法——**批量光线追迹(Batch Ray Tracing)**
1. 手动定义一大批光线的初始参数（在光瞳上的位置、所属视场和波长）。
2. 将这些光线一次性“打包”追迹穿过整个光学系统。
3. 逐条读取每一根光线追迹完成后的结果，特别是它们在像面上的坐标(x,y)。
4. 使用这些原始坐标数据，**手动地**用`matplotlib`绘制出点列图。
5. 最后，打开标准的“点列图”分析窗口，提取其计算好的RMS和GEO半径等指标，用以对比验证。

### Batch Ray Trace
批量光线追迹
```python
# Set up Batch Ray Trace
raytrace = TheSystem.Tools.OpenBatchRayTrace()
nsur = TheSystem.LDE.NumberOfSurfaces
max_rays = 30
normUnPolData = raytrace.CreateNormUnpol((max_rays + 1) * (max_rays + 1), ZOSAPI.Tools.RayTrace.RaysType.Real, nsur)
```

`normUnPolData`。这个缓冲区专门用于存储我们要追迹的“标准化的、非偏振的(Normalized, Unpolarized)”真实光线(`RaysType.Real`)。我们预先为它分配了足够大的空间。

### Add Ray Trace
向缓冲区中添加光线
```python
# Adding Rays to Batch, varying normalised object height hy
normUnPolData.ClearData() # 清空缓冲区
waveNumber = wave
#for i = 1:((max_rays + 1) * (max_rays + 1))
for i in range(1, (max_rays + 1) * (max_rays + 1) + 1):

    px = np.random.random() * 2 - 1
    py = np.random.random() * 2 - 1

    while (px*px + py*py > 1):      # 确保入瞳是严格的圆形分布
        py = np.random.random() * 2 - 1
    normUnPolData.AddRay(waveNumber, hx, hy_ary[field - 1], px, py, Enum.Parse(ZOSAPI.Tools.RayTrace.OPDMode, "None"))\

raytrace.RunAndWaitForCompletion()
```

### Read Raytrace
读取追迹结果
```python
# Read batch raytrace and display results
normUnPolData.StartReadingResults()

# Python NET requires all arguments to be passed in as reference, so need to have placeholders
sysInt = Int32(1)
sysDbl = Double(1.0)

# output[0] 是一个布尔值，表示读取是否成功。

output = normUnPolData.ReadNextResult(sysInt, sysInt, sysInt,
                sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl);

while output[0]:                                                    # success
    if ((output[2] == 0) and (output[3] == 0)):                     # ErrorCode & vignetteCode
        x_ary[field - 1, wave - 1, output[1] - 1] = output[4]   # X
        y_ary[field - 1, wave - 1, output[1] - 1] = output[5]   # Y
    output = normUnPolData.ReadNextResult(sysInt, sysInt, sysInt,
                sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl);
```

### 获取RMS光斑半径，无需自己手动计算

```python
#! [e22s06_py]
# Spot Diagram Analysis Results
spot = TheSystem.Analyses.New_Analysis(ZOSAPI.Analysis.AnalysisIDM.StandardSpot)
spot_setting = spot.GetSettings()

# extract RMS & Geo spot size for field points
spot.ApplyAndWaitForCompletion()
spot_results = spot.GetResults()
print('RMS radius: %6.3f ...' % (spot_results.SpotData.GetRMSSpotSizeFor(1, 1), ...))
```

### 例程23
**对比生成“光线差扇形图(Ray Aberration Fan Plot)”的两种方法，并进行性能基准测试。**
1. **“手动”方法**: 完全利用底层的**批量光线追迹(Batch Ray Tracing)**工具，自己定义一“束”光扇，追迹它们，获取原始的像面坐标，然后手动计算出横向光线差(Deltay=y_ray−y_chief)，最后用`matplotlib`绘制出光扇图。
2. **“原生”方法**: 直接调用ZOSAPI中高级的、内置的**光扇图分析(`RayFan`)**窗口，然后从分析结果中提取已经计算好的数据系列并绘制。


### Manual Method
准备工作与基准值获取
```python
#! [e23s01_py]
max_field = 0
for i in range(1,TheSystem.SystemData.Fields.NumberOfFields + 1):
    if TheSystem.SystemData.Fields.GetField(i).Y > max_field:
        max_field = TheSystem.SystemData.Fields.GetField(i).Y
#! [e23s01_py]
# ...
#! [e23s02_py]
# Set up Batch Ray Trace
raytrace = TheSystem.Tools.OpenBatchRayTrace()
nsur = TheSystem.LDE.NumberOfSurfaces
normUnPolData = raytrace.CreateNormUnpol(max_rays + 1, ZOSAPI.Tools.RayTrace.RaysType.Real, nsur)
#! [e23s02_py]
#! [e23s03_py]
# define batch ray trace constants
hx = 0
# since python doesn't include STOP number in range, need to use STOP value slightly more than 1
py_ary = np.arange(0, 1.0001, 1 / max_rays) * 2 - 1
px = 0
max_wave = TheSystem.SystemData.Wavelengths.NumberOfWavelengths
#! [e23s03_py]
# ...
#! [e23s04_py]
# image surface number and primary wavelength
nsur = TheSystem.LDE.NumberOfSurfaces
pwav = 0
for a in range(1, TheSystem.SystemData.Wavelengths.NumberOfWavelengths + 1):
    if TheSystem.SystemData.Wavelengths.GetWavelength(a).IsPrimary == 1:
        pwav = a

# creates array of Y coordinate chief ray values
chief_ary = np.zeros(max_num_field)
for field in range(1, max_num_field + 1):
    hy = 1 if max_field == 0 else TheSystem.SystemData.Fields.GetField(field).Y / max_field
    # gets single value without using MFE (see ZPL OPEV)
    chief_ary[field - 1] = TheSystem.MFE.GetOperandValue(ZOSAPI.Editors.MFE.MeritOperandType.REAY, nsur, pwav, 0, hy , 0, 0, 0, 0)
#! [e23s04_py]
```
- **`max_field`**: 首先计算出最大的Y视场值，用于后续归一化视场坐标。
- **`OpenBatchRayTrace`, `CreateNormUnpol`**: 打开批量追迹工具，并创建一个用于存储光线数据的**缓冲区**`normUnPolData`。
- **`py_ary`**: 创建一个Numpy数组，其值为从-1到+1均匀分布的一系列数值。这将作为我们光扇的归一化光瞳Y坐标。`px`被固定为0，这就定义了一束沿着光瞳Y轴的光扇。
- **`chief_ary`**: **这是手动方法的第一步关键**。通过循环和`GetOperandValue`，我们获取了每个视场下主光线在像面上的Y坐标，存入`chief_ary`数组。这个数组是我们计算光线差的**绝对基准**。

循环追迹与数据处理
```python
for field in range(1, max_num_field + 1):
    # ... (subplot setup) ...
    hy = 1 if max_field == 0 else TheSystem.SystemData.Fields.GetField(field).Y / max_field

    for wave in range(1, max_wave + 1):
        #! [e23s05_py]
        # Adding Rays to Batch, varying normalized object height hy
        normUnPolData.ClearData()
        for i in range(0, max_rays + 1):
            py = py_ary[i]
            normUnPolData.AddRay(Int32(wave), Double(hx), Double(hy), Double(px), Double(py), Enum.Parse(ZOSAPI.Tools.RayTrace.OPDMode, "None"))
        #! [e23s05_py]

        #! [e23s06_py]
        # Run Batch Ray Trace
        raytrace.RunAndWaitForCompletion()
        #! [e23s06_py]

        #! [e23s07_py]
        # Read and display results
        normUnPolData.StartReadingResults()
        
        # ... (setup for ReadNextResult) ...
        
        output = normUnPolData.ReadNextResult(...)
        
        while output[0]:
            if (output[2] == 0 and output[3] == 0):
                y_ary[field, wave, output[1] - 1] = output[5]
            
            output = normUnPolData.ReadNextResult(...)

        # 这是手动方法的核心计算与绘图
        plt.plot(py_ary[:], np.squeeze((y_ary[field, wave,:] - chief_ary[field - 1]) * 1000), '-', ms = 4)
        #! [e23s07_py]
```

- **`AddRay`**: 在内层循环中，我们将定义好的一束光扇（Y-Fan）填入缓冲区。
- **`RunAndWaitForCompletion`**: 执行批量追迹。
- **`ReadNextResult`**: 追迹完成后，用一个`while`循环逐条读取结果，并将有效的像面Y坐标(`output[5]`)存入`y_ary`数组。
- **`plt.plot(...)`**: **这是画龙点睛之笔**。
    - **X轴**: `py_ary[:]`，即光瞳坐标。
    - **Y轴**: `(y_ary[...] - chief_ary[...]) * 1000`。我们用读取到的每条光线的Y坐标，减去对应视场的主光线Y坐标基准值，从而得到了**横向光线差**，再乘以1000换算成微米(mum)。

### Native Method
```python
#! [e23s08_py]
ray = TheSystem.Analyses.New_Analysis(ZOSAPI.Analysis.AnalysisIDM.RayFan)
ray_settings = ray.GetSettings()
ray_settings.NumberOfRays = max_rays / 2
ray_settings.Field.UseAllFields()
ray_settings.Wavelength.UseAllWavelengths()

ray.ApplyAndWaitForCompletion()
ray_results = ray.GetResults()
#! [e23s08_py]

for field in range(1, max_num_field + 1):
    #! [e23s09_py]
    # Read and display results
    if field == 1:
        ax2 = plt.subplot(2, max_num_field, field)
    else:
        plt.subplot(2, max_num_field, field)
    
    # 注意：这里的GetDataSeries索引计算方式与您更新并修复的版本不同
    # 这个版本是为一次性获取所有数据而设计的
    ds = ray_results.GetDataSeries(field *2 - 2)
    # get raw .NET data into numpy array
    xRaw = np.asarray(tuple(ds.XData.Data))
    yRaw = np.asarray(tuple(ds.YData.Data))
    
    x = xRaw
    y = yRaw.reshape(ds.YData.Data.GetLength(0), ds.YData.Data.GetLength(1))

    plt.plot(x, y)
    hy = 1 if max_field == 0 else TheSystem.SystemData.Fields.GetField(field).Y / max_field
    plt.title('Field: %4.3f' % (hy))
    #! [e23s09_py]
```