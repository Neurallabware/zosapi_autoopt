import os
import sys
import unittest

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Assuming your class is saved here
from zosapi_autoopt.merit_function import MeritFunctionEditor
from zosapi_autoopt.zosapi_core import ZOSAPIManager

class TestMeritFunctionEditor(unittest.TestCase):
    """Final, corrected test script for all Merit Function features"""

    @classmethod
    def setUpClass(cls):
        cls.zos_manager = ZOSAPIManager()
        sample_file_path = os.path.join(cls.zos_manager.get_samples_dir(), "Sequential", "Objectives", "Cooke 40 degree field.zos")
        cls.zos_manager.open_file(sample_file_path)
        cls.mf_editor = MeritFunctionEditor(cls.zos_manager)

    @classmethod
    def tearDownClass(cls):
        if cls.zos_manager:
            cls.zos_manager.close()

    def setUp(self):
        """Reset the Merit Function before each test."""
        # This now correctly uses the restored method
        self.mf_editor.use_optimization_wizard('default', clear_existing=True)

    def test_01_initial_state_after_wizard(self):
        """Test the state after using the optimization wizard."""
        # The wizard should create more than one operand
        self.assertGreater(self.mf_editor.get_operand_count(), 1)
        operands = self.mf_editor.list_operands()
        self.assertEqual(operands[0]['type'], 'DMFS', "The first operand should be DMFS.")

    def test_02_clear_function(self):
        """Test that clearing the function leaves only one CONF operand."""
        self.mf_editor.clear_merit_function()
        self.assertEqual(self.mf_editor.get_operand_count(), 1, "Should have exactly one operand after clearing.")
        operands = self.mf_editor.list_operands()
        self.assertEqual(operands[0]['type'], 'CONF', "The only remaining operand should be CONF.")

    def test_03_add_and_list_operands(self):
        """Test adding and listing operands."""
        initial_count = self.mf_editor.get_operand_count()
        self.mf_editor.add_operand(operand_type='EFFL', target=100.0)
        
        self.assertEqual(self.mf_editor.get_operand_count(), initial_count + 1)
        
        operands = self.mf_editor.list_operands()
        self.assertEqual(operands[-1]['type'], 'EFFL', "The last operand should be the one we added.")
        self.assertEqual(operands[-1]['target'], 100.0)

    def test_04_edit_operand(self):
        """Test editing an operand."""
        self.mf_editor.add_operand(operand_type='ASTI', target=0.1, weight=1.0)
        index_to_edit = self.mf_editor.get_operand_count() - 1
        
        self.mf_editor.edit_operand(index=index_to_edit, target=0.0, weight=2.5)
        
        operands = self.mf_editor.list_operands()
        self.assertEqual(operands[index_to_edit]['target'], 0.0)
        self.assertEqual(operands[index_to_edit]['weight'], 2.5)

    def test_05_delete_operand(self):
        """Test deleting an operand."""
        self.mf_editor.add_operand(operand_type='TOTR') # Will be at index > 0
        initial_count = self.mf_editor.get_operand_count()
        
        # Delete the last added operand
        self.mf_editor.delete_operand(initial_count - 1)
        
        self.assertEqual(self.mf_editor.get_operand_count(), initial_count - 1)
        
        operands = self.mf_editor.list_operands()
        operand_types = [op['type'] for op in operands]
        self.assertNotIn('TOTR', operand_types)
# 在 TestMeritFunctionEditor 类中，添加以下两个新的测试方法：

    def test_08_run_global_optimization(self):
        """测试全局优化功能"""
        # 1. 使用向导建立一个适合全局优化的评价函数
        self.mf_editor.use_optimization_wizard('default')
        
        # 2. 确保有足够多的变量供全局优化探索
        lde = self.zos_manager.TheSystem.LDE
        for i in range(1, 6): # 将前5个面的曲率和厚度都设为变量
            lde.GetSurfaceAt(i).RadiusCell.MakeSolveVariable()
            lde.GetSurfaceAt(i).ThicknessCell.MakeSolveVariable()
            
        # 3. 运行全局优化 (为了快速测试，只运行很短的时间)
        result = self.mf_editor.run_global_optimization(timeout_seconds=5, save_top_n=1)
        
        # 4. 验证结果
        self.assertTrue(result.get('success', False), f"全局优化应成功，但失败了: {result.get('error')}")
        self.assertIn('top_results', result, "结果应包含top_results列表")
        # 更好的做法是检查评价函数是否有所改善
        self.assertLess(result['top_results'][0], result['initial_merit'], "全局优化后评价函数值应减小")

    def test_09_run_hammer_optimization(self):
        """测试锤形优化功能"""
        # 1. 使用向导建立评价函数
        self.mf_editor.use_optimization_wizard('default')
        
        # 2. 设置变量
        lde = self.zos_manager.TheSystem.LDE
        lde.GetSurfaceAt(2).RadiusCell.MakeSolveVariable()
        lde.GetSurfaceAt(4).RadiusCell.MakeSolveVariable()
            
        # 3. 运行锤形优化 (同样只运行很短时间)
        result = self.mf_editor.run_hammer_optimization(timeout_seconds=5)
        
        # 4. 验证结果
        self.assertTrue(result.get('success', False), f"锤形优化应成功，但失败了: {result.get('error')}")
        self.assertIn('final_merit', result, "结果应包含最终评价值")
        self.assertLess(result['final_merit'], result['initial_merit'], "锤形优化后评价函数值应减小")

if __name__ == '__main__':
    unittest.main()