"""
镜头数据编辑器(LDE)功能测试脚本
用于验证基本的镜头设计和编辑功能

Author: allin-love
Date: 2025-07-03
"""

import os
import sys

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from zosapi_autoopt import create_zosapi_manager, create_lens_design_manager


def main():
    """主函数：测试LDE基本功能"""
    print("=== 镜头数据编辑器(LDE)功能测试 ===\n")
    
    # 创建输出目录
    output_dir = os.path.join(parent_dir, "output", "lde_test")
    os.makedirs(output_dir, exist_ok=True)
    print(f"输出目录: {output_dir}")
    
    # 创建管理器
    print("1. 创建ZOS管理器...")
    zos = create_zosapi_manager()
    print("✓ ZOS管理器创建成功")
    
    try:
        # 创建基础系统
        print("2. 创建基础系统...")
        zos.TheSystem.New(False)
        print("✓ 新系统创建成功")
        
        # 创建镜头设计管理器
        print("3. 创建镜头设计管理器...")
        lde = create_lens_design_manager(zos)
        print("✓ 镜头设计管理器创建成功")
        
        # 添加表面
        print("\n--- 添加光学表面 ---")
        
        # 添加第一个镜片
        print("4. 添加第一个镜片...")
        # 前表面 - 第1面
        lde.set_radius(1, 50.0)  # 曲率半径为50mm
        lde.set_thickness(1, 5.0)  # 厚度为5mm
        lde.set_material(1, "N-BK7")  # 材料为N-BK7
        
        # 后表面 - 第2面
        lde.insert_surface(2)  # 插入表面
        lde.set_radius(2, -50.0)  # 曲率半径为-50mm
        lde.set_thickness(2, 20.0)  # 厚度为20mm
        print("✓ 第一个镜片添加完成")
        
        # 添加第二个镜片
        print("5. 添加第二个镜片...")
        # 前表面 - 第3面
        lde.insert_surface(3)  # 插入表面
        lde.set_radius(3, 40.0)  # 曲率半径为40mm
        lde.set_thickness(3, 3.0)  # 厚度为3mm
        lde.set_material(3, "F2")  # 材料为F2
        
        # 后表面 - 第4面
        lde.insert_surface(4)  # 插入表面
        lde.set_radius(4, -40.0)  # 曲率半径为-40mm
        lde.set_thickness(4, 50.0)  # 厚度为50mm
        print("✓ 第二个镜片添加完成")
        
        # 添加像面
        print("6. 添加像面...")
        lde.insert_surface(5)  # 插入表面
        lde.set_radius(5, 0.0)  # 平面
        lde.set_thickness(5, 0.0)  # 厚度为0
        print("✓ 像面添加完成")
        
        # 设置光阑
        print("7. 设置光阑...")
        lde.set_aperture(1, "none", 10.0)  # 设置第1面为圆形光阑，半径10mm
        print("✓ 光阑设置完成")
        
        # 获取系统信息
        print("\n--- 系统信息 ---")
        summary = lde.get_system_summary()
        print(f"表面数量: {summary['surface_count']}")
        
        for i, surface in enumerate(summary['surfaces'], 1):
            print(f"\n表面 {i}:")
            print(f"  曲率半径: {surface['radius']}")
            print(f"  厚度: {surface['thickness']}")
            print(f"  材料: {surface['material']}")
            print(f"  半口径: {surface['semi_diameter']}")
        
        # 保存文件
        file_path = os.path.join(output_dir, "simple_lens.zos")
        zos.TheSystem.SaveAs(file_path)
        print(f"\n✓ 保存文件: {os.path.basename(file_path)}")
        
        # 显示结果
        if os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024
            print(f"  文件大小: {size_kb:.1f} KB")
            print(f"  文件位置: {output_dir}")
            print("\n✅ 测试成功完成！你可以在OpticStudio中打开此文件验证。")
        else:
            print("❌ 文件保存失败")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # 清理资源
        del zos
        print("\n🧹 清理完成")


if __name__ == "__main__":
    main()
