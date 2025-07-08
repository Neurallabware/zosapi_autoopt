### `MeritFunctionEditor` 使用指南

#### 1\. 初始化

使用前，需先初始化`ZOSAPIManager`并加载一个光学系统文件。

```python
from zosapi_autoopt.zosapi_core import ZOSAPIManager
from zosapi_autoopt.merit_function import MeritFunctionEditor

# 连接并加载系统
zos_manager = ZOSAPIManager()
zos_manager.open_file("your_lens_file.zos")

# 初始化评价函数编辑器
mf_editor = MeritFunctionEditor(zos_manager)

# (推荐) 创建操作数库的别名，让代码更简洁
Op = mf_editor.Operands
```

-----

#### 2\. 核心功能：操作数管理

##### **2.1 添加操作数 `add_operand()`**

使用内置的`Operands`库可以安全、便捷地添加操作数。

```python
# --- 添加各种类型的操作数 ---

# 添加一个简单的几何操作数，如有效焦距
mf_editor.add_operand(Op.EFFL, target=100.0, weight=1.0)

# 添加一个像差操作数，并指定其参数
mf_editor.add_operand(
    Op.ASTI,          # 操作数类型：像散
    target=0.0,
    weight=2.0,
    field=2,          # 参数：第2个视场
    wave=1            # 参数：第1个波长
)

# 添加一个约束操作数，并指定其参数
mf_editor.add_operand(
    Op.MNCG,          # 操作数类型：最小中心玻璃厚度
    target=3.0,
    weight=10.0,
    surf1=1,          # 参数：起始面1
    surf2=2           # 参数：结束面2
)

# 添加一个带频率参数的MTF操作数
mf_editor.add_operand(
    Op.MTFT,          # 操作数类型：子午MTF
    target=0.5,
    weight=1.0,
    field=2,
    wave=1,
    freq=50.0         # 参数：空间频率50 lp/mm
)
```

##### **2.2 列出、编辑与删除**

```python
# 列出当前所有操作数
all_operands = mf_editor.list_operands()
for op in all_operands:
    print(f"Index: {op['index']}, Type: {op['type']}, Value: {op['value']:.4f}")

# 编辑操作数 (例如，编辑最后一个)
last_op_index = mf_editor.get_operand_count() - 1
mf_editor.edit_operand(
    index=last_op_index,
    target=0.45,
    weight=1.5
)

# 删除操作数 (例如，删除倒数第二个)
if mf_editor.get_operand_count() > 1:
    mf_editor.delete_operand(mf_editor.get_operand_count() - 2)
```

##### **2.3 清空评价函数 `clear_merit_function()`**

此方法会将评价函数恢复到仅包含一个`CONF`操作数的、最简单的初始状态。

```python
# 安全地清空评价函数
mf_editor.clear_merit_function()

# 验证
print(mf_editor.list_operands())
# 预期输出: [{'index': 0, 'type': 'CONF', ...}]
```

-----

#### 3\. 自动化构建：优化向导

使用优化向导可以快速构建标准的评价函数。

```python
# 自动生成基于RMS光斑尺寸的评价函数
mf_editor.use_optimization_wizard(
    wizard_type='rms_spot',  # 可选 'rms_spot', 'wavefront', 'default'
    clear_existing=True    # 在生成前清空现有函数
)

print(f"向导已生成 {mf_editor.get_operand_count()} 个操作数。")
```

-----

#### 4\. 运行优化

该类封装了Zemax的优化工具，可直接调用。

```python
# --- 关键前提：运行优化前，必须先设置变量！ ---
# from zosapi_autoopt.zosapi_lde import LensDesignManager
# lde_manager = LensDesignManager(zos_manager)
# lde_manager.set_variable(1, 'radius')
# lde_manager.set_variable(2, 'thickness')

# 获取优化前的评价值
initial_merit = mf_editor.get_current_merit_value()
print(f"优化前评价函数值: {initial_merit:.6f}")

# 运行局部优化
result = mf_editor.run_local_optimization(timeout_seconds=60)

if result['success']:
    print(f"优化完成。优化后评价函数值: {result['final_merit']:.6f}")
```

-----

#### 5\. 内置操作数库 `Operands`

这是`MeritFunctionEditor`最强大的功能，它将所有操作数以常量的形式内置，您可以通过代码提示轻松调用。

```python
# 创建别名以简化调用
Op = MeritFunctionEditor.Operands

# --- 调用示例 ---
# 控制类: Op.Control.CONF
# 像差类: Op.Aberration.SPHA
# 约束类: Op.Constraint.MNCG
# 几何类: Op.Geometric.EFFL
# 光线追迹类: Op.Ray.REAX
# MTF类: Op.MTF.MTFT
# 非序列类: Op.NonSequential.NSDD
```