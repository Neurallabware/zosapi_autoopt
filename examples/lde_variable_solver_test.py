"""
镜头数据编辑器(LDE)变量与求解器功能测试脚本
专注于测试 Even Asphere 文件中的变量设置功能

Author: allin-love
Date: 2025-07-05
"""

import os
import sys

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from zosapi_autoopt import create_zosapi_manager, create_lens_design_manager, create_system_parameter_manager


def main():
    """主函数：测试LDE变量与求解器功能"""
    print("=== 镜头数据编辑器(LDE)变量与求解器功能测试 ===\n")
    
    # 创建输出目录
    output_dir = os.path.join(parent_dir, "output", "lde_test")
    os.makedirs(output_dir, exist_ok=True)
    print(f"输出目录: {output_dir}")
    
    # 创建管理器
    print("1. 创建ZOS管理器...")
    zos = create_zosapi_manager()
    print("✓ ZOS管理器创建成功")
    
    try:
        # 创建管理器
        print("2. 创建镜头设计管理器...")
        lde = create_lens_design_manager(zos)
        print("✓ 管理器创建成功")
        
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
        
        # 查找非球面表面
        print("\n4. 查找非球面表面...")
        surface_count = lde.LDE.NumberOfSurfaces
        aspheric_surfaces = []
        
        for i in range(1, surface_count + 1):
            try:
                surface = lde.get_surface(i)
                
                # 方法1: 尝试通过单元格获取表面类型
                is_aspheric = False
                try:
                    type_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Type)
                    type_value = type_cell.Value if type_cell else None
                    is_aspheric = type_value and ('even' in str(type_value).lower() or 'aspheric' in str(type_value).lower())
                    
                    if is_aspheric:
                        print(f"✓ 表面 {i} 是非球面，类型: {type_value}")
                        aspheric_surfaces.append(i)
                except Exception as e:
                    pass
                
                # 方法2: 检查是否有非零非球面系数
                if not is_aspheric:
                    has_aspheric_coef = False
                    for j in range(4):  # 检查前4个非球面系数
                        try:
                            param_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Par1 + j)
                            if param_cell:
                                param_value = None
                                try:
                                    param_value = param_cell.DoubleValue
                                except:
                                    try:
                                        param_value = param_cell.Value
                                        if param_value and isinstance(param_value, str):
                                            try:
                                                param_value = float(param_value)
                                            except:
                                                param_value = 0
                                    except:
                                        param_value = 0
                                
                                if param_value and abs(float(param_value)) > 1e-16:
                                    has_aspheric_coef = True
                                    break
                        except:
                            pass
                    
                    if has_aspheric_coef:
                        print(f"✓ 表面 {i} 通过非球面系数判断为非球面")
                        if i not in aspheric_surfaces:
                            aspheric_surfaces.append(i)
            except Exception as e:
                print(f"- 表面 {i} 检查失败: {str(e)}")
        
        if not aspheric_surfaces:
            print("! 未找到非球面表面，使用默认表面进行测试")
            aspheric_surfaces = [3, 5]  # 假定表面3和5为非球面
        else:
            print(f"共找到 {len(aspheric_surfaces)} 个非球面表面: {aspheric_surfaces}")
        
        # 针对每个非球面表面批量设置变量
        print("\n5. 批量设置变量测试...")
        
        # 批量设置所有曲率半径为变量
        print("\n5.1 批量设置所有非球面表面的曲率半径为变量...")
        result = lde.set_all_radii_as_variables(
            start_surface=min(aspheric_surfaces), 
            end_surface=max(aspheric_surfaces), 
            exclude_surfaces=[i for i in range(min(aspheric_surfaces), max(aspheric_surfaces)+1) if i not in aspheric_surfaces], 
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
        print("\n5.2 批量设置所有非球面表面的锥面系数为变量...")
        result = lde.set_all_conics_as_variables(
            start_surface=min(aspheric_surfaces), 
            end_surface=max(aspheric_surfaces), 
            exclude_surfaces=[i for i in range(min(aspheric_surfaces), max(aspheric_surfaces)+1) if i not in aspheric_surfaces], 
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
        print("\n5.3 批量设置所有非球面表面的非球面系数为变量...")
        result = lde.set_all_aspheric_as_variables(
            start_surface=min(aspheric_surfaces), 
            end_surface=max(aspheric_surfaces), 
            exclude_surfaces=[i for i in range(min(aspheric_surfaces), max(aspheric_surfaces)+1) if i not in aspheric_surfaces], 
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
        
        # 保存系统
        print("\n6. 保存系统...")
        
        # 更新系统
        try:
            zos.TheSystem.Update()
        except:
            try:
                zos.TheSystem.PushLens()
            except:
                pass
        
        # 保存文件
        file_path = os.path.join(output_dir, "even_asphere_variables.zos")
        
        try:
            zos.TheSystem.Save(file_path)
            print(f"✓ 系统已保存到: {file_path}")
        except Exception as e:
            print(f"× 保存系统失败: {str(e)}")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 关闭ZOS连接
        print("\n7. 关闭连接...")
        zos.close()
        print("✓ 连接已关闭")
        
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()
