import unittest
from sudokuTableGen import *
import random
from unittest.mock import MagicMock

class TestTableGen(unittest.TestCase):
	def test_gen22RamdomTable(self):
		tableGenerator = TableGenerator(2, 1)
		randint = random.randint
		random.randint = MagicMock(side_effect=[0, 0])
		table = tableGenerator.getTable()
		self.assertEqual('[[1, 2], [2, 1]]', table.toString())
		random.randint = randint
		pass

	def test_gen33RamdomTable(self):
		tableGenerator = TableGenerator(3, 1)
		randint = random.randint
		random.randint = MagicMock(side_effect=[0, 0, 0, 0, 0, 0, 0, 0])
		table = tableGenerator.getTable()
		self.assertEqual('[[1, 2, 3], [2, 3, 1], [3, 1, 2]]', table.toString())
		random.randint = randint
		pass

	def test_gen33RamdomTableNumber2(self):
		tableGenerator = TableGenerator(3, 1)
		randint = random.randint
		random.randint = MagicMock(side_effect=[1, 0, 0, 0, 0, 0, 0, 0])
		table = tableGenerator.getTable()
		self.assertEqual('[[1, 2, 3], [3, 1, 2], [2, 3, 1]]', table.toString())
		random.randint = randint
		pass