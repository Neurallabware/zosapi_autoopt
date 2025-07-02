"""
系统参数设置测试脚本
Author: allin-love
Date: 2025-07-03
"""
import os
import sys

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from zosapi_autoopt import create_zosapi_manager, create_system_parameter_manager


def main():   
    # 创建输出目录
    output_dir = os.path.join(parent_dir, "output", "basic_test")
    os.makedirs(output_dir, exist_ok=True)
    print(f"输出目录: {output_dir}")
    
    # 创建管理器
    zos = create_zosapi_manager()    

    # 创建基础系统
    zos.TheSystem.New(False)
        
    # 创建系统参数管理器
    sys_param = create_system_parameter_manager(zos)

    # 基础参数设置
    sys_param.set_aperture('entrance_pupil_diameter', 50.0)
    print("入瞳直径设置为 50.0 mm")
    
    # 设置波长
    sys_param.set_wavelength_preset('d_0p587')  # D线
    sys_param.add_wavelength(0.486, 1.0)        # F线
    sys_param.add_wavelength(0.656, 1.0)        # C线
    print("设置F, d, C三条谱线")

    # 设置视场
    sys_param.set_field_type('angle')
    sys_param.clear_fields()  # 清除默认视场
    sys_param.add_field(0, 0, 1.0)    # 轴上视场
    sys_param.add_field(0, 10, 1.0)   # 10度视场
    sys_param.add_field(0, 20, 1.0)   # 20度视场
    print("设置三个视场点: 0°, 10°, 20°")
    
    # 设置环境参数
    # sys_param.set_environment(20.0, 1.0, True)
    # print("设置标准环境: 20°C, 1atm")

    # 获取系统摘要
    summary = sys_param.get_system_summary()
    print(f"孔径: {summary['aperture']}")
    print(f"波长数量: {len(summary['wavelengths'])}")
    print(f"视场数量: {len(summary['fields'])}")
    print(f"环境: {summary['environment']}")
    
    # 保存文件
    file_path = os.path.join(output_dir, "basic_parameters.zos")
    zos.TheSystem.SaveAs(file_path)
    print(f"保存文件: {os.path.basename(file_path)}")
    
    # 显示结果
    if os.path.exists(file_path):
        size_kb = os.path.getsize(file_path) / 1024
        print(f"  文件大小: {size_kb:.1f} KB")
        print(f"  文件位置: {output_dir}")
        
    # 清理资源
    del zos



if __name__ == "__main__":
    main()
