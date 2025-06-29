#!/usr/bin/env python3
"""
ZOSAPI Multi-Wavelength Multi-Field Analysis Demo
=================================================

This script demonstrates the enhanced high-level plotting functions that now properly
support both multi-field and multi-wavelength analysis, following the official 
examples 22 and 23.

Key improvements:
- True multi-wavelength support
- Flexible field/wavelength selection
- Proper wavelength color coding and legends
- Control options: "all", "single", or specific indices
"""

import os
import sys
from pathlib import Path

# Add the current directory to sys.path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from zosapi_core import ZOSAPIManager
from zosapi_analysis import ZOSAnalyzer
from zosapi_plotting import (
    plot_multifield_spots, 
    plot_multifield_rayfan, 
    plot_system_mtf, 
    plot_comprehensive_analysis, 
    analyze_and_plot_system
)


def test_multiwavelength_analysis():
    """
    Test enhanced multi-wavelength multi-field analysis capabilities
    """
    print("="*70)
    print("ZOSAPI Enhanced Multi-Wavelength Multi-Field Analysis Demo")
    print("="*70)
    
    try:
        # Connect to Zemax
        zos_manager = ZOSAPIManager()
        if not zos_manager.is_connected:
            print("❌ Failed to connect to Zemax OpticStudio")
            return False
        
        print("✅ Connected to Zemax OpticStudio")
        
        # Try to load a sample file with multiple wavelengths
        sample_files = [
            r"C:\Program Files\ANSYS Inc\v242\Zemax OpticStudio\ZemaxData\Samples\Sequential\Objectives\Cooke 40 degree field.zos",
            # Add more paths as needed
        ]
        
        loaded = False
        for sample_file in sample_files:
            if os.path.exists(sample_file):
                try:
                    zos_manager.load_file(sample_file)
                    print(f"✅ Loaded sample file: {Path(sample_file).name}")
                    loaded = True
                    break
                except:
                    continue
        
        if not loaded:
            # Create a multi-wavelength system
            zos_manager.new_file()
            system = zos_manager.TheSystem
            
            # Add multiple wavelengths
            system.SystemData.Wavelengths.GetWavelength(1).Wavelength = 0.486  # F-line (blue)
            system.SystemData.Wavelengths.AddWavelength(0.587, 1.0)  # d-line (yellow) - primary
            system.SystemData.Wavelengths.AddWavelength(0.656, 1.0)  # C-line (red)
            
            # Add multiple fields
            system.SystemData.Fields.GetField(1).Y = 0.0
            system.SystemData.Fields.AddField(0, 10.0, 1.0)
            system.SystemData.Fields.AddField(0, 20.0, 1.0)
            
            # Add simple doublet lens
            system.LDE.InsertNewSurfaceAt(1)
            surf1 = system.LDE.GetSurfaceAt(1)
            surf1.Radius = 50.0
            surf1.Thickness = 5.0
            surf1.Material = "N-BK7"
            
            system.LDE.InsertNewSurfaceAt(2)
            surf2 = system.LDE.GetSurfaceAt(2)
            surf2.Radius = -50.0
            surf2.Thickness = 2.0
            
            system.LDE.InsertNewSurfaceAt(3)
            surf3 = system.LDE.GetSurfaceAt(3)
            surf3.Radius = 100.0
            surf3.Thickness = 3.0
            surf3.Material = "SF10"
            
            system.LDE.InsertNewSurfaceAt(4)
            surf4 = system.LDE.GetSurfaceAt(4)
            surf4.Radius = -100.0
            surf4.Thickness = 100.0
            
            print("✅ Created multi-wavelength test system")
        
        # Get system information
        system = zos_manager.TheSystem
        num_fields = system.SystemData.Fields.NumberOfFields
        num_wavelengths = system.SystemData.Wavelengths.NumberOfWavelengths
        
        print(f"📊 System: {num_fields} fields, {num_wavelengths} wavelengths")
        
        # Show wavelength information
        print("🌈 Wavelengths:")
        for i in range(1, num_wavelengths + 1):
            wave = system.SystemData.Wavelengths.GetWavelength(i)
            primary = "★" if wave.IsPrimary else " "
            print(f"   {primary} Wave {i}: {wave.Wavelength:.3f} μm (weight: {wave.Weight:.1f})")
        
        # Show field information
        print("🎯 Fields:")
        for i in range(1, num_fields + 1):
            field = system.SystemData.Fields.GetField(i)
            print(f"     Field {i}: Y = {field.Y:.1f}")
        
        # Initialize analyzer
        analyzer = ZOSAnalyzer(zos_manager)
        
        # Set up output directory
        output_dir = current_dir / "multiwave_outputs"
        output_dir.mkdir(exist_ok=True)
        
        print("\n" + "="*50)
        print("Testing Different Field/Wavelength Combinations")
        print("="*50)
        
        # Test 1: All fields, all wavelengths
        print("\n1️⃣ ALL FIELDS + ALL WAVELENGTHS")
        plot_multifield_spots(zos_manager, analyzer, 
                             fields="all", wavelengths="all",
                             save_path=str(output_dir / "spots_all_all.png"))
        
        plot_multifield_rayfan(zos_manager, analyzer, 
                              fields="all", wavelengths="all",
                              save_path=str(output_dir / "rayfan_all_all.png"))
        print("   ✅ Generated: All fields + All wavelengths plots")
        
        # Test 2: All fields, single wavelength (primary)
        print("\n2️⃣ ALL FIELDS + PRIMARY WAVELENGTH")
        plot_multifield_spots(zos_manager, analyzer, 
                             fields="all", wavelengths="single",
                             save_path=str(output_dir / "spots_all_single.png"))
        
        plot_multifield_rayfan(zos_manager, analyzer, 
                              fields="all", wavelengths="single",
                              save_path=str(output_dir / "rayfan_all_single.png"))
        print("   ✅ Generated: All fields + Primary wavelength plots")
        
        # Test 3: Single field, all wavelengths
        print("\n3️⃣ SINGLE FIELD + ALL WAVELENGTHS")
        plot_multifield_spots(zos_manager, analyzer, 
                             fields="single", wavelengths="all",
                             save_path=str(output_dir / "spots_single_all.png"))
        
        plot_multifield_rayfan(zos_manager, analyzer, 
                              fields="single", wavelengths="all",
                              save_path=str(output_dir / "rayfan_single_all.png"))
        print("   ✅ Generated: Single field + All wavelengths plots")
        
        # Test 4: Specific field and wavelength combinations
        if num_fields >= 2 and num_wavelengths >= 2:
            print("\n4️⃣ CUSTOM FIELD/WAVELENGTH SELECTION")
            plot_multifield_spots(zos_manager, analyzer, 
                                 fields=[0, 1], wavelengths=[0, 2],  # First 2 fields, wavelengths 1&3
                                 save_path=str(output_dir / "spots_custom.png"))
            
            plot_multifield_rayfan(zos_manager, analyzer, 
                                  fields=[0, 1], wavelengths=[0, 2],
                                  save_path=str(output_dir / "rayfan_custom.png"))
            print("   ✅ Generated: Custom field/wavelength selection plots")
        
        # Test 5: MTF analysis with different configurations
        print("\n5️⃣ MTF ANALYSIS")
        plot_system_mtf(zos_manager, 
                       fields="all", wavelengths="all", max_frequency=100,
                       save_path=str(output_dir / "mtf_all_all.png"))
        
        plot_system_mtf(zos_manager, 
                       fields="single", wavelengths="single", max_frequency=100,
                       save_path=str(output_dir / "mtf_single_single.png"))
        print("   ✅ Generated: MTF analysis plots")
        
        # Test 6: Comprehensive analysis
        print("\n6️⃣ COMPREHENSIVE ANALYSIS")
        plot_comprehensive_analysis(zos_manager, analyzer, 
                                   fields="all", wavelengths="all",
                                   save_path=str(output_dir / "comprehensive_all_all.png"))
        
        plot_comprehensive_analysis(zos_manager, analyzer, 
                                   fields="all", wavelengths="single",
                                   save_path=str(output_dir / "comprehensive_all_single.png"))
        print("   ✅ Generated: Comprehensive analysis plots")
        
        # Test 7: Ultimate one-liner with options
        print("\n7️⃣ ULTIMATE ONE-LINER (with options)")
        
        # All fields, all wavelengths
        saved_files_all = analyze_and_plot_system(
            zos_manager, str(output_dir / "oneliner_all"), 
            fields="all", wavelengths="all"
        )
        
        # Single field, primary wavelength
        saved_files_single = analyze_and_plot_system(
            zos_manager, str(output_dir / "oneliner_single"), 
            fields="single", wavelengths="single"
        )
        
        print("   ✅ One-liner analysis completed!")
        print("   📁 All configuration files:")
        for analysis_type, file_path in saved_files_all.items():
            print(f"      • {analysis_type}: {Path(file_path).name}")
        
        print("\n" + "="*70)
        print("🎉 SUCCESS! Enhanced Multi-Wavelength Analysis Complete!")
        print("="*70)
        print("📊 Key Features Demonstrated:")
        print("   ✅ True multi-wavelength support")
        print("   ✅ Flexible field/wavelength selection")
        print("   ✅ Proper wavelength color coding")
        print("   ✅ Comprehensive legends and labels")
        print("   ✅ All/single/custom selection modes")
        print("   ✅ One-liner function with full control")
        print(f"📂 Results saved in: {output_dir}")
        
        print("\n💡 Usage Examples:")
        print("   # All fields, all wavelengths")
        print("   plot_multifield_spots(zos_manager, analyzer, 'all', 'all')")
        print("   # Single field, primary wavelength")
        print("   plot_multifield_spots(zos_manager, analyzer, 'single', 'single')")
        print("   # Custom selection")
        print("   plot_multifield_spots(zos_manager, analyzer, [0,1], [0,2])")
        print("   # One-liner with options")
        print("   analyze_and_plot_system(zos_manager, output_dir, 'all', 'all')")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'zos_manager' in locals():
            try:
                zos_manager.disconnect()
                print("🔌 Disconnected from Zemax OpticStudio")
            except:
                pass


if __name__ == "__main__":
    print("ZOSAPI Enhanced Multi-Wavelength Analysis Demo")
    print("This demonstrates TRUE multi-wavelength support following official examples!\n")
    
    success = test_multiwavelength_analysis()
    
    if success:
        print("\n🎯 The enhanced functions now provide:")
        print("   • Complete multi-wavelength support")
        print("   • Flexible field/wavelength selection")
        print("   • Following official Zemax examples 22 & 23")
        print("   • Professional multi-color visualization")
        print("   • Easy-to-use control parameters")
    else:
        print("\n❌ Demo failed. Please check your Zemax installation.")
    
    input("\nPress Enter to exit...")
