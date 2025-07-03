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


if __name__ == '__main__':
    unittest.main()