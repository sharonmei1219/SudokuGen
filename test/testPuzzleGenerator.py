import unittest
from puzzleGenerator import *
from unittest.mock import MagicMock
from unittest.mock import call
from puzzle import *
from solutionFinder import *
from sudokuTableGen import *
import cProfile

class MockObject:
	pass

class TestPuzzleGenerator(unittest.TestCase):
	def setUp(self):
		self.factory = MockObject()
		self.table = MockObject()
		self.puzzle_1 = MockObject()
		self.puzzle_2 = MockObject()
		self.solver = MockObject()
		self.puzzleGen = PuzzleGenerator(self.factory, self.solver)
		self.result_1 = MockObject()
		self.result_2 = MockObject()
		
		self.factory.getRandomPos = MagicMock(return_value=[(0, 1)])

	def test_constructPuzzleWithOnlyOneSolutionWithOneTry(self):
		self.factory.createPuzzleFromTable = MagicMock(return_value=self.puzzle_1)
		self.solver.solve = MagicMock(return_value=self.result_1)
		self.result_1.solutionCount = MagicMock(return_value = 1)

		puzzle = self.puzzleGen.constructPuzzleWithOnlySolution(self.table, 1)

		self.factory.getRandomPos.assert_called_once_with(1)
		self.factory.createPuzzleFromTable.assert_called_once_with(self.table, [(0, 1)])
		self.solver.solve.assert_called_once_with(self.puzzle_1)
		self.result_1.solutionCount.assert_called_once_with()
		self.assertEquals(self.puzzle_1, puzzle)

	def test_constructPuzzleWithOnlyOneSolutionWith2ndTry(self):
		self.factory.createPuzzleFromTable = MagicMock(side_effect=[self.puzzle_1, self.puzzle_2])
		self.solver.solve = MagicMock(side_effect=[self.result_1, self.result_2])
		self.result_1.solutionCount = MagicMock(return_value = 2)
		self.result_1.solutionDifference = MagicMock(return_value = (2, 3))
		self.result_2.solutionCount = MagicMock(return_value = 1)

		puzzle = self.puzzleGen.constructPuzzleWithOnlySolution(self.table, 1)

		self.assertEquals([call(self.table, [(0, 1)]), call(self.table, [(0, 1), (2, 3)])],self.factory.createPuzzleFromTable.mock_calls)
		self.assertEquals([call(self.puzzle_1), call(self.puzzle_2)], self.solver.solve.mock_calls)
		self.assertEquals(self.puzzle_2, puzzle)

class TestMutiSolutionSolver(unittest.TestCase):
	def test_OnlyOneSolutionAvailable(self):
		solutionFinder = MockObject()
		solutionFinder.solve = MagicMock()
		puzzle = MagicMock()
		collection = MagicMock()
		collectedResult = MagicMock()
		solver = MultiSolutionSolver(solutionFinder)
		solver.newSolutionCollections = MagicMock(return_value=collection)
		collection.result = MagicMock(return_value=collectedResult)

		result = solver.solve(puzzle)

		self.assertEquals(result, collectedResult)
		solver.newSolutionCollections.assert_called_once_with()
		collection.result.assert_called_once_with()
		solutionFinder.solve.assert_called_once_with(puzzle, collection)

class TestMultiSolutionCollector(unittest.TestCase):
	def setUp(self):
		self.collector = MultisolutionCollector()
		self.puzzle_1 = MockObject()
		self.puzzle_2 = MockObject()

		self.puzzle_1.compare = MagicMock(name="puzzle_1.compare", return_value = (0, 1))
	
	def test_OnlyOneSolutionAvailable(self):
		self.collector.record(self.puzzle_1)
		self.assertEquals(1, self.collector.result().solutionCount())

	def test_OnlyTwoSolutionAvailable(self):
		self.collector.record(self.puzzle_1)
		self.collector.record(self.puzzle_2)

		result = self.collector.result()

		self.puzzle_1.compare.assert_called_once_with(self.puzzle_2)
		self.assertEquals(2, result.solutionCount())
		self.assertEquals((0, 1), result.solutionDifference())

	def test_solultionCollectingNotDoneEvenAfterOneSolutionFind(self):
		self.collector.record(self.puzzle_1)
		self.assertFalse(self.collector.done())

	def test_solutionCollectingDoneAfter2SolutionsFound(self):
		self.collector.record(self.puzzle_1)
		self.collector.record(self.puzzle_2)
		self.assertTrue(self.collector.done())

class TestPuzzleGeneratorIntegration(unittest.TestCase):
	# def test_generateASimpleWithOneShot(self):
	# 	factory = RandomPuzzleFactory(2, 1, 1)
	# 	solutionFinder = SolutionFinder()
	# 	solver = MultiSolutionSolver(solutionFinder)
	# 	puzzleGen = PuzzleGenerator(factory, solver)

	# 	table = factory.creatPuzzleByMatrix([[1, 2], [2, 1]])
	# 	puzzle = puzzleGen.constructPuzzleWithOnlySolution(table, 0)

	# 	self.assertEquals("sharon", puzzle.toString())

	def test_generate99Sudoku(self):
		tableGen = SudokuTableGenerator()
		# for i in range(100):
		# 	table = tableGen.getTable()

		factory = RandomPuzzleFactory(9, 3, 3)
		solutionFinder = SolutionFinder()
		solver = MultiSolutionSolver(solutionFinder)
		puzzleGen = PuzzleGenerator(factory, solver)

		for i in range(10):
			table = tableGen.getTable()
			puzzle = puzzleGen.constructPuzzleWithOnlySolution(table, 27)
		self.assertEquals("sharon", puzzle.toString())
		pass