"""
检查 Even Asphere 样例文件中的表面类型信息
专注于获取表面类型、曲率半径、厚度、锥面系数和非球面系数等信息
Author: allin-love
Date: 2025-07-05
"""

import os
import sys

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from zosapi_autoopt import create_zosapi_manager


def main():
    """主函数：检查 Even Asphere 样例文件中的表面类型"""
    print("=== 检查 Even Asphere 样例文件中的表面类型 ===\n")
    
    # 创建管理器
    print("1. 创建ZOS管理器...")
    zos = create_zosapi_manager()
    print("✓ ZOS管理器创建成功")
    
    try:
        # 加载 Even Asphere 样例文件
        print("2. 加载 Even Asphere 样例文件...")
        zmx_file = os.path.join(parent_dir, "zmx_data", "Even Asphere.zos")
        
        if os.path.exists(zmx_file):
            print(f"✓ 文件存在: {zmx_file}")
            zos.TheSystem.LoadFile(zmx_file, False)
            print(f"✓ 文件加载成功")
        else:
            print(f"× 文件不存在: {zmx_file}")
            return
        
        # 获取LDE编辑器引用
        lde = zos.TheSystem.LDE
        
        # 获取系统信息
        print("\n--- 系统信息 ---")
        surface_count = lde.NumberOfSurfaces
        print(f"表面总数: {surface_count}")
        print(f"波长数量: {zos.TheSystem.SystemData.Wavelengths.NumberOfWavelengths}")
        print(f"视场数量: {zos.TheSystem.SystemData.Fields.NumberOfFields}")
        
        # 遍历表面获取信息
        print("\n--- 表面详细信息 ---")
        aspheric_surfaces = []
        
        for i in range(surface_count):
            surface = lde.GetSurfaceAt(i+1)
            print(f"\n表面 {i+1} 信息:")
            
            # 获取表面类型
            try:
                # 通过单元格获取表面类型
                type_cell = surface.SurfaceType
                type_value = type_cell if type_cell else "未知"
                print(f"  表面类型: {type_value}")
                
                # 检查是否为非球面
                is_aspheric = type_value and ('even' in str(type_value).lower() or 'aspheric' in str(type_value).lower())
                if is_aspheric:
                    aspheric_surfaces.append(i+1)
                    print(f"  * 这是非球面表面")
            except Exception as e:
                print(f"  表面类型获取失败: {str(e)}")
            
            # 获取曲率半径
            try:
                radius_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Radius)
                radius = radius_cell.Value
                print(f"  曲率半径: {radius}")
            except Exception as e:
                print(f"  曲率半径获取失败: {str(e)}")
            
            # 获取厚度
            try:
                thickness_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Thickness)
                thickness = thickness_cell.Value
                print(f"  厚度: {thickness}")
            except Exception as e:
                print(f"  厚度获取失败: {str(e)}")
            
            # 获取材料
            try:
                material_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Material)
                material = material_cell.Value
                if material:
                    print(f"  材料: {material}")
            except Exception as e:
                print(f"  材料获取失败: {str(e)}")
            
            # 获取锥面系数
            try:
                conic_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Conic)
                conic = conic_cell.Value
                print(f"  锥面系数: {conic}")
            except Exception as e:
                print(f"  锥面系数获取失败: {str(e)}")
            
            # 获取非球面系数
            has_aspheric_coef = False
            print("  非球面系数:")
            for j in range(8):  # 获取前8个非球面系数
                try:
                    param_cell = surface.GetCellAt(zos.ZOSAPI.Editors.LDE.SurfaceColumn.Par1 + j)
                    if param_cell:
                        param_value = None
                        try:
                            param_value = param_cell.DoubleValue
                        except:
                            try:
                                param_value = param_cell.Value
                            except:
                                pass
                        
                        if param_value is not None and param_value != 0:
                            print(f"    {(j+1)*2+2}阶: {param_value}")
                            has_aspheric_coef = True
                except Exception as e:
                    pass
            
            if not has_aspheric_coef:
                print("    无非球面系数或全为零")
            
            # 通过非球面系数判断是否为非球面
            if has_aspheric_coef and (i+1) not in aspheric_surfaces:
                aspheric_surfaces.append(i+1)
                print(f"  * 根据非球面系数判断为非球面表面")
        
        # 输出找到的非球面表面
        print("\n--- 非球面表面总结 ---")
        if aspheric_surfaces:
            print(f"找到的非球面表面: {aspheric_surfaces}")
        else:
            print("未找到非球面表面")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        # 关闭ZOS连接
        print("\n3. 关闭连接...")
        zos.close()
        print("✓ 连接已关闭")
        
    print("\n=== 检查完成 ===")


if __name__ == "__main__":
    main()
