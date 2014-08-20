import unittest
from unittest.mock import MagicMock
from src.puzzle import Puzzle
from src.puzzle import Validator

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
	def test_duplicationDetection(self):
		self.validator = Validator()
		self.assertTrue(self.validator.detectDuplication([1, 1, 2]))
		self.assertFalse(self.validator.detectDuplication([1, 2]))
		self.assertFalse(self.validator.detectDuplication([]))
		pass

	pass
