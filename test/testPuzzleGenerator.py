import unittest
from unittest.mock import MagicMock
from unittest.mock import call
from puzzleGenerator import *
from puzzle import *

class MockObj:
	pass

class TestPuzzleGenerator(unittest.TestCase):
	def setUp(self):
		self.table = MockObj()
		self.fromList = MockObj()
		self.toList = MockObj()
		self.puzzle_1 = MockObj()
		self.puzzle_2 = MockObj()
		self.result = MockObj()
		self.table.toElementList = MagicMock(name="table.toElementList", return_value=self.fromList)
		self.fromList.extractRandomly = MagicMock(name="fromList.extractRandomly", return_value=self.toList)
		self.toList.toPuzzle = MagicMock(name="toList.toPuzzle", return_value=self.puzzle_1)
		self.gen = PuzzleGenerator()
		self.gen.solve = MagicMock(name="gen.solve", return_value=self.result)
		self.result.solutionCnt = MagicMock(name="result.solutionCnt", return_value=1)

	def test_puzzleGeneratedWithInitialNumbersOnlyHaveOneSolution(self):
		puzzle = self.gen.generatePuzzle(self.table, 1)

		self.table.toElementList.assert_called_once_with()
		self.fromList.extractRandomly.assert_called_once_with(1)
		self.toList.toPuzzle.assert_called_once_with()
		self.gen.solve.assert_called_once_with(self.puzzle_1)
		self.result.solutionCnt.assert_called_once_with()
		self.assertEquals(self.puzzle_1, puzzle)

	def test_puzzleGeneratedWithInitialNumbersHaveMoreThanOneSolution(self):
		self.result.solutionCnt = MagicMock(name="result.solutionCnt", side_effect=[2, 1])
		self.result.difference = MagicMock(name="result.difference", return_value=(1, 2))
		self.toList.add = MagicMock(return_value=self.toList)
		self.fromList.retrieve = MagicMock(return_value="elem")
		self.toList.toPuzzle = MagicMock(name="toList.toPuzzle", side_effect=[self.puzzle_1, self.puzzle_2])
		
		puzzle = self.gen.generatePuzzle(self.table, 1)

		self.result.difference.assert_called_once_with()
		self.toList.add.assert_called_once_with("elem")
		self.fromList.retrieve.assert_called_once_with(1, 2)
		self.assertEquals([call(), call()], self.toList.toPuzzle.mock_calls)
		self.assertEquals([call(self.puzzle_1), call(self.puzzle_2)], self.gen.solve.mock_calls)
		self.assertEquals(self.puzzle_2, puzzle)

class TestPuzzleToList(unittest.TestCase):
	pass
		

class TestNumberOccupationList(unittest.TestCase):

	def test_listCreation(self):
		gridType = type('OneOneGrid', (Grid, ), {'bw':1, 'bh':1})
		gridType.EmptySign = '/'
		validator = MockObj()
		candidatesGen = MockObj()
		elemList = NumberOccupationList({(0, 0):1, (0, 1):2, (1, 0):3, (1, 1):4}, gridType, validator, candidatesGen, 2, 2)
		puzzle = elemList.toPuzzle()
		self.assertEquals('[[1, 2], [3, 4]]', puzzle.toString())

		