"""
ZOSAPI Test
"""

import sys
import logging
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))



def find_sample_file():
    """Find first Zemax sample file"""
    base_paths = [
        r"C:\Program Files\ANSYS Inc\v242\Zemax OpticStudio",
    ]
    
    sample_files = [
        r"ZemaxData\Samples\Sequential\Objectives\Cooke 40 degree field.zos",
        r"ZemaxData\Samples\Sequential\Objectives\Double Gauss 28 degree field.zos",
        r"ZemaxData\Samples\Sequential\Objectives\Singlet.zos"
    ]
    
    for base_path in base_paths:
        if Path(base_path).exists():
            for sample_file in sample_files:
                full_path = Path(base_path) / sample_file
                if full_path.exists():
                    return str(full_path)
    return None


def main():
    """Main test function"""
    # 导入模块
    from zosapi_core import ZOSAPIManager
    from zosapi_plotting import analyze_and_plot_system
    
    # Connect to Zemax
    zos_manager = ZOSAPIManager()
    assert zos_manager.is_connected, "Failed to connect to Zemax OpticStudio"
    print("Connected to Zemax OpticStudio")
    
    # Load sample file or create new system
    sample_file = find_sample_file()
    if sample_file:
        zos_manager.open_file(sample_file)
        print(f"Loaded: {Path(sample_file).name}")
    else:
        zos_manager.new_file()
        print("No sample files found - using new empty system")
        
    # Complete analysis
    print("Running analysis...")
    saved_files = analyze_and_plot_system(zos_manager, output_dir="zosapi_output")

    print("\nAnalysis completed! Generated plots:")
    for analysis_type, file_path in saved_files.items():
        print(f"  - {analysis_type}: {Path(file_path).name}")
    
    zos_manager.disconnect()
    print("Disconnected from Zemax OpticStudio")
    return True


if __name__ == "__main__":

    success = main()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
