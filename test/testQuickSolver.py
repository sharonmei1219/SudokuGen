import unittest
from unittest.mock import MagicMock
from unittest.mock import call
from src.quickSolutionFinder import *
from src.puzzle import PuzzleFactory
from src.puzzle import _
from src.solutionCollector import SolutionCollectorWithoutMemory
from src.solutionCollector import SolutionCollectorWithMemory

class MockObj:
	pass
		

class TestQuickSolver(unittest.TestCase):
	def setUp(self):
		self.solutionCollector = MockObj()
		self.puzzle = MockObj()
		self.solver = QuickSolutionFinder()
		self.puzzle.change = MagicMock(name="change")
		self.puzzle.clone = MagicMock(name="clone", side_effect=['clone_1', 'clone_2'])
		self.puzzle.clear = MagicMock(name="clear")
		self.solutionCollector.record = MagicMock(name="record")

	def test_qs_impossibleToHaveSolutionAtFirstCall(self):
		self.solutionCollector.impossibleTohaveSolution = MagicMock(return_value=True)
		self.solver.solve(self.puzzle, self.solutionCollector)
		self.solutionCollector.impossibleTohaveSolution.assert_called_once_with(self.puzzle)

	def test_qs_allTry(self):
		self.puzzle.solved = MagicMock(side_effect=[False, True, True])
		self.puzzle.firstEmptyCell = MagicMock(return_value=(0, 0))
		self.puzzle.candidatesAt = MagicMock(return_value=[1, 2])
		self.solutionCollector.impossibleTohaveSolution = MagicMock(return_value=False)
		self.solutionCollector.done = MagicMock(side_effect=[False, True])

		self.solver.solve(self.puzzle, self.solutionCollector)

		self.assertEquals([call('clone_1'), call('clone_2')], self.solutionCollector.record.mock_calls)
		self.assertEquals([call((0, 0), 1), call((0, 0), 2)], self.puzzle.change.mock_calls)

	def test_qs_cutPathWhichHasOneFilledIn(self):
		self.puzzle.solved = MagicMock(side_effect=[False, True, True])
		self.puzzle.firstEmptyCell = MagicMock(return_value=(0, 0))
		self.puzzle.candidatesAt = MagicMock(return_value=[1, 2])
		self.solutionCollector.impossibleTohaveSolution = MagicMock(side_effect=[False, True, False])
		self.solutionCollector.done = MagicMock(side_effect=[False, True])

		self.solver.solve(self.puzzle, self.solutionCollector)

		self.assertEquals([call((0, 0), 1), call((0, 0), 2)], self.puzzle.change.mock_calls)
		self.solutionCollector.record.assert_called_once_with('clone_1')


class TestQuickSolverInt(unittest.TestCase):
	def test_integrationEmptyCollector(self):
		factory = PuzzleFactory(2, 1, 1)
		table = factory.creatPuzzleByMatrix([[2, 1],[1, 2]])
		puzzle = factory.creatPuzzleByMatrix([[_, _],[_, _]])
		collector = SolutionCollectorWithoutMemory(table)
		solver = QuickSolutionFinder()
		solver.solve(puzzle, collector)
		result = collector.result()
		self.assertEquals(2, result.solutionCount())

	def test_integrationWithMemoryCollector(self):
		factory = PuzzleFactory(2, 1, 1)
		table = factory.creatPuzzleByMatrix([[2, 1],[1, 2]])
		lastSolution = factory.creatPuzzleByMatrix([[1, 2], [2, 1]])
		puzzle = factory.creatPuzzleByMatrix([[_, _],[_, _]])
		collector = SolutionCollectorWithMemory(table, lastSolution)
		solver = QuickSolutionFinder()
		solver.solve(puzzle, collector)
		result = collector.result()
		self.assertEquals(1, result.solutionCount())

		
		