import unittest
from unittest.mock import MagicMock
from unittest.mock import call
from src.solutionFinder import *
from puzzle import *
from sudokuTableGen import *

class MockPuzzle:
	pass

class TestSolutionFinder(unittest.TestCase):

	# puzzle_one is the original puzzle, it has 2 candidates for its first empty cell, [1, 2] 
	# puzzle_one.fill(1) will get puzzle_two
	# puzzle_one.fill(2) will get puzzle_three
	def setUp(self):
		self.solver = SolutionFinder()
		self.solutions = SolutionsCollector()
		self.solutions.record = MagicMock(name="solutions.record")
		self.solutions.done = MagicMock(name="solutions.done default", return_value=False)

		self.puzzle_one = MockPuzzle()
		self.puzzle_two = MockPuzzle()
		self.puzzle_three = MockPuzzle()
		
		self.puzzle_one.solved = MagicMock(name="puzzle_one.solved", return_value=False)
		self.puzzle_one.candidates = MagicMock(name="puzzle_one.candidates", return_value=[1, 2])
		puzzlesToReturn = {1:self.puzzle_two, 2:self.puzzle_three}
		def side_effect(arg):
			return puzzlesToReturn[arg]
			pass
		self.puzzle_one.fill = MagicMock(name="puzzle_one.fill", side_effect=side_effect)

		self.puzzle_two.clone = MagicMock(name="puzzle_two.clone", return_value="puzzle_two.clone")
		self.puzzle_two.candidates = MagicMock(name="puzzle_two.candidates", return_value=[])
		self.puzzle_three.clone = MagicMock(name="puzzle_three.clone", return_value="puzzle_three.clone")
		
	def test_solveASolvedPuzzle(self):
		self.puzzle_one.solved = MagicMock(name="puzzle.solved", return_value=True)
		self.puzzle_one.clone = MagicMock(name="puzzle.clone", return_value="puzzle.clone")

		self.solver.solve(self.puzzle_one, self.solutions)

		self.puzzle_one.solved.assert_called_once_with()
		self.puzzle_one.clone.assert_called_once_with()
		self.solutions.record.assert_called_once_with("puzzle.clone")

	def test_solveAPuzzleWithOneEmptyCellWithOneTry(self):
		self.puzzle_one.candidates = MagicMock(name="puzzle_one.candidates", return_value=[1])
		self.puzzle_two.solved = MagicMock(name="puzzle_two.solved", return_value=True)

		self.solver.solve(self.puzzle_one, self.solutions)

		self.puzzle_one.fill.assert_called_once_with(1)
		self.solutions.record.assert_called_once_with("puzzle_two.clone")
		

	def test_solveAPuzzleWithOneEmptyCellWith2ndTry(self):
		self.puzzle_two.solved = MagicMock(name="puzzle_two.solved", return_value=False)
		self.puzzle_three.solved = MagicMock(name="puzzle_three.solved", return_value=True)

		self.solver.solve(self.puzzle_one, self.solutions)

		self.assertEquals([call(1), call(2)], self.puzzle_one.fill.mock_calls)
		self.solutions.record.assert_called_once_with("puzzle_three.clone")


	def test_solveTryingToGetAllSolutions(self):
		self.puzzle_two.solved = MagicMock(name="puzzle_two.solved", return_value=True)
		self.puzzle_three.solved = MagicMock(name="puzzle_three.solved", return_value=True)

		self.solver.solve(self.puzzle_one, self.solutions)

		self.assertEquals([call(1), call(2)], self.puzzle_one.fill.mock_calls)
		self.assertEquals([call("puzzle_two.clone"), call("puzzle_three.clone")], self.solutions.record.mock_calls)
	
	def test_solveStopTryingIfSolutionIsDone(self):
		self.puzzle_two.solved = MagicMock(name="puzzle_two.solved", return_value=True)
		self.solutions.done = MagicMock(name="solutions.done", return_value=True)

		self.solver.solve(self.puzzle_one, self.solutions)

		self.puzzle_one.fill.assert_called_once_with(1)
		self.solutions.done.assert_called_once_with()
		self.solutions.record.assert_called_once_with("puzzle_two.clone")

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
		_ = Grid.EmptySign
		puzzle = self.puzzleFactory.emptyPuzzle()
		solutionCollector = SolutionsCollector()
		solver = SolutionFinder()

		solver.solve(puzzle, solutionCollector)
		self.assertTrue(solutionCollector.result().solved())

	# def test_get99Table(self):
	# 	tableGen = SudokuTableGenerator()
	# 	self.assertEquals("sharon", tableGen.getTable().toString())	