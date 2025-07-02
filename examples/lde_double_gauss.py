"""
镜头数据编辑器(LDE)高级功能测试脚本
创建一个简化的双高斯镜头设计

Author: allin-love
Date: 2025-07-03
"""

import os
import sys

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from zosapi_autoopt import create_zosapi_manager, create_lens_design_manager, create_system_parameter_manager


def main():
    """主函数：创建双高斯镜头"""
    print("=== 双高斯镜头设计测试 ===\n")
    
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
        
        # 创建系统参数管理器和镜头设计管理器
        print("3. 创建管理器...")
        sys_param = create_system_parameter_manager(zos)
        lde = create_lens_design_manager(zos)
        print("✓ 管理器创建成功")
        
        # 设置系统参数
        print("\n--- 设置系统参数 ---")
        
        print("4. 设置孔径...")
        sys_param.set_aperture('entrance_pupil_diameter', 25.0)  # 入瞳直径25mm
        print("✓ 入瞳直径设置为 25.0 mm")
        
        print("5. 设置波长...")
        sys_param.set_wavelength_preset('fdc_visible')  # F, d, C三条可见光谱线
        print("✓ 设置F, d, C三条谱线")
        
        print("6. 设置视场...")
        sys_param.set_field_type('angle')
        sys_param.clear_fields()  # 清除默认视场
        sys_param.add_field(0, 0, 1.0)    # 轴上视场
        sys_param.add_field(0, 10, 1.0)   # 10度视场
        sys_param.add_field(0, 20, 1.0)   # 20度视场
        print("✓ 设置三个视场点: 0°, 10°, 20°")
        
        # 创建双高斯镜头
        print("\n--- 创建双高斯镜头 ---")
        
        # 物面 - 第0面
        print("7. 添加物面...")
        lde.set_radius(0, 0.0)        # 平面
        lde.set_thickness(0, 100.0)   # 物距
        print("✓ 物面添加完成")
        
        # 添加光阑面
        print("8. 添加光阑面...")
        lde.set_radius(1, 0.0)        # 平面
        lde.set_thickness(1, 10.0)    # 厚度
        print("✓ 光阑面添加完成")
        
        # 前组镜片
        print("9. 添加前组镜片...")
        
        # 第一片正透镜 - 前表面
        lde.insert_surface(2)
        lde.set_radius(2, 40.0)       # 曲率半径
        lde.set_thickness(2, 6.0)     # 厚度
        lde.set_material(2, "N-BK7")  # 材料
        
        # 第一片正透镜 - 后表面
        lde.insert_surface(3)
        lde.set_radius(3, -40.0)      # 曲率半径
        lde.set_thickness(3, 2.0)     # 厚度
        
        # 第二片负透镜 - 前表面
        lde.insert_surface(4)
        lde.set_radius(4, -20.0)      # 曲率半径
        lde.set_thickness(4, 2.0)     # 厚度
        lde.set_material(4, "F2")     # 材料
        
        # 第二片负透镜 - 后表面
        lde.insert_surface(5)
        lde.set_radius(5, 20.0)       # 曲率半径
        lde.set_thickness(5, 30.0)    # 厚度
        print("✓ 前组镜片添加完成")
        
        # 后组镜片
        print("10. 添加后组镜片...")
        
        # 第三片负透镜 - 前表面
        lde.insert_surface(6)
        lde.set_radius(6, -20.0)      # 曲率半径
        lde.set_thickness(6, 2.0)     # 厚度
        lde.set_material(6, "F2")     # 材料
        
        # 第三片负透镜 - 后表面
        lde.insert_surface(7)
        lde.set_radius(7, 20.0)       # 曲率半径
        lde.set_thickness(7, 2.0)     # 厚度
        
        # 第四片正透镜 - 前表面
        lde.insert_surface(8)
        lde.set_radius(8, 40.0)       # 曲率半径
        lde.set_thickness(8, 6.0)     # 厚度
        lde.set_material(8, "N-BK7")  # 材料
        
        # 第四片正透镜 - 后表面
        lde.insert_surface(9)
        lde.set_radius(9, -40.0)      # 曲率半径
        lde.set_thickness(9, 50.0)    # 厚度
        print("✓ 后组镜片添加完成")
        
        # 像面
        print("11. 添加像面...")
        lde.insert_surface(10)
        lde.set_radius(10, 0.0)       # 平面
        lde.set_thickness(10, 0.0)    # 厚度
        print("✓ 像面添加完成")
        
        # 设置表面口径
        print("12. 设置表面口径...")
        for i in range(2, 10):
            lde.set_semi_diameter(i, 15.0)  # 半口径15mm
        print("✓ 表面口径设置完成")
        
        # 获取系统信息
        print("\n--- 系统信息 ---")
        summary = lde.get_system_summary()
        print(f"表面数量: {summary['surface_count']}")
        
        # 保存文件
        file_path = os.path.join(output_dir, "double_gauss.zos")
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
