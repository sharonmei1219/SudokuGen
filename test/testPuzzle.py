import unittest
from unittest.mock import MagicMock
from unittest.mock import call
from src.puzzle import *
import random

class MockGrid:
	pass

class MockValidator:
	pass

class MockCandidates:
	pass

class TestPuzzle(unittest.TestCase):
	def  setUp(self):
		self.grid = MockGrid()
		self.validator = MockValidator()
		self.candidates = MockCandidates()
		self.grid.full = MagicMock(return_value=True)
		self.validator.validate = MagicMock(return_value=True)
		self.puzzle = Puzzle(self.grid, self.validator, self.candidates)
		pass
	
	def test_puzzleIsSolvedIfMatrixIsFullAndValidationPassed(self):
		self.grid.full = MagicMock(return_value=True)
		self.validator.validate = MagicMock(return_value=True)

		self.assertTrue(self.puzzle.solved())

		self.grid.full.assert_called_once_with()
		self.validator.validate.assert_called_once_with(self.grid)
		pass

	def test_puzzleIsNotSolvedIfGridIsNotFull(self):
		self.grid.full = MagicMock(return_value=False)
		self.assertFalse(self.puzzle.solved())
		pass

	def test_puzzleIsNotSolvedIfGridIsNotValid(self):
		self.validator.validate = MagicMock(return_value=False)
		self.assertFalse(self.puzzle.solved())
		pass

	def test_puzzleCandidates(self):
		self.candidates.getCandidates = MagicMock(return_value=[1, 2])
		self.assertEquals([1, 2], self.puzzle.candidates())
		self.candidates.getCandidates.assert_called_once_with(self.grid)

	def test_puzzleFillWithNumber(self):
		newGrid = MockGrid()
		self.grid.fill = MagicMock(return_value=newGrid)
		newPuzzle = self.puzzle.fill(1)
		self.assertEquals(newGrid, newPuzzle.grid)
		self.grid.fill.assert_called_once_with(1)

class TestValidator(unittest.TestCase):
	def setUp(self):
		self.validator = Validator()
		self.grid = MockGrid()
		self.grid.allRows = MagicMock(return_value=[[1, 2],[3, 4]])
		self.grid.allColumns = MagicMock(return_value=[[1, 2],[3, 4]])
		self.grid.allBlocks = MagicMock(return_value=[[1, 2],[3, 4]])

	def test_duplicationDetection(self):
		self.assertTrue(self.validator.detectDuplication([1, 1, 2]))
		self.assertFalse(self.validator.detectDuplication([1, 2]))
		self.assertFalse(self.validator.detectDuplication([]))

	def test_gridNotValideIfDuplicationExistInARow(self):
		self.grid.allRows = MagicMock(return_value=[[1, 2],[3, 3]])
		self.assertFalse(self.validator.validate(self.grid))
		self.grid.allRows.assert_called_once_with()


	def test_gridNotValidIfDuplicationExistInColumn(self):
		self.grid.allColumns = MagicMock(return_value=[[1, 2],[3, 3]])
		self.assertFalse(self.validator.validate(self.grid))

	def test_gridNotValidIfDuplicationExistInBlock(self):
		self.grid.allBlocks = MagicMock(return_value=[[1, 2],[3, 3]])
		self.assertFalse(self.validator.validate(self.grid))

	def test_gridValidIfThereIsNoDuplicationExistInAnyZone(self):
		self.assertTrue(self.validator.validate(self.grid))


class TestCandidates(unittest.TestCase):
	def setUp(self):
		self.candidatesGen = CandidatesGen([1, 2, 3, 4])
		self.grid = MockGrid()

	def test_candidatesIs4WhenSuroundingsAre123(self):
		self.grid.emptyCellSurounding = MagicMock(return_value=[1, 2, 3])
		self.assertEquals([4], self.candidatesGen.getCandidates(self.grid))

	def test_candidatesIsEmptyListWhenSuroundingsAre1234(self):
		self.grid.emptyCellSurounding = MagicMock(return_value=[1, 2, 3, 4])
		self.assertEquals([], self.candidatesGen.getCandidates(self.grid))

	def test_candidatesIs1234WhenSuroundingsAreEmpty(self):
		self.grid.emptyCellSurounding = MagicMock(return_value=[])
		self.assertEquals([1, 2, 3, 4], self.candidatesGen.getCandidates(self.grid))

