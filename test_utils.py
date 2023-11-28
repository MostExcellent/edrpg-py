import unittest
import json
from utils import Die, flatten_range, DieTable, ListTable

# Load test data
with open('./tables/table_test.json', 'r') as file:
    test_data = json.load(file)

class TestDie(unittest.TestCase):
    def test_die_roll_range(self):
        die = Die(6)
        for _ in range(100):  # Test with multiple rolls
            roll = die.roll()
            roll_value = roll[0] if isinstance(roll, list) else roll
            self.assertTrue(1 <= roll_value <= 6)

class TestFlattenRange(unittest.TestCase):
    def test_flatten_range(self):
        input_table = test_data['DieTableTest']
        expected_keys = list(range(1, 11))  # Expected keys from 1 to 10
        flattened_table = flatten_range(input_table)
        self.assertEqual(sorted(flattened_table.keys()), expected_keys)
        self.assertEqual(flattened_table[1], "Outcome A")
        self.assertEqual(flattened_table[10], "Outcome D")

class TestDieTable(unittest.TestCase):
    def setUp(self):
        self.die_type = 10  # Assuming a D10 for DieTableTest
        flattened_table = flatten_range(test_data['DieTableTest'])
        self.die_table = DieTable(self.die_type, flattened_table)

    def test_die_table_roll(self):
        roll = self.die_table.roll()
        roll_value = roll[0] if isinstance(roll, list) else roll
        self.assertIn(roll_value, ["Outcome A", "Outcome B", "Outcome C", "Outcome D"])

class TestListTable(unittest.TestCase):
    def setUp(self):
        self.list_table = ListTable(test_data['ListTableTest'])

    def test_list_table_roll(self):
        item = self.list_table.roll()
        item_value = item[0] if isinstance(item, list) else item
        self.assertIn(item_value, test_data['ListTableTest'])

if __name__ == '__main__':
    unittest.main()
