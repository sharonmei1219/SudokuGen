import unittest
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import ANY
from src.puzzle import *
from src.puzzle import _
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
		self.puzzle = Puzzle(PuzzleMatrix(self.matrix), self.grid, self.validator, self.candidates)
		pass
	
	def test_puzzleIsSolvedIfMatrixIsFullAndValidationPassed(self):
		self.puzzle.full = MagicMock(return_value=True)
		self.validator.validate = MagicMock(return_value=True)

		self.assertTrue(self.puzzle.solved())

		self.validator.validate.assert_called_once_with(self.grid, ANY)
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
		self.candidates.getCandidatesAt.assert_called_once_with(self.grid, (0,0), ANY)
		pass

	def test_compare(self):
		puzzle_1 = Puzzle(PuzzleMatrix([[1, 1], [1, 1]]), self.grid, self.validator, self.candidates)
		puzzle_2 = Puzzle(PuzzleMatrix([[1, 1], [1, 2]]), self.grid, self.validator, self.candidates)
		self.assertEquals(-1, puzzle_1.compare(puzzle_2))

		puzzle_1 = Puzzle(PuzzleMatrix([[1, 1], [_, 1]]), self.grid, self.validator, self.candidates)
		puzzle_2 = Puzzle(PuzzleMatrix([[1, 1], [1, 2]]), self.grid, self.validator, self.candidates)
		self.assertEquals(1, puzzle_1.compare(puzzle_2))

		puzzle_1 = Puzzle(PuzzleMatrix([[1, 1], [_, 1]]), self.grid, self.validator, self.candidates)
		puzzle_2 = Puzzle(PuzzleMatrix([[1, 2], [1, 2]]), self.grid, self.validator, self.candidates)
		self.assertEquals(-1, puzzle_1.compare(puzzle_2))

		puzzle_1 = Puzzle(PuzzleMatrix([[1, 2], [2, 1]]), self.grid, self.validator, self.candidates)
		puzzle_2 = Puzzle(PuzzleMatrix([[1, 2], [2, 1]]), self.grid, self.validator, self.candidates)
		self.assertEquals(0, puzzle_1.compare(puzzle_2))	

	def test_GridIsNotFullWhenThereIsEmptyCell(self):
		puzzle_1 = Puzzle(PuzzleMatrix([[1, 1], [_, 1]],), self.grid, self.validator, self.candidates)		
		self.assertFalse(puzzle_1.full())

	def test_GridIsFull(self):
		puzzle_1 = Puzzle(PuzzleMatrix([[1, 2], [2, 1]]), self.grid, self.validator, self.candidates)
		self.assertTrue(puzzle_1.full())

class TestValidator(unittest.TestCase):
	def setUp(self):
		self.validator = Validator()
		self.grid = MockObject()
		self.matrix = MockObject()

	def test_duplicationDetection(self):
		self.assertTrue(self.validator.detectDuplication([1, 1, 2]))
		self.assertFalse(self.validator.detectDuplication([1, 2]))
		self.assertFalse(self.validator.detectDuplication([]))

	def test_gridNotValideIfDuplicationExistInARow(self):
		self.matrix = [[1, 1], [2, 3]]
		self.grid = Grid(2, 2, 1, 1)
		self.puzzleMatrix = PuzzleMatrix(self.matrix)
		self.assertFalse(self.validator.validate(self.grid, self.puzzleMatrix))

	def test_gridNotValidIfDuplicationExistInColumn(self):
		self.matrix = [[1, 2], [1, 3]]
		self.grid = Grid(2, 2, 1, 1)
		self.puzzleMatrix = PuzzleMatrix(self.matrix)
		self.assertFalse(self.validator.validate(self.grid, self.puzzleMatrix))

	def test_gridNotValidIfDuplicationExistInBlock(self):
		self.matrix = [[1, 2, 3, 4], [2, 1, 4, 3], [3, 4, 1, 2], [4, 3, 2, 1]]
		self.grid = Grid(4, 4, 2, 2)
		self.puzzleMatrix = PuzzleMatrix(self.matrix)
		self.assertFalse(self.validator.validate(self.grid, self.puzzleMatrix))

	def test_gridValidIfThereIsNoDuplicationExistInAnyZone(self):
		self.matrix = [[1, 2, 3, 4], [3, 4, 1, 2], [2, 1, 4, 3], [4, 3, 2, 1]]
		self.grid = Grid(4, 4, 2, 2)
		self.puzzleMatrix = PuzzleMatrix(self.matrix)
		self.assertTrue(self.validator.validate(self.grid, self.puzzleMatrix))


class TestCandidates(unittest.TestCase):
	def setUp(self):
		self.candidatesGen = CandidatesGen([1, 2, 3, 4])
		self.grid = MockObject()
		self.matrix = MockObject()
		self.puzzleMatrix = MockObject()

	def test_candidatesAt00Is4WhenSuroundingsAre123(self):
		self.grid.suroundings = MagicMock(return_value=[1, 2, 3])
		self.assertEquals([4], self.candidatesGen.getCandidatesAt(self.grid, (0, 0), self.puzzleMatrix))
		self.grid.suroundings.assert_called_once_with((0, 0), self.puzzleMatrix)

	def test_candidatesAt00IsEmptyListWhenSuroundingsAre1234(self):
		self.grid.suroundings = MagicMock(return_value=[1, 2, 3, 4])
		self.assertEquals([], self.candidatesGen.getCandidatesAt(self.grid, (0, 0), self.puzzleMatrix))
		self.grid.suroundings.assert_called_once_with((0, 0), self.puzzleMatrix)

	def test_candidatesAt00Is1234WhenSuroundingsAreEmpty(self):
		self.grid.suroundings = MagicMock(return_value=[])
		self.assertEquals([1, 2, 3, 4], self.candidatesGen.getCandidatesAt(self.grid, (0, 1), self.puzzleMatrix))
		self.grid.suroundings.assert_called_once_with((0, 1), self.puzzleMatrix)

class TestCandidatesInRandomSeq(unittest.TestCase):
	def setUp(self):
		candidatesGen = MockObject()
		candidatesGen.getCandidatesAt = MagicMock(return_value=[1, 2, 3])
		self.randomSeqCandidatesGen = RandomSeqCandidatesDecorator(candidatesGen)
		self.randint = random.randint
		self.grid = MockObject()
		self.matrix = MockObject()
		self.puzzleMatrix = MockObject()

	def tearDown(self):
		random.randint = self.randint

	def test_RandomSeqCandidatesGen(self):
		random.randint = MagicMock(side_effect=[0, 0, 0])
		self.assertEquals([1, 2, 3], self.randomSeqCandidatesGen.getCandidatesAt(self.grid, (0, 0), self.puzzleMatrix))
		self.assertEquals([call(0, 2), call(0, 1), call(0, 0)], random.randint.mock_calls)

	def test_RandomSeqCandidatesGenReversedSeq(self):
		random.randint = MagicMock(side_effect=[2, 1, 0])
		self.assertEquals([3, 2, 1], self.randomSeqCandidatesGen.getCandidatesAt(self.grid, (0, 0), self.puzzleMatrix))

	def test_RandomSeqCandidatesGenReversedSeq(self):
		random.randint = MagicMock(side_effect=[1, 1, 0])
		self.assertEquals([2, 3, 1], self.randomSeqCandidatesGen.getCandidatesAt(self.grid, (0, 0), self.puzzleMatrix))

class TestGrid(unittest.TestCase):
	def setUp(self):
		self.grid = Grid(2, 2, 1, 1)
		self.gridRow = GridRow(2, 2)

	def test_GridGetAllRowsInPos(self):
		self.assertEquals([[(0, 0), (0, 1)], [(1, 0), (1, 1)]], self.gridRow.zones())

	def test_GridGetAllColumnsInPos(self):
		self.assertEquals([[(0, 0), (1, 0)], [(0, 1), (1, 1)]], self.grid.gridColumn.zones())

	def test_allPos(self):
		self.assertEquals([(0, 0), (0, 1), (1, 0), (1, 1)], self.grid.allPos())
		pass


class TestBlockInGrid(unittest.TestCase):
	def setUp(self):
		self.matrix = [[1, 1, 2, 2],
			 	       [1, 1, _, _],
			      	   [_, _, 2, 2],
			           [_, 3, _, 4],
			           [3, _, 4, _],
			           [3, 3, 4, 4]];

		self.grid = Grid(6, 4, 3, 2)

	def test_emptyCellSuroundingAt21(self):
		matrix = [[1, 2, _, _],
 	              [3, 4, _, _],
      	          [5, _, _, 6],
           		  [_, 7, _, _],
                  [_, _, _, _],
                  [_, _, _, _]];
		puzzleMatrix = PuzzleMatrix(matrix)

		grid =  Grid(6, 4, 3, 2)
		self.assertEquals(set([1, 2, 3, 4, 5, 6, 7]), grid.suroundings((2, 1), puzzleMatrix))

class TestBlockIndexExchange(unittest.TestCase):
	def setUp(self):
		self.referenceMatrix = [[ 0,  1, 10, 11],
						   		[ 2,  3, 12, 13],
						   		[ 4,  5, 14, 15],
						   		[20, 21, 30, 31],
						  		[22, 23, 32, 33],
						   		[24, 25, 34, 35]]
		self.grid =  GridBlock(6, 4, 3, 2)
		pass
		
	def test_blockIndexToMatrixIndex(self):
		self.assertEquals((4, 2), self.grid.blockIndexToMatrixIndex(3, 2))
		self.assertEquals((2, 1), self.grid.blockIndexToMatrixIndex(0, 5))
		self.assertEquals((1, 3), self.grid.blockIndexToMatrixIndex(1, 3))
		pass

	def test_matrixIndexToBlockIndex(self):
		self.assertEquals((3, 0), self.grid.blockIndexMap[3][2])
		self.assertEquals((3, 5), self.grid.blockIndexMap[5][3])
		self.assertEquals((2, 1), self.grid.blockIndexMap[3][1])		
		pass

	def test_coordsOfRow(self):
		grid = GridRow(6, 4)
		self.assertEquals([(0, 0), (0, 1), (0, 2), (0, 3)], grid.zoneWithPosIn((0, 1)))

	def test_coordsOfColumn(self):
		grid = GridColumn(6, 4)
		self.assertEquals([(0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1)], grid.zoneWithPosIn((0, 1)))

	def test_coordsOfBlock(self):
		self.assertEquals([(3, 2), (3, 3), (4, 2), (4, 3), (5, 2), (5, 3)], self.grid.zoneWithPosIn((4, 2)))

	def test_GridGetAllBlocksInPos(self):
		self.assertEquals([[(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)],
			               [(0, 2), (0, 3), (1, 2), (1, 3), (2, 2), (2, 3)],
			               [(3, 0), (3, 1), (4, 0), (4, 1), (5, 0), (5, 1)],
			               [(3, 2), (3, 3), (4, 2), (4, 3), (5, 2), (5, 3)]], self.grid.zones())		
		pass

class TestPuzzleIntegrate(unittest.TestCase):
	def test_integratePuzzle(self):
		matrix = [[1, 8, 8, 8],
	 	          [2, 8, 8, 8],
	              [8, _, 3, 4],
	    		  [8, 8, 8, 8],
	              [8, 5, 8, 8],
	              [8, 6, 8, 8]]
		grid = Grid(6, 4, 3, 2)
		candidatesGen = CandidatesGen([1, 2, 3, 4, 5, 6, 7])
		validator = Validator()
		puzzle = Puzzle(PuzzleMatrix(matrix), grid, validator, candidatesGen)
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
		puzzle = self.factory.creatPuzzleByMatrix([[1, _], [_, 4]])
		
		self.assertEquals((0, 1), puzzle.firstEmptyCell())
		self.assertEquals((1, 0), puzzle.firstEmptyCell())

	def test_puzzleChange(self):
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
		puzzle_1 = self.newPuzzle([[1, 1], [1, 1]])
		puzzle_2 = self.newPuzzle([[1, 1], [1, 2]])
		self.assertEquals(-1, puzzle_1.compare(puzzle_2))
		pass

	def newPuzzle(self, matrix):
		return self.factory.creatPuzzleByMatrix(matrix)
		pass

class TestViewDirection(unittest.TestCase):
	def testGetRowWithPosIn(self):
		view = GridRow(2, 2)
		zone = view.zoneWithPosIn((0, 0))
		self.assertEquals([(0, 0), (0, 1)], zone)
		pass

	def testGetColumnWithPosIn(self):
		view = GridColumn(2, 2)
		zone = view.zoneWithPosIn((0, 0))
		self.assertEquals([(0, 0), (1, 0)], zone)
		pass

	def testGetBlockWithPosIn(self):
		view = GridBlock(4, 4, 2, 2)
		zone = view.zoneWithPosIn((0, 0))
		self.assertEquals([(0, 0), (0, 1), (1, 0), (1, 1)], zone)
		pass


class TestViewDirectionPosesInSameZone(unittest.TestCase):
	def testPosesInSameBlock(self):
		view = GridBlock(4, 4, 2, 2)
		poses = {(0, 0), (0, 1)}
		self.assertTrue(view.posesInSameZone(poses))
		pass
	pass

class TestViewDirectionSplitPosesInDifferentZone(unittest.TestCase):
	def testSplitOnePosInOneZone(self):
		view = GridRow(2, 2)
		poses = [(0, 0)]
		self.assertEquals([{(0, 0)}], view.split(poses))
		pass

	def testSplitPosesInDifferentZone(self):
		view = GridRow(2, 2)
		poses = [(0, 0), (1, 0), (1, 1)]
		self.assertEquals([{(0, 0)}, {(1, 0), (1, 1)}], view.split(poses))
		pass

class TestPuzzleKnownAndUnKnownPart(unittest.TestCase):
	def testKnownPartOfPuzzle(self):
		puzzle = Puzzle(PuzzleMatrix([[1, _],
									  [_, _]]), 
						Grid(2, 2, 1, 1),
						Validator(),
						CandidatesGen([1, 2]))
		myMap = {(0, 0):1}
		self.assertEquals(myMap, puzzle.knownPart())
		pass

	def testUnknownPartOfPuzzle(self):
		puzzle = Puzzle(PuzzleMatrix([[1, 2],
									  [_, _]]), 
						Grid(2, 2, 1, 1),
						Validator(),
						CandidatesGen([1, 2, 3]))
		myMap = {(1, 0): {2, 3}, (1, 1):{1, 3}}
		self.assertEquals(myMap, puzzle.unknownPart())		
		pass
	pass

class testPuzzlePermutation(unittest.TestCase):

	def testOneListInABlock(self):
		permutator = PuzzlePermutator(1, 2, 1, 1)
		row = permutator.permGroupsAndPermItemWithinGroup([1, 0], [[0],[0]])
		self.assertEquals([1, 0], row)
		pass

	def testTwoListNoTwistInABlock(self):
		permutator = PuzzlePermutator(1, 2, 1, 1)
		row = permutator.permGroupsAndPermItemWithinGroup([1, 0], [[0, 1],[0, 1]])
		self.assertEquals([2, 3, 0, 1], row)
		pass

	def testTwoListTwistInABlock(self):
		permutator = PuzzlePermutator(1, 2, 1, 1)
		row = permutator.permGroupsAndPermItemWithinGroup([1, 0], [[1, 0],[0, 1]])
		self.assertEquals([3, 2, 0, 1], row)
		pass

	def testRandomPerOfListSizeOf1(self):
		permutator = PuzzlePermutator(1, 2, 1, 1)
		perm = permutator.genPerm(1, 0)
		self.assertEquals([0], perm)
		pass

	def testRandomPerOfListSizeOf3(self):
		permutator = PuzzlePermutator(1, 3, 1, 1)
		self.assertEquals([0, 1, 2], permutator.genPerm(3, 0))
		self.assertEquals([0, 2, 1], permutator.genPerm(3, 1))
		self.assertEquals([1, 0, 2], permutator.genPerm(3, 2))				
		self.assertEquals([1, 2, 0], permutator.genPerm(3, 3))
		self.assertEquals([2, 0, 1], permutator.genPerm(3, 4))
		self.assertEquals([2, 1, 0], permutator.genPerm(3, 5))
		pass

	def testRandomlyPermRow(self):
		permutator = PuzzlePermutator(6, 1, 2, 1)
		self.randint = random.randint
		random.randint = MagicMock(side_effect=[5, 1, 0, 0])
		rowPerm = permutator.randomRowPerm()
		self.assertEquals([5, 4, 2, 3, 0, 1], rowPerm)
		random.randint = self.randint
		pass

	def testRandomlyPerColumn(self):
		permutator = PuzzlePermutator(1, 6, 1, 3)
		self.randint = random.randint
		random.randint = MagicMock(side_effect=[1, 5, 0])
		rowPerm = permutator.randomColumnPerm()
		self.assertEquals([5, 4, 3, 0, 1, 2], rowPerm)
		random.randint = self.randint
		pass
	pass
		