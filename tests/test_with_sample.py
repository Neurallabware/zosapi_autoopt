"""
ZOSAPI Test
"""

import sys
import logging
import argparse
from pathlib import Path

# 添加父目录到路径，以便导入zosapi_autoopt包
sys.path.insert(0, str(Path(__file__).parent.parent))


def find_sample_file():
    """Find first Zemax sample file"""

    sample_files = [
        r"D:\Science\summer\code\zosapi\zmx_data\Cooke 40 degree field.zos"
        # r"D:\Science\summer\code\zosapi\zmx_data\Double Gauss 28 degree field.zos"
        # r"D:\Science\summer\code\zosapi\zmx_data\Even Asphere.zos"
    ]
    
    for sample_file in sample_files:
        if Path(sample_file).exists():
            return str(sample_file)
    return None


def main():
    """Main test function"""
    # 导入模块
    from zosapi_autoopt.zosapi_core import ZOSAPIManager
    from zosapi_autoopt.zosapi_plotting import ZOSPlotter
    from zosapi_autoopt.zosapi_layout import ZOSLayoutAnalyzer

    # Connect to Zemax
    zos_manager = ZOSAPIManager()
    print("Connected to Zemax OpticStudio")
    
    # Load sample file or create new system
    sample_file = find_sample_file()
    zos_manager.open_file(sample_file)
    
        
    # Complete analysis
    print("Running analysis...")
    plotter = ZOSPlotter(zos_manager)
    saved_files = plotter.analyze_and_plot_system(output_dir="output/plots")

    for analysis_type, file_path in saved_files.items():
        print(f"  - {analysis_type}: {Path(file_path).name}")
    
    

    # Create layout analyzer
    layout_analyzer = ZOSLayoutAnalyzer(zos_manager)
    layout_analyzer.export_cross_section("output/plots/layout_export.png")
    print("Layout export completed: output/plots/layout_export.png")


    # Disconnect from Zemax
    zos_manager.disconnect()
    print("Disconnected from Zemax OpticStudio")
    return True


if __name__ == "__main__":

    success = main()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
