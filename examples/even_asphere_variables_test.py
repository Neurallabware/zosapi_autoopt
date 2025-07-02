"""
Even Asphere 表面变量设置测试脚本
该脚本专注于测试 Even Asphere.zos 文件中的非球面参数设置为变量的功能

Author: allin-love
Date: 2025-07-05
"""

import os
import sys

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from zosapi_autoopt import create_zosapi_manager, create_lens_design_manager


def main():
    """主函数：专注测试 Even Asphere 文件中的非球面变量设置"""
    print("=== Even Asphere 非球面变量设置测试 ===\n")
    
    # 创建ZOS管理器
    print("1. 创建ZOS管理器...")
    zos = create_zosapi_manager()
    print("✓ ZOS管理器创建成功")
    
    try:
        # 创建镜头设计管理器
        print("2. 创建镜头设计管理器...")
        lde = create_lens_design_manager(zos)
        print("✓ 镜头设计管理器创建成功")
        
        # 加载 Even Asphere 样例文件
        print("\n3. 加载 Even Asphere 样例文件...")
        zmx_file = os.path.join(parent_dir, "zmx_data", "Even Asphere.zos")
        
        if os.path.exists(zmx_file):
            print(f"✓ 文件存在: {zmx_file}")
            zos.TheSystem.LoadFile(zmx_file, False)
            print(f"✓ 文件加载成功")
        else:
            print(f"× 文件不存在: {zmx_file}")
            return
        
        # 获取系统信息
        print("\n4. 系统信息:")
        surface_count = lde.LDE.NumberOfSurfaces
        print(f"表面总数: {surface_count}")
        
        # 找出非球面表面
        print("\n5. 查找非球面表面...")
        aspheric_surfaces = []
        
        for i in range(1, surface_count + 1):
            try:
                surface = lde.get_surface(i)
                
                # 尝试获取表面类型
                is_aspheric = False
                
                # 方法1: 尝试通过单元格获取表面类型
                try:
                    type_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Type)
                    type_value = type_cell.Value if type_cell else None
                    is_aspheric = type_value and ('even' in str(type_value).lower() or 'aspheric' in str(type_value).lower())
                    
                    if is_aspheric:
                        print(f"✓ 表面 {i} 是非球面，类型: {type_value}")
                        aspheric_surfaces.append(i)
                    else:
                        print(f"- 表面 {i} 不是非球面，类型: {type_value}")
                except Exception as e:
                    print(f"- 表面 {i} 类型检查失败: {str(e)}")
                
                # 方法2: 如果方法1失败，尝试通过锥面系数和非球面系数判断
                if not is_aspheric:
                    try:
                        # 检查是否有非零锥面系数
                        conic_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Conic)
                        conic_value = conic_cell.DoubleValue if conic_cell else 0.0
                        
                        # 检查是否有非零非球面系数
                        has_aspheric_coef = False
                        for j in range(4):  # 检查前4个非球面系数
                            try:
                                param_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Par1 + j)
                                param_value = param_cell.DoubleValue if param_cell else 0.0
                                if abs(param_value) > 1e-16:  # 如果有非零系数
                                    has_aspheric_coef = True
                                    break
                            except:
                                pass
                        
                        if abs(conic_value) > 1e-16 or has_aspheric_coef:
                            print(f"✓ 表面 {i} 通过参数判断为非球面")
                            if i not in aspheric_surfaces:
                                aspheric_surfaces.append(i)
                    except Exception as e:
                        print(f"- 表面 {i} 参数检查失败: {str(e)}")
                
            except Exception as e:
                print(f"- 表面 {i} 检查失败: {str(e)}")
        
        if not aspheric_surfaces:
            print("! 未找到非球面表面，使用默认表面进行测试")
            aspheric_surfaces = [3, 5]  # 假定表面3和5为非球面
        
        print(f"\n找到的非球面表面: {aspheric_surfaces}")
        
        # 对非球面表面分别设置变量
        print("\n6. 测试单个非球面表面变量设置...")
        
        # 选择第一个非球面表面进行详细测试
        test_surface = aspheric_surfaces[0]
        print(f"对表面 {test_surface} 进行详细测试:")
        
        # 设置曲率半径为变量
        print("\n6.1 设置曲率半径为变量...")
        try:
            result = lde.set_variable(test_surface, 'radius', min_value=-200.0, max_value=200.0)
            print(f"✓ 设置曲率半径为变量{'成功' if result else '失败'}")
            
            # 验证设置
            surface = lde.get_surface(test_surface)
            cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Radius)
            solve_type = cell.SolveType if hasattr(cell, "SolveType") else "未知"
            print(f"   曲率半径变量状态: SolveType={solve_type}, 当前值={cell.Value}")
        except Exception as e:
            print(f"× 设置曲率半径为变量失败: {str(e)}")
        
        # 设置锥面系数为变量
        print("\n6.2 设置锥面系数为变量...")
        try:
            result = lde.set_variable(test_surface, 'conic', min_value=-5.0, max_value=0.0)
            print(f"✓ 设置锥面系数为变量{'成功' if result else '失败'}")
            
            # 验证设置
            surface = lde.get_surface(test_surface)
            cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Conic)
            solve_type = cell.SolveType if hasattr(cell, "SolveType") else "未知"
            print(f"   锥面系数变量状态: SolveType={solve_type}, 当前值={cell.Value}")
        except Exception as e:
            print(f"× 设置锥面系数为变量失败: {str(e)}")
        
        # 设置非球面系数为变量
        print("\n6.3 设置非球面系数为变量...")
        for j in range(4):  # 设置前4个非球面系数
            try:
                order = j + 1  # 系数阶数 (4阶、6阶、8阶、10阶)
                
                # 获取当前值
                surface = lde.get_surface(test_surface)
                param_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Par1 + j)
                current_value = None
                try:
                    current_value = param_cell.DoubleValue
                except:
                    try:
                        current_value = float(param_cell.Value)
                    except:
                        current_value = 0.0
                
                # 设置为变量
                param_cell.Value = str(current_value)  # 确保有有效值
                param_cell.MakeSolveVariable()
                
                # 设置变量范围
                solver_data = param_cell.GetSolveData()
                if solver_data is not None:
                    solver_data.MinValue = -1e-4
                    solver_data.MaxValue = 1e-4
                    solver_data.Status = True
                    param_cell.SetSolveData(solver_data)
                
                # 验证设置
                solve_type = param_cell.SolveType if hasattr(param_cell, "SolveType") else "未知"
                print(f"✓ 设置{(j+1)*2+2}阶系数为变量，状态: SolveType={solve_type}, 当前值={param_cell.Value}")
            except Exception as e:
                print(f"× 设置{(j+1)*2+2}阶系数为变量失败: {str(e)}")
        
        # 测试批量设置变量功能
        print("\n7. 测试批量变量设置功能...")
        
        # 清除之前的变量设置
        print("\n7.1 清除之前的变量设置...")
        try:
            surface = lde.get_surface(test_surface)
            # 清除曲率半径变量
            radius_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Radius)
            radius_cell.ClearSolve()
            # 清除锥面系数变量
            conic_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Conic)
            conic_cell.ClearSolve()
            # 清除非球面系数变量
            for j in range(4):
                param_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Par1 + j)
                param_cell.ClearSolve()
            print("✓ 变量设置已清除")
        except Exception as e:
            print(f"× 清除变量设置失败: {str(e)}")
        
        # 批量设置所有曲率半径为变量
        print("\n7.2 批量设置所有曲率半径为变量...")
        result = lde.set_all_radii_as_variables(
            start_surface=aspheric_surfaces[0], 
            end_surface=aspheric_surfaces[-1], 
            exclude_surfaces=[],  # 不排除任何表面
            min_value=-200.0, 
            max_value=200.0
        )
        print(f"✓ 批量设置曲率半径变量{'成功' if result else '失败'}")
        
        # 验证曲率半径变量设置
        print("   验证曲率半径变量设置:")
        for i in aspheric_surfaces:
            try:
                surface = lde.get_surface(i)
                cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Radius)
                solve_type = cell.SolveType if hasattr(cell, "SolveType") else "未知"
                is_var = isinstance(solve_type, int) and solve_type == 5  # 5通常对应变量
                print(f"   表面 {i} 曲率半径: {'变量' if is_var else '非变量'} (SolveType={solve_type})")
            except Exception as e:
                print(f"   表面 {i} 曲率半径检查失败: {str(e)}")
        
        # 批量设置所有锥面系数为变量
        print("\n7.3 批量设置所有锥面系数为变量...")
        result = lde.set_all_conics_as_variables(
            start_surface=aspheric_surfaces[0], 
            end_surface=aspheric_surfaces[-1], 
            exclude_surfaces=[], 
            min_value=-5.0, 
            max_value=0.0
        )
        print(f"✓ 批量设置锥面系数变量{'成功' if result else '失败'}")
        
        # 验证锥面系数变量设置
        print("   验证锥面系数变量设置:")
        for i in aspheric_surfaces:
            try:
                surface = lde.get_surface(i)
                cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Conic)
                solve_type = cell.SolveType if hasattr(cell, "SolveType") else "未知"
                is_var = isinstance(solve_type, int) and solve_type == 5  # 5通常对应变量
                print(f"   表面 {i} 锥面系数: {'变量' if is_var else '非变量'} (SolveType={solve_type})")
            except Exception as e:
                print(f"   表面 {i} 锥面系数检查失败: {str(e)}")
        
        # 批量设置所有非球面系数为变量
        print("\n7.4 批量设置所有非球面系数为变量...")
        result = lde.set_all_aspheric_as_variables(
            start_surface=aspheric_surfaces[0], 
            end_surface=aspheric_surfaces[-1], 
            exclude_surfaces=[], 
            order=4,  # 设置到10阶
            min_value=-1e-4, 
            max_value=1e-4
        )
        print(f"✓ 批量设置非球面系数变量{'成功' if result else '失败'}")
        
        # 验证非球面系数变量设置
        print("   验证非球面系数变量设置:")
        for i in aspheric_surfaces:
            for j in range(4):  # 检查前4个非球面系数
                try:
                    surface = lde.get_surface(i)
                    cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Par1 + j)
                    solve_type = cell.SolveType if hasattr(cell, "SolveType") else "未知"
                    is_var = isinstance(solve_type, int) and solve_type == 5  # 5通常对应变量
                    print(f"   表面 {i} 非球面{(j+1)*2+2}阶系数: {'变量' if is_var else '非变量'} (SolveType={solve_type})")
                except Exception as e:
                    print(f"   表面 {i} 非球面{(j+1)*2+2}阶系数检查失败: {str(e)}")
        
        # 保存并输出系统信息
        print("\n8. 保存系统...")
        
        # 更新系统
        try:
            zos.TheSystem.Update()
        except:
            try:
                zos.TheSystem.PushLens()
            except:
                pass
        
        # 保存文件
        output_dir = os.path.join(parent_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, "even_asphere_variables_test.zos")
        
        try:
            zos.TheSystem.Save(file_path)
            print(f"✓ 系统已保存到: {file_path}")
        except Exception as e:
            print(f"× 保存系统失败: {str(e)}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 关闭ZOS连接
        print("\n9. 关闭连接...")
        zos.close()
        print("✓ 连接已关闭")
        
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()
