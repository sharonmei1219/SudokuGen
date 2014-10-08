import unittest
from unittest.mock import MagicMock
from unittest.mock import call
from src.puzzle import *
import random

class MockObject:
	pass

class TestPuzzle(unittest.TestCase):
	def  setUp(self):
		self.matrix = [[]]
		self.grid = MockObject()
		self.validator = MockObject()
		self.candidates = MockObject()
		self.grid.full = MagicMock(return_value=True)
		self.validator.validate = MagicMock(return_value=True)
		self.puzzle = Puzzle(self.matrix, self.grid, self.validator, self.candidates)
		pass
	
	def test_puzzleIsSolvedIfMatrixIsFullAndValidationPassed(self):
		self.puzzle.full = MagicMock(return_value=True)
		self.validator.validate = MagicMock(return_value=True)

		self.assertTrue(self.puzzle.solved())

		self.validator.validate.assert_called_once_with(self.grid, self.matrix)
		pass

	def test_puzzleIsNotSolvedIfGridIsNotFull(self):
		self.puzzle.full = MagicMock(return_value=False)
		self.assertFalse(self.puzzle.solved())
		pass

	def test_puzzleIsNotSolvedIfGridIsNotValid(self):
		self.validator.validate = MagicMock(return_value=False)
		self.assertFalse(self.puzzle.solved())
		pass

	def test_puzzleCandidatesAt(self):
		self.candidates.getCandidatesAt = MagicMock(return_value=[1, 2])
		self.assertEquals([1, 2], self.puzzle.candidatesAt((0,0)))
		self.candidates.getCandidatesAt.assert_called_once_with(self.grid, (0,0), self.matrix)
		pass

	def test_compare(self):
		_ = Puzzle.EmptySign
		puzzle_1 = Puzzle([[1, 1], [1, 1]], self.grid, self.validator, self.candidates)
		puzzle_2 = Puzzle([[1, 1], [1, 2]], self.grid, self.validator, self.candidates)
		self.assertEquals(-1, puzzle_1.compare(puzzle_2))

		puzzle_1 = Puzzle([[1, 1], [_, 1]], self.grid, self.validator, self.candidates)
		puzzle_2 = Puzzle([[1, 1], [1, 2]], self.grid, self.validator, self.candidates)
		self.assertEquals(1, puzzle_1.compare(puzzle_2))

		puzzle_1 = Puzzle([[1, 1], [_, 1]], self.grid, self.validator, self.candidates)
		puzzle_2 = Puzzle([[1, 2], [1, 2]], self.grid, self.validator, self.candidates)
		self.assertEquals(-1, puzzle_1.compare(puzzle_2))

		puzzle_1 = Puzzle([[1, 2], [2, 1]], self.grid, self.validator, self.candidates)
		puzzle_2 = Puzzle([[1, 2], [2, 1]], self.grid, self.validator, self.candidates)
		self.assertEquals(0, puzzle_1.compare(puzzle_2))	

	def test_GridIsNotFullWhenThereIsEmptyCell(self):
		_ = Puzzle.EmptySign		
		puzzle_1 = Puzzle([[1, 1], [_, 1]], self.grid, self.validator, self.candidates)		
		self.assertFalse(puzzle_1.full())

	def test_GridIsFull(self):
		puzzle_1 = Puzzle([[1, 2], [2, 1]], self.grid, self.validator, self.candidates)
		self.assertTrue(puzzle_1.full())

class TestValidator(unittest.TestCase):
	def setUp(self):
		self.validator = Validator()
		self.grid = MockObject()
		self.matrix = MockObject()
		self.grid.allRows = MagicMock(return_value=[[1, 2],[3, 4]])
		self.grid.allColumns = MagicMock(return_value=[[1, 2],[3, 4]])
		self.grid.allBlocks = MagicMock(return_value=[[1, 2],[3, 4]])

	def test_duplicationDetection(self):
		self.assertTrue(self.validator.detectDuplication([1, 1, 2]))
		self.assertFalse(self.validator.detectDuplication([1, 2]))
		self.assertFalse(self.validator.detectDuplication([]))

	def test_gridNotValideIfDuplicationExistInARow(self):
		self.grid.allRows = MagicMock(return_value=[[1, 2],[3, 3]])
		self.assertFalse(self.validator.validate(self.grid, self.matrix))
		self.grid.allRows.assert_called_once_with(self.matrix)


	def test_gridNotValidIfDuplicationExistInColumn(self):
		self.grid.allColumns = MagicMock(return_value=[[1, 2],[3, 3]])
		self.assertFalse(self.validator.validate(self.grid, self.matrix))

	def test_gridNotValidIfDuplicationExistInBlock(self):
		self.grid.allBlocks = MagicMock(return_value=[[1, 2],[3, 3]])
		self.assertFalse(self.validator.validate(self.grid, self.matrix))

	def test_gridValidIfThereIsNoDuplicationExistInAnyZone(self):
		self.assertTrue(self.validator.validate(self.grid, self.matrix))


