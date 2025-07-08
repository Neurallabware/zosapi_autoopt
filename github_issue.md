# Bug Report: TypeError in _get_cell method - GetCellAt doesn't accept SurfaceColumn enum

## Issue Description

When calling solver methods like `set_substitute_solve()`, the code fails with a `TypeError` indicating that `GetCellAt` doesn't accept `SurfaceColumn` enum arguments.

## Error Details

```
TypeError: No method matches given arguments for IEditorRow.GetCellAt: (<class 'ZOSAPI.Editors.LDE.SurfaceColumn'>)
  File "zosapi_lde.py", line 947, in _get_cell
    return surface.GetCellAt(param_column_map[param_name.lower()])
  File "zosapi_lde.py", line 979, in set_substitute_solve
    cell = self._get_cell(surface_pos, 'material')
  File "examples\3p_smartphone.py", line 58, in main
    lde_manager.set_substitute_solve(2*i, 'PLASTIC')
```

## Steps to Reproduce

1. Run the `examples/3p_smartphone.py` script
2. The error occurs when trying to set a substitute solver on surface materials:
   ```python
   lde_manager.set_substitute_solve(2*i, 'PLASTIC')
   ```

## Root Cause

The `_get_cell()` method in `zosapi_lde.py` (line 947) uses `SurfaceColumn` enum values directly:

```python
def _get_cell(self, surface_pos: int, param_name: str) -> Any:
    """【私有辅助函数】获取指定表面和参数的单元格对象。"""
    surface = self.get_surface(surface_pos)
    param_column_map = {
        'radius': self.ZOSAPI.Editors.LDE.SurfaceColumn.Radius,
        'thickness': self.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness,
        'material': self.ZOSAPI.Editors.LDE.SurfaceColumn.Material,
        'conic': self.ZOSAPI.Editors.LDE.SurfaceColumn.Conic
    }
    if param_name.lower() not in param_column_map:
        raise ValueError(f"不支持的参数名称: {param_name}")
    return surface.GetCellAt(param_column_map[param_name.lower()])  # ← This line fails
```

However, the ZOS-API `GetCellAt` method expects integer column indices, not enum objects.

## Analysis

Looking at the official ZOS-API sample code (`PythonStandalone_03_open_file_and_optimise.py`), `GetCellAt` is consistently called with integer arguments:

```python
Operand_3.GetCellAt(2).IntegerValue = 1  # Integer index, not enum
Operand_3.GetCellAt(3).IntegerValue = 3
```

## Inconsistency in Current Code

Interestingly, other parts of the same file successfully use enum values with `GetCellAt`:

```python
# Line 760 - This works fine
cell = surface.GetCellAt(self.ZOSAPI.Editors.LDE.SurfaceColumn.Comment)

# Line 632 - This also works
cell = surface.GetCellAt(param_column)
```

This suggests there might be different behavior between different ZOS-API versions or different object types.

## Proposed Solution

Convert the `SurfaceColumn` enum values to their integer equivalents:

```python
def _get_cell(self, surface_pos: int, param_name: str) -> Any:
    """【私有辅助函数】获取指定表面和参数的单元格对象。"""
    surface = self.get_surface(surface_pos)
    param_column_map = {
        'radius': self.ZOSAPI.Editors.LDE.SurfaceColumn.Radius,
        'thickness': self.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness,
        'material': self.ZOSAPI.Editors.LDE.SurfaceColumn.Material,
        'conic': self.ZOSAPI.Editors.LDE.SurfaceColumn.Conic
    }
    if param_name.lower() not in param_column_map:
        raise ValueError(f"不支持的参数名称: {param_name}")
    
    column_enum = param_column_map[param_name.lower()]
    # Convert enum to integer value to ensure compatibility
    column_index = int(column_enum)
    return surface.GetCellAt(column_index)
```

## Environment

- **Operating System**: Windows
- **Python Version**: [Unknown - please specify]
- **ZOS-API Version**: [Unknown - please specify]
- **OpticStudio Version**: [Unknown - please specify]

## Affected Methods

The following solver methods are currently affected by this bug:
- `set_substitute_solve()`
- `set_pickup_solve()`
- `set_f_number_solve()`
- `set_marginal_ray_angle_solve()`
- `clear_solve()`

## Additional Notes

1. This might be a ZOS-API version compatibility issue
2. The inconsistency within the same codebase (some enum usage works, some doesn't) suggests this might be object-type specific
3. Consider adding proper error handling and fallback mechanisms for different ZOS-API versions

## Priority

**High** - This blocks the execution of solver-related functionality, which is core to the library's optimization features.
