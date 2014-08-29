import unittest
from src.solutionCollector import * 
from unittest.mock import MagicMock

class MockObject:
	pass

class TestMultiSolutionCollector(unittest.TestCase):
	def setUp(self):
		self.collector = MultisolutionCollector()
		self.puzzle_1 = MockObject()
		self.puzzle_2 = MockObject()

		self.puzzle_1.differences = MagicMock(name="puzzle_1.compare", return_value = (0, 1))
	
	def test_OnlyOneSolutionAvailable(self):
		self.collector.record(self.puzzle_1)
		self.assertEquals(1, self.collector.result().solutionCount())

	def test_OnlyTwoSolutionAvailable(self):
		self.collector.record(self.puzzle_1)
		self.collector.record(self.puzzle_2)

		result = self.collector.result()

		self.puzzle_1.differences.assert_called_once_with(self.puzzle_2)
		self.assertEquals(2, result.solutionCount())
		self.assertEquals((0, 1), result.solutionDifference())

	def test_solultionCollectingNotDoneEvenAfterOneSolutionFind(self):
		self.collector.record(self.puzzle_1)
		self.assertFalse(self.collector.done())

	def test_solutionCollectingDoneAfter2SolutionsFound(self):
		self.collector.record(self.puzzle_1)
		self.collector.record(self.puzzle_2)
		self.assertTrue(self.collector.done())


class TestSolutionCollectorWithoutMemory(unittest.TestCase):
	def setUp(self):
		self.table = MockObject()
		self.collector = SolutionCollectorWithoutMemory(self.table)
		self.puzzle = MockObject()
		self.puzzle.compare = MagicMock(name="compare", return_value=0)

	def test_construct(self):
		self.assertFalse(self.collector.done())

	def test_recordPuzzleSameAsPuzzle(self):
		self.puzzle.compare = MagicMock(name="compare", return_value=0)

		self.collector.record(self.puzzle)

		self.puzzle.compare.assert_called_once_with(self.table)
		self.assertFalse(self.collector.done())


	def test_recordPuzzleDifferentFromTable(self):
		self.puzzle.compare = MagicMock(name="compare", return_value=-1)
		self.collector.record(self.puzzle)

		self.puzzle.compare.assert_called_once_with(self.table)
		self.assertTrue(self.collector.done())		

	def test_getResultOutOfCollectorPuzzleDifferentFromTable(self):
		self.puzzle.compare = MagicMock(name="compare", return_value=-1)
		self.puzzle.differences = MagicMock(name="differences", return_value=(3, 0))
		self.collector.record(self.puzzle)

		result = self.collector.result()

		self.puzzle.differences.assert_called_once_with(self.table)
		self.assertEquals(2, result.solutionCount())
		self.assertEquals((3, 0), result.solutionDifference())

	def test_getResultOutOfCollectorPuzzleSameAsTable(self):
		self.puzzle.compare = MagicMock(name="compare", return_value=0)
		self.collector.record(self.puzzle)

		result = self.collector.result()

		self.assertEquals(1, result.solutionCount())

	def test_solutionCollectorIterationIfNoResultCollectedReturnSelf(self):
		collector = self.collector.next()
		self.assertEquals(self.collector, collector)

	def test_solutionCollectorIterationIfNoResultCollectedReturnCollectorWithMemory(self):
		self.collector.record(self.puzzle)
		self.collector.createCollectorWithMemory = MagicMock(return_value="collector_with_memory")
		collector = self.collector.next()
		self.assertEquals("collector_with_memory", collector)
		self.collector.createCollectorWithMemory.assert_called_once_with(self.table, self.puzzle)

	def test_impTohaveSolutionIsAlwaysFalse(self):
		self.assertFalse(self.collector.impossibleTohaveSolution(self.puzzle))

	pass

class TestSolutionCollectorWithMemory(unittest.TestCase):
	def setUp(self):
		self.table = MockObject()
		self.lastSolution = MockObject()
		self.testedPuzzle = MockObject()
		self.recordedPuzzle = MockObject()

		self.collector = SolutionCollectorWithMemory(self.table, self.lastSolution)

	def test_stopSearchIsFalseIfTestedPuzzleIsGreaterThanLastSolution(self):
		self.testedPuzzle.compare = MagicMock(return_value=1)
		stopSearch = self.collector.impossibleTohaveSolution(self.testedPuzzle)
		self.assertFalse(stopSearch)
		self.testedPuzzle.compare.assert_called_once_with(self.lastSolution)

	def test_stopSearchIsTrueIfTestedPuzzleIsNotGreaterThanLastSolution(self):
		self.testedPuzzle.compare = MagicMock(return_value=-1)
		stopSearch = self.collector.impossibleTohaveSolution(self.testedPuzzle)
		self.assertTrue(stopSearch)
		self.testedPuzzle.compare.assert_called_once_with(self.lastSolution)

	def test_stopSearchIsFalseEverSinceFirstBecomeFalse(self):
		self.recordedPuzzle.compare = MagicMock(return_value = 1)
		self.testedPuzzle.compare = MagicMock()
		self.collector.record(self.recordedPuzzle)
		stopSearch = self.collector.impossibleTohaveSolution(self.testedPuzzle)
		self.assertFalse(stopSearch)
		self.assertEquals(0, self.testedPuzzle.compare.call_count)
