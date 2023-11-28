from abc import ABC, abstractmethod
import random

def flatten_range(table):
    """
    Converts a table with range strings as keys into a table with individual integers as keys.

    Args:
    - table (dict): A dictionary where keys are range strings (e.g., '1-16') and values are outcomes.

    Returns:
    - dict: A new dictionary with individual integers as keys and corresponding outcomes as values.
    """
    flattened_table = {}
    for range_str, outcome in table.items():
        # Handle single value and range values differently
        if '-' in range_str:
            start, end = map(int, range_str.split('-'))
            for i in range(start, end + 1):
                flattened_table[i] = outcome
        else:
            flattened_table[int(range_str)] = outcome
    return flattened_table

class Die:
    def __init__(self, die_type):
        self.die_type = die_type

    def roll(self, n=1):
        return [random.randint(1, self.die_type) for _ in range(n)]

class Table(ABC):
    def __init__(self, table):
        self.table = table

    @abstractmethod
    def roll(self, n=1):
        pass

class DieTable(Table):
    def __init__(self, die, flattened_table):
        super().__init__(flattened_table)
        self.die = Die(die) if isinstance(die, int) else die

    def roll(self, n=1):
        results = self.die.roll(n)
        return [self.table.get(result, result) for result in results]

class ListTable(Table):
    def __init__(self, table):
        super().__init__(table)

    def roll(self, n=1):
        return random.choices(self.table, k=n)
