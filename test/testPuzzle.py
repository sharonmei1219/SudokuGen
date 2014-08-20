import unittest
from unittest.mock import MagicMock
from src.puzzle import *

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

class TestGrid(unittest.TestCase):
	def test_GridGetAllRows(self):
		_ = Grid.EmptySign
		OneOneGrid = type('OneOneGrid', (Grid, ), {'bw':1, 'bh':1})
		self.grid = OneOneGrid([[1, _], [3, 4]])
		self.assertEquals([[1], [3, 4]], self.grid.allRows())

	def test_GridGetAllColumns(self):
		_ = Grid.EmptySign
		OneOneGrid = type('OneOneGrid', (Grid, ), {'bw':1, 'bh':1})
		self.grid = OneOneGrid([[1, _], [3, 4]])
		self.assertEquals([[1, 3], [4]], self.grid.allColumns())
