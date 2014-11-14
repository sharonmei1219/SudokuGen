import unittest
from puzzleGenerator import *
from unittest.mock import MagicMock
from unittest.mock import call
from puzzle import *
from solutionFinder import *
from quickSolutionFinder import *
from sudokuTableGen import *
from solutionCollector import *
import cProfile
from humanSolver import *

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



class TestPuzzleGeneratorIntegration(unittest.TestCase):

	def test_generate99Sudoku(self):
		tableGen = SudokuTableGenerator()

		factory = PuzzleFactory(9, 3, 3)
		solutionFinder = SolutionFinder()
		solver = MultiSolutionSolver(solutionFinder)
		puzzleGen = PuzzleGenerator(factory, solver)

	def test_quickPuzzleGen(self):
		tableGen = SudokuTableGenerator()

		factory = PuzzleFactory(9, 3, 3)
		solutionFinder = QuickSolutionFinder()
		solver = QuickSolver(solutionFinder)
		puzzleGen = QuickPuzzleGenerator(factory, solver)

class TestHoleDigger(unittest.TestCase):

	def setUp(self):
		self.gen = MockObject()
		self.gen.refresh = MagicMock()
		self.table = MockObject()
		self.digger = HoleDigger(self.gen)
		self.puzzleAfterDiggerHole = MockObject()
		pass

	def test_DigHoleAfterPuzzleGenerated(self):
		initPuzzle = MockObject()
		pos = [(0, 0)]
		self.gen.constructPuzzleWithInitialPos = MagicMock(return_value=(initPuzzle, pos))
		self.gen.randomPos = MagicMock(return_value=[(1, 1)])
		self.digger.removePosFromPuzzle = MagicMock(return_value=[(1, 1)])
		self.digger.createPuzzle = MagicMock(return_value=self.puzzleAfterDiggerHole)

		self.digger.constructPuzzleWithOnlySolution(self.table, 1)
		self.gen.constructPuzzleWithInitialPos.assert_called_once_with(self.table, [(1, 1)])
		self.digger.removePosFromPuzzle.assert_called_once_with(self.table, [(1, 1), (0, 0)], 1)

	def test_digOneHoleWithOneTry(self):
		result = MockObject()
		result.solutionCount = MagicMock(return_value = 1)
		self.digger.createPuzzle = MagicMock(return_value=self.puzzleAfterDiggerHole)
		self.digger.solve = MagicMock(return_value=result)

		puzzle = self.digger.removePosFromPuzzle(self.table, [(1, 1), (0, 0)], 1)

		self.digger.createPuzzle.assert_called_once_with(self.table, [(0, 0)])
		self.digger.solve.assert_called_once_with(self.puzzleAfterDiggerHole)
		result.solutionCount.assert_called_once_with()

		self.assertEquals([(0, 0)], puzzle)
	
	def test_digOneHoleWithTwoTries(self):
		result = MockObject()
		puzzle_1 = MockObject()
		puzzle_2 = MockObject()
		result.solutionCount = MagicMock(side_effect = [2, 1])
		self.digger.createPuzzle = MagicMock(side_effect=[puzzle_1, puzzle_2])
		self.digger.solve = MagicMock(return_value=result)

		pos = self.digger.removePosFromPuzzle(self.table, [(1, 1), (0, 0)], 1)

		self.assertEquals([call(self.table, [(0, 0)]), call(self.table, [(1, 1)])], self.digger.createPuzzle.mock_calls)

		self.assertEquals([call(puzzle_1), call(puzzle_2)], self.digger.solve.mock_calls)
		self.assertEquals([(1, 1)], pos)

	def test_digOneHoleFaledWithTwoTries(self):
		result = MockObject()
		puzzle_1 = MockObject()
		puzzle_2 = MockObject()
		result.solutionCount = MagicMock(side_effect = [2, 2])
		self.digger.createPuzzle = MagicMock(side_effect=[puzzle_1, puzzle_2])
		self.digger.solve = MagicMock(return_value=result)

		pos = self.digger.removePosFromPuzzle(self.table, [(1, 1), (0, 0)], 1)

		self.assertEquals([call(self.table, [(0, 0)]), call(self.table, [(1, 1)])], self.digger.createPuzzle.mock_calls)

		self.assertEquals([call(puzzle_1), call(puzzle_2)], self.digger.solve.mock_calls)
		self.assertEquals([(1, 1), (0, 0)], pos)

	def test_integration(self):
		tableGen = SudokuTableGenerator()

		# factory = PuzzleFactory(9, 3, 3)
		# solutionFinder = QuickSolutionFinder()
		# solver = QuickSolver(solutionFinder)
		# puzzleGen = QuickPuzzleGenerator(factory, solver)
		# digger = HoleDigger(puzzleGen)
		# for i in range(1):
		# 	table = tableGen.getTable()
		# 	puzzle = digger.constructPuzzleWithOnlySolution(table, 20)
		# 	slow_solutionFinder = SolutionFinder()
		# 	slow_solver = MultiSolutionSolver(slow_solutionFinder)
		# hc = HumanSolver()
		# hc.solve(puzzle)
		# self.assertEquals("sharon", puzzle.toString())