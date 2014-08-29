import unittest
from unittest.mock import MagicMock
from src.holeDigger import HoleDigger

class MockObject:
	pass

class TestHoleDigger(unittest.TestCase):
	def testDigOneHole(self):
		puzzle_1 = MockObject()
		puzzle_2 = MockObject()
		table = MockObject()
		result = MockObject()
		holeDigger = HoleDigger()

		puzzle_1.numberedPos = MagicMock(return_value=[(0, 0), (0, 1)])
		holeDigger.randomlyRemoveOne = MagicMock(return_value=[(0, 0)])
		holeDigger.createPuzzle = MagicMock(return_value = puzzle_2)
		holeDigger.solve = MagicMock(return_value = result)
		result.solutionCount = MagicMock(return_value = 1)

		newPuzzle = holeDigger.dig(table, puzzle_1, 1)

		self.assertEquals(puzzle_2, newPuzzle)
		puzzle_1.numberedPos.assert_called_once_with()
		holeDigger.randomlyRemoveOne.assert_called_once_with([(0, 0), (0, 1)])
		holeDigger.createPuzzle.assert_called_once_with(table, [(0, 0)])
		holeDigger.solve.assert_called_once_with(table, puzzle_1)
		result.solutionCount.assert_called_once_with()
		pass

	def testDigOneHoleWith2Tries(self):
		pass
	pass