class TestCandidates(unittest.TestCase):
	def setUp(self):
		self.candidatesGen = CandidatesGen([1, 2, 3, 4])
		self.grid = MockObject()
		self.matrix = MockObject()

	def test_candidatesAt00Is4WhenSuroundingsAre123(self):
		self.grid.suroundings = MagicMock(return_value=[1, 2, 3])
		self.assertEquals([4], self.candidatesGen.getCandidatesAt(self.grid, (0, 0), self.matrix))
		self.grid.suroundings.assert_called_once_with((0, 0), self.matrix)

	def test_candidatesAt00IsEmptyListWhenSuroundingsAre1234(self):
		self.grid.suroundings = MagicMock(return_value=[1, 2, 3, 4])
		self.assertEquals([], self.candidatesGen.getCandidatesAt(self.grid, (0, 0), self.matrix))
		self.grid.suroundings.assert_called_once_with((0, 0), self.matrix)

	def test_candidatesAt00Is1234WhenSuroundingsAreEmpty(self):
		self.grid.suroundings = MagicMock(return_value=[])
		self.assertEquals([1, 2, 3, 4], self.candidatesGen.getCandidatesAt(self.grid, (0, 1), self.matrix))
		self.grid.suroundings.assert_called_once_with((0, 1), self.matrix)

class TestCandidatesInRandomSeq(unittest.TestCase):
	def setUp(self):
		candidatesGen = MockObject()
		candidatesGen.getCandidatesAt = MagicMock(return_value=[1, 2, 3])
		self.randomSeqCandidatesGen = RandomSeqCandidatesDecorator(candidatesGen)
		self.randint = random.randint
		self.grid = MockObject()
		self.matrix = MockObject()

	def tearDown(self):
		random.randint = self.randint

	def test_RandomSeqCandidatesGen(self):
		random.randint = MagicMock(side_effect=[0, 0, 0])
		self.assertEquals([1, 2, 3], self.randomSeqCandidatesGen.getCandidatesAt(self.grid, (0, 0), self.matrix))
		self.assertEquals([call(0, 2), call(0, 1), call(0, 0)], random.randint.mock_calls)

	def test_RandomSeqCandidatesGenReversedSeq(self):
		random.randint = MagicMock(side_effect=[2, 1, 0])
		self.assertEquals([3, 2, 1], self.randomSeqCandidatesGen.getCandidatesAt(self.grid, (0, 0), self.matrix))

	def test_RandomSeqCandidatesGenReversedSeq(self):
		random.randint = MagicMock(side_effect=[1, 1, 0])
		self.assertEquals([2, 3, 1], self.randomSeqCandidatesGen.getCandidatesAt(self.grid, (0, 0), self.matrix))


_ = Grid.EmptySign
class TestGrid(unittest.TestCase):
	def setUp(self):
		self.grid = Grid([[1, _], [3, 4]], 1, 1)

	def test_GridGetAllRows(self):
		self.assertEquals([[1], [3, 4]], self.grid.allRows([[1, _], [3, 4]]))

	def test_GridGetAllColumns(self):
		self.assertEquals([[1, 3], [4]], self.grid.allColumns([[1, _], [3, 4]]))


class TestBlockInGrid(unittest.TestCase):
	def setUp(self):
		_ = Grid.EmptySign
		self.matrix = [[1, 1, 2, 2],
			 	          [1, 1, _, _],
			      	      [_, _, 2, 2],
			           	  [_, 3, _, 4],
			              [3, _, 4, _],
			              [3, 3, 4, 4]];

		self.grid = Grid([[1, 1, 2, 2],
			 	          [1, 1, _, _],
			      	      [_, _, 2, 2],
			           	  [_, 3, _, 4],
			              [3, _, 4, _],
			              [3, 3, 4, 4]], 2, 3)

	def test_GridGetBlock(self):
		self.assertEquals([1, 1, 1, 1], self.grid.block(2, 1, self.matrix))
		self.assertEquals([2, 2, 2, 2], self.grid.block(2, 2, self.matrix))
		self.assertEquals([3, 3, 3, 3], self.grid.block(5, 0, self.matrix))
		self.assertEquals([4, 4, 4, 4], self.grid.block(3, 2, self.matrix))

	def test_GridGetAllBlocks(self):
		self.assertEquals([[1, 1, 1, 1],[2, 2, 2, 2],[3, 3, 3, 3],[4, 4, 4, 4]], self.grid.allBlocks(self.matrix))

	def test_emptyCellSuroundingAt21(self):
		_ = Grid.EmptySign
		matrix = [[1, 2, _, _],
 	                  [3, 4, _, _],
      	              [5, _, _, 6],
           		      [_, 7, _, _],
                	  [_, _, _, _],
                 	  [_, _, _, _]];

		grid =  Grid(matrix, 2, 3)
		self.assertEquals(set([1, 2, 3, 4, 5, 6, 7]), grid.suroundings((2, 1), matrix))