class TestCandidatesInRandomSeq(unittest.TestCase):
	def setUp(self):
		candidatesGen = MockCandidates()
		candidatesGen.getCandidates = MagicMock(return_value=[1, 2, 3])
		self.randomSeqCandidatesGen = RandomSeqCandidatesDecorator(candidatesGen)
		self.randint = random.randint
		self.grid = MockGrid()

	def tearDown(self):
		random.randint = self.randint

	def test_RandomSeqCandidatesGen(self):
		random.randint = MagicMock(side_effect=[0, 0, 0])
		self.assertEquals([1, 2, 3], self.randomSeqCandidatesGen.getCandidates(self.grid))
		self.assertEquals([call(0, 2), call(0, 1), call(0, 0)], random.randint.mock_calls)

	def test_RandomSeqCandidatesGenReversedSeq(self):
		random.randint = MagicMock(side_effect=[2, 1, 0])
		self.assertEquals([3, 2, 1], self.randomSeqCandidatesGen.getCandidates(self.grid))

	def test_RandomSeqCandidatesGenReversedSeq(self):
		random.randint = MagicMock(side_effect=[1, 1, 0])
		self.assertEquals([2, 3, 1], self.randomSeqCandidatesGen.getCandidates(self.grid))


class TestGrid(unittest.TestCase):
	def setUp(self):
		self.OneOneGrid = type('OneOneGrid', (Grid, ), {'bw':1, 'bh':1})
		_ = Grid.EmptySign
		self.grid = self.OneOneGrid([[1, _], [3, 4]])

	def test_GridGetAllRows(self):
		self.assertEquals([[1], [3, 4]], self.grid.allRows())

	def test_GridGetAllColumns(self):
		self.assertEquals([[1, 3], [4]], self.grid.allColumns())

	def test_GridIsNotFullWhenThereIsEmptyCell(self):
		self.assertFalse(self.grid.full())

	def test_GridIsFull(self):
		self.grid = self.OneOneGrid([[1, 2], [3, 4]])
		self.assertTrue(self.grid.full())

	def test_fillInAFullGrid(self):
		grid = self.OneOneGrid([[1, 2], [3, 4]])
		newGrid = grid.fill(6)
		self.assertEquals([[1, 2], [3, 4]], newGrid.allRows())


class TestBlockInGrid(unittest.TestCase):
	def setUp(self):
		_ = Grid.EmptySign
		self.TwoThreeGrid = type('TwoThreeGrid', (Grid, ), {'bw':2, 'bh':3})
		self.grid = self.TwoThreeGrid([[1, 1, 2, 2],
			 	                  [1, 1, _, _],
			      	              [_, _, 2, 2],
			           		      [_, 3, _, 4],
			                	  [3, _, 4, _],
			                 	  [3, 3, 4, 4]])

	def test_GridGetBlock(self):
		self.assertEquals([1, 1, 1, 1], self.grid.block(2, 1))
		self.assertEquals([2, 2, 2, 2], self.grid.block(2, 2))
		self.assertEquals([3, 3, 3, 3], self.grid.block(5, 0))
		self.assertEquals([4, 4, 4, 4], self.grid.block(3, 2))

	def test_GridGetAllBlocks(self):
		self.assertEquals([[1, 1, 1, 1],[2, 2, 2, 2],[3, 3, 3, 3],[4, 4, 4, 4]], self.grid.allBlocks())

	def test_GridFill(self):
		newGrid = self.grid.fill(2)
		self.assertEquals([2, 2, 2, 2], self.grid.block(2, 2))
		self.assertEquals([2, 2, 2, 2, 2], newGrid.block(2, 2))
		self.assertEquals([1, 1, 2], newGrid.allRows()[1])
		newGrid = newGrid.fill(3)
		self.assertEquals([1, 1, 2, 3], newGrid.allRows()[1])

	def test_emptyCellSurounding(self):
		_ = Grid.EmptySign
		grid = self.TwoThreeGrid([[1, 2, 0, 0],
			 	                  [3, 4, 0, 0],
			      	              [5, _, _, 6],
			           		      [_, 7, _, _],
			                	  [_, _, _, _],
			                 	  [_, _, _, _]])
		self.assertEquals(set([1, 2, 3, 4, 5, 6, 7]), grid.emptyCellSurounding())

class TestPuzzleIntegrate(unittest.TestCase):
	def test_integratePuzzle(self):
		_ = Grid.EmptySign
		TwoThreeGrid = type('TwoThreeGrid', (Grid, ), {'bw':2, 'bh':3})
		grid = TwoThreeGrid([[1, 0, 0, 0],
			 	             [2, 0, 0, 0],
			                 [0, _, 3, 4],
			    		     [0, 0, 0, 0],
			                 [0, 5, 0, 0],
			                 [0, 6, 0, 0]])
		candidatesGen = CandidatesGen([1, 2, 3, 4, 5, 6, 7])
		validator = Validator()
		puzzle = Puzzle(grid, validator, candidatesGen)
		self.assertFalse(puzzle.solved())
		self.assertEquals([7], puzzle.candidates())