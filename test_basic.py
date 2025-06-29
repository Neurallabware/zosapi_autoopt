"""
简单测试脚本
用于验证 Zemax OpticStudio Python API 封装库的基本功能
"""

import sys
import os

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        # 测试核心模块
        from zosapi_core import ZOSAPIManager, quick_connect
        print("✓ zosapi_core 导入成功")
        
        # 测试工具模块
        from zosapi_utils import ZOSDataProcessor
        print("✓ zosapi_utils 导入成功")
        
        # 测试绘图模块
        from zosapi_plotting import ZOSPlotter
        print("✓ zosapi_plotting 导入成功")
        
        # 测试分析模块
        from zosapi_analysis import ZOSAnalyzer
        print("✓ zosapi_analysis 导入成功")
        
        # 测试配置模块
        import config
        print("✓ config 导入成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ 导入失败: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ 未知错误: {str(e)}")
        return False


def test_basic_functionality():
    """测试基本功能"""
    print("\n测试基本功能...")
    
    try:
        # 测试配置
        from config import get_config, validate_settings
        
        config = get_config()
        print(f"✓ 配置加载成功，包含 {len(config)} 个配置项")
        
        # 验证设置
        issues = validate_settings()
        if issues:
            print(f"⚠ 配置验证发现问题: {issues}")
        else:
            print("✓ 配置验证通过")
        
        # 测试工具函数
        from zosapi_utils import degrees_to_radians, mm_to_microns
        
        rad_val = degrees_to_radians(90)
        micron_val = mm_to_microns(1.0)
        
        print(f"✓ 工具函数测试通过: 90° = {rad_val:.6f} rad, 1mm = {micron_val:.1f} μm")
        
        # 测试绘图器初始化
        from zosapi_plotting import ZOSPlotter
        plotter = ZOSPlotter()
        print("✓ 绘图器初始化成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 基本功能测试失败: {str(e)}")
        return False


def test_zosapi_connection():
    """测试 ZOSAPI 连接（需要 OpticStudio）"""
    print("\n测试 ZOSAPI 连接...")
    
    try:
        from zosapi_core import quick_connect
        
        # 尝试连接（不会自动连接）
        print("正在尝试连接到 OpticStudio...")
        
        # 注意：这个测试需要 OpticStudio 已安装且可用
        zos_manager = quick_connect()
        
        if zos_manager.is_connected:
            print("✓ ZOSAPI 连接成功")
            
            # 测试系统信息获取
            license_type = zos_manager.get_license_type()
            print(f"✓ 许可证类型: {license_type}")
            
            # 获取样本目录
            samples_dir = zos_manager.get_samples_dir()
            print(f"✓ 样本目录: {samples_dir}")
            
            # 断开连接
            zos_manager.disconnect()
            print("✓ 连接已断开")
            
            return True
        else:
            print("✗ ZOSAPI 连接失败")
            return False
            
    except Exception as e:
        print(f"✗ ZOSAPI 连接测试失败: {str(e)}")
        print("  这可能是因为:")
        print("  1. OpticStudio 未安装")
        print("  2. 许可证不支持 API")
        print("  3. 路径配置不正确")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("Zemax OpticStudio Python API 封装库测试")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_imports),
        ("基本功能", test_basic_functionality),
        ("ZOSAPI连接", test_zosapi_connection)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name}测试 ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name}测试异常: {str(e)}")
            results[test_name] = False
    
    # 总结结果
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "通过" if result else "失败"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！封装库可以正常使用。")
    else:
        print("⚠ 部分测试失败，请检查相关配置和环境。")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