class TestBlockIndexExchange(unittest.TestCase):
	def setUp(self):
		_ = Grid.EmptySign
		self.grid =  Grid([[ 0,  1, 10, 11],
						   [ 2,  3, 12, 13],
						   [ 4,  5, 14, 15],
						   [20, 21, 30, 31],
						   [22, 23, 32, 33],
						   [24, 25, 34, 35]], 2, 3)
		pass
		
	def test_blockIndexToMatrixIndex(self):
		self.assertEquals((4, 2), self.grid.blockIndexToMatrixIndex(3, 2))
		self.assertEquals((2, 1), self.grid.blockIndexToMatrixIndex(0, 5))
		self.assertEquals((1, 3), self.grid.blockIndexToMatrixIndex(1, 3))
		pass

	def test_matrixIndexToBlockIndex(self):
		self.assertEquals((3, 0), self.grid.matrixIndexToBlockIndex(3, 2))
		self.assertEquals((3, 5), self.grid.matrixIndexToBlockIndex(5, 3))
		self.assertEquals((2, 1), self.grid.matrixIndexToBlockIndex(3, 1))		
		pass

class TestPuzzleIntegrate(unittest.TestCase):
	def test_integratePuzzle(self):
		_ = Grid.EmptySign
		matrix = [[1, 8, 8, 8],
	 	          [2, 8, 8, 8],
	              [8, _, 3, 4],
	    		  [8, 8, 8, 8],
	              [8, 5, 8, 8],
	              [8, 6, 8, 8]]
		grid = Grid(matrix, 2, 3)
		candidatesGen = CandidatesGen([1, 2, 3, 4, 5, 6, 7])
		validator = Validator()
		puzzle = Puzzle(matrix, grid, validator, candidatesGen)
		self.assertFalse(puzzle.solved())
		self.assertEquals((2,1), puzzle.firstEmptyCell())
		self.assertEquals([7], puzzle.candidatesAt((2, 1)))

class TestPuzzleFactory(unittest.TestCase):
	def setUp(self):
		self.randint = random.randint
		self.factory = RandomPuzzleFactory(2, 1, 1)

	def tearDown(self):
		random.randint = self.randint

	def test_randomPosGenOnePos(self):
		random.randint = MagicMock(return_value=0)
		pos = self.factory.getRandomPos(1)
		random.randint.assert_called_once_with(0, 3)
		self.assertEquals([(0, 0)], pos)

	def test_randomPosGenTwoPos(self):
		random.randint = MagicMock(side_effect=[1, 2])
		pos = self.factory.getRandomPos(2)
		self.assertEquals([call(0, 3), call(0, 2)],random.randint.mock_calls)
		self.assertEquals([(0, 1), (1, 1)], pos)

	def test_createPuzzleFromTable(self):
		table = MockObject()
		table.getNumbersInPos = MagicMock(return_value=[1, 2])
		pos = [(0, 0), (1, 1)]
		puzzle = self.factory.createPuzzleFromTable(table, pos)
		self.assertEquals("[[1, \"/\"], [\"/\", 2]]", puzzle.toString())

	def test_puzzleGetNumbersInPos(self):
		table = self.factory.creatPuzzleByMatrix([[1, 2], [3, 4]])
		nums = table.getNumbersInPos([(0, 0), (1, 1)])
		self.assertEquals([1, 4], nums)


class TestPuzzleCompare(unittest.TestCase):
	def setUp(self):
		self.factory = PuzzleFactory(2, 1, 1)

	def test_puzzleDifferences(self):
		puzzle_1 = self.factory.creatPuzzleByMatrix([[1, 2], [3, 4]])
		puzzle_2 = self.factory.creatPuzzleByMatrix([[1, 2], [4, 4]])
		self.assertEquals((1, 0), puzzle_1.differences(puzzle_2))

	def test_puzzleFirstEmptyCell(self):
		_ = Grid.EmptySign
		puzzle = self.factory.creatPuzzleByMatrix([[1, _], [_, 4]])
		
		self.assertEquals((0, 1), puzzle.firstEmptyCell())
		self.assertEquals((1, 0), puzzle.firstEmptyCell())

	def test_puzzleChange(self):
		_ = Grid.EmptySign
		puzzle = self.factory.creatPuzzleByMatrix([[1, _], [_, 4]])
		puzzle.change((0, 1), 2)

		self.assertEquals("[[1, 2], [\"/\", 4]]" ,puzzle.toString())

	def test_puzzleClear(self):
		puzzle = self.factory.creatPuzzleByMatrix([[1, 2], [3, 4]])
		puzzle.clear((1, 0))
		self.assertEquals((1, 0), puzzle.firstEmptyCell())
		self.assertEquals("[[1, 2], [\"/\", 4]]", puzzle.toString())
	
	# 1 is least, 2 is greater, empty sign is the greatest
	# matrix[0][0] is highest pos, and matrix[m][n] is the lowest pos
	def test_compare(self):
		_ = Grid.EmptySign
		puzzle_1 = self.newPuzzle([[1, 1], [1, 1]])
		puzzle_2 = self.newPuzzle([[1, 1], [1, 2]])
		self.assertEquals(-1, puzzle_1.compare(puzzle_2))
		pass

	def newPuzzle(self, matrix):
		return self.factory.creatPuzzleByMatrix(matrix)
		pass