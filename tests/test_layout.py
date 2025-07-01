"""
简化的PNG Layout导出测试
Author: allin-love
Date: 2025-07-01
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from zosapi_autoopt.zosapi_core import ZOSAPIManager
from zosapi_autoopt.zosapi_layout import ZOSLayoutAnalyzer


def test_png_export():
    """测试PNG格式Layout导出"""
    print("=== 测试PNG Layout导出 ===")
    

    # 连接到ZOSAPI并加载文件
    zos_manager = ZOSAPIManager()
    sample_file = Path.cwd() / "zmx_data" / "Double Gauss 28 degree field.zos"

    zos_manager.open_file(str(sample_file))

    # 设置导出参数
    system = zos_manager.TheSystem
    layouts_interface = system.Tools.Layouts
    num_surfaces = system.LDE.NumberOfSurfaces
        
    output_path = str(Path.cwd() / "layout_export.png")
    print(f"输出路径: {output_path}")
    
    layout_analyzer = ZOSLayoutAnalyzer(zos_manager)
    layout_analyzer.export_cross_section(output_path)
    # layout_analyzer.export_3d_viewer(output_path)
    # layout_analyzer.export_shaded_model(output_path)

if __name__ == "__main__":
    test_png_export()

