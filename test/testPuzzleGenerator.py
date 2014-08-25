import unittest
from puzzleGenerator import PuzzleGenerator
from unittest.mock import MagicMock
from unittest.mock import call

class MockObject:
	pass

class TestPuzzleGenerator(unittest.TestCase):
	def setUp(self):
		self.factory = MockObject()
		self.table = MockObject()
		self.puzzle_1 = MockObject()
		self.puzzle_2 = MockObject()
		self.puzzleGen = PuzzleGenerator(self.factory)
		self.result_1 = MockObject()
		self.result_2 = MockObject()
		
		self.factory.getRandomPos = MagicMock(return_value=[(0, 1)])

	def test_constructPuzzleWithOnlyOneSolutionWithOneTry(self):
		self.factory.createPuzzleFromTable = MagicMock(return_value=self.puzzle_1)
		self.puzzleGen.solve = MagicMock(return_value=self.result_1)
		self.result_1.solutionCount = MagicMock(return_value = 1)

		puzzle = self.puzzleGen.constructPuzzleWithOnlySolution(self.table, 1)

		self.factory.getRandomPos.assert_called_once_with(1)
		self.factory.createPuzzleFromTable.assert_called_once_with(self.table, [(0, 1)])
		self.puzzleGen.solve.assert_called_once_with(self.puzzle_1)
		self.result_1.solutionCount.assert_called_once_with()
		self.assertEquals(self.puzzle_1, puzzle)

	def test_constructPuzzleWithOnlyOneSolutionWith2ndTry(self):
		self.factory.createPuzzleFromTable = MagicMock(side_effect=[self.puzzle_1, self.puzzle_2])
		self.puzzleGen.solve = MagicMock(side_effect=[self.result_1, self.result_2])
		self.result_1.solutionCount = MagicMock(return_value = 2)
		self.result_1.solutionDifference = MagicMock(return_value = (2, 3))
		self.result_2.solutionCount = MagicMock(return_value = 1)

		puzzle = self.puzzleGen.constructPuzzleWithOnlySolution(self.table, 1)

		self.assertEquals([call(self.table, [(0, 1)]), call(self.table, [(0, 1), (2, 3)])],self.factory.createPuzzleFromTable.mock_calls)
		self.assertEquals([call(self.puzzle_1), call(self.puzzle_2)], self.puzzleGen.solve.mock_calls)
		self.assertEquals(self.puzzle_2, puzzle)

class TestPuzzleGeneratorSolvePuzzle(unittest.TestCase):
	def test_solvePuzzle(self):
		pass