import unittest
from unittest.mock import MagicMock
from unittest.mock import call
from solutionFinder import *
from puzzle import *
from sudokuTableGen import *

class MockPuzzle:
	pass

class TestSolutionFinder(unittest.TestCase):

	def setUp(self):
		self.solver = SolutionFinder()
		self.solutions = SolutionsCollector()
		self.solutions.record = MagicMock(name="solutions.record")
		self.solutions.done = MagicMock(name="solutions.done", return_value=False)

		self.puzzle_one = MockPuzzle()
		self.puzzle_two = MockPuzzle()
		self.puzzle_three = MockPuzzle()
		
		self.puzzle_one.firstEmptyCell = MagicMock(return_value=(0,0))
		self.puzzle_one.candidatesAt = MagicMock(name="puzzle_one.candidates", side_effect=[[1, 2], [], []])
		self.puzzle_one.clone = MagicMock(name="puzzle_one.clone", return_value=self.puzzle_two)
		self.puzzle_one.clear = MagicMock(name="puzzle_one.clear")
		self.puzzle_one.change = MagicMock(name="puzzle_one.change")
		
	def test_solveASolvedPuzzle(self):
		self.puzzle_one.solved = MagicMock(name="puzzle.solved", return_value=True)
		self.puzzle_one.clone = MagicMock(name="puzzle.clone", return_value="puzzle.clone")

		self.solver.solve(self.puzzle_one, self.solutions)

		self.puzzle_one.solved.assert_called_once_with()
		self.puzzle_one.clone.assert_called_once_with()
		self.solutions.record.assert_called_once_with("puzzle.clone")

	def test_solveAPuzzleWithOneEmptyCellWithOneTry(self):
		self.solutions.done = MagicMock(name="solutions.done default", return_value=True)
		self.puzzle_one.solved = MagicMock(name="puzzle_one.solved", side_effect=[False, True])

		self.solver.solve(self.puzzle_one, self.solutions)
		
		self.solutions.record.assert_called_once_with(self.puzzle_two)
		self.assertEquals([call((0,0))], self.puzzle_one.clear.mock_calls)
		

	def test_solveAPuzzleWithOneEmptyCellWith2ndTry(self):
		self.puzzle_one.solved = MagicMock(name="puzzle_one.solved", side_effect=[False, False, True])

		self.solver.solve(self.puzzle_one, self.solutions)

		self.assertEquals([call((0,0), 1), call((0,0),2)], self.puzzle_one.change.mock_calls)
		self.assertEquals([call((0,0)), call((0,0))], self.puzzle_one.clear.mock_calls)
		self.solutions.record.assert_called_once_with(self.puzzle_two)


	def test_solveTryingToGetAllSolutions(self):
		self.puzzle_one.solved = MagicMock(name="puzzle_one.solved", side_effect=[False, True, True])

		self.solver.solve(self.puzzle_one, self.solutions)

		self.assertEquals([call((0,0), 1), call((0,0),2)], self.puzzle_one.change.mock_calls)
		self.assertEquals([call(self.puzzle_two), call(self.puzzle_two)], self.solutions.record.mock_calls)
	
	def test_solveStopTryingIfSolutionIsDone(self):
		self.puzzle_one.firstEmptyCell = MagicMock(return_value=(0,0))
		self.puzzle_one.solved = MagicMock(name="puzzle_one.solved", side_effect=[False, True])
		self.solutions.done = MagicMock(name="solutions.done", return_value=True)

		self.solver.solve(self.puzzle_one, self.solutions)

		self.puzzle_one.change.assert_called_once_with((0,0),1)
		self.solutions.done.assert_called_once_with()
		self.solutions.record.assert_called_once_with(self.puzzle_two)

class TestSolutionCollector(unittest.TestCase):
	def setUp(self):
		self.solutionCollector = SolutionsCollector()

	def test_SolutionCollectorNotDoneWhenNoPuzzleIsRecorded(self):
		self.assertFalse(self.solutionCollector.done())


	def test_SolutionCollectorRecordSolution(self):
		solutionCollector = SolutionsCollector()
		solutionCollector.record("puzzle")
		self.assertTrue(solutionCollector.done())
		self.assertEquals("puzzle", solutionCollector.result())

class TestSolutionFinderIntegration(unittest.TestCase):
	def setUp(self):
		self.puzzleFactory = RandomPuzzleFactory(4, 2, 2)	
				
	def test_findSolution(self):
		puzzle = self.puzzleFactory.emptyPuzzle()
		solutionCollector = SolutionsCollector()
		solver = SolutionFinder()

		solver.solve(puzzle, solutionCollector)
		self.assertTrue(solutionCollector.result().solved())

	# def test_get99Table(self):
	# 	tableGen = SudokuTableGenerator()
	# 	self.assertEquals("sharon", tableGen.getTable().toString())	