import unittest
from unittest.mock import MagicMock
from unittest.mock import call
from humanSolver import *
from puzzle import Grid

class MockObject:
	pass

class TestHumanSolver(unittest.TestCase):

	def setUp(self):
		self.tier_0_Strategy = MockObject()
		self.tier_0_Strategy.solve = MagicMock()
		self.tier_0_Strategy.rank = MagicMock(return_value = 0)

		self.tier_1_Strategy = MockObject()
		self.tier_1_Strategy.solve = MagicMock()
		self.tier_1_Strategy.rank = MagicMock(return_value = 1)

		self.puzzle = MockObject()
		self.pMatrix = MockObject()
		self.ranker = Ranker([self.tier_0_Strategy, self.tier_1_Strategy])
		self.ranker.createPossibilityMatrix = MagicMock(return_value = self.pMatrix)
		pass

	def test_HumanSolver_puzzleSolvedByTierOneStrategy(self):
		self.puzzle.solved = MagicMock(side_effect=[False, True])

		rank = self.ranker.rank(self.puzzle)

		self.ranker.createPossibilityMatrix.assert_called_once_with(self.puzzle)
		self.tier_0_Strategy.solve.assert_called_once_with(self.pMatrix, self.puzzle)
		self.tier_1_Strategy.solve.assert_called_once_with(self.pMatrix, self.puzzle)
		self.assertEquals([call(), call()], self.puzzle.solved.mock_calls)
		self.assertEquals(1, rank)


class TestTierZeroStrategy(unittest.TestCase):
	def setUp(self):
		self.stg = Tier_0_Strategy()
		self.puzzle = MockObject()
		self.pMatrix = MockObject()
		self.single_0 = MockObject()
		self.single_0.update = MagicMock()
		self.single_0.updatePuzzle = MagicMock()
		self.single_1 = MockObject()
		self.single_1.update = MagicMock()
		self.single_1.updatePuzzle = MagicMock()
		pass

	def test_NoSingleFound(self):
		self.pMatrix.findNewSingle = MagicMock(return_value = None)
		self.stg.solve(self.pMatrix, self.puzzle)
		self.pMatrix.findNewSingle.assert_called_once_with()
		pass

	def test_TwoSingleFound(self):
		self.pMatrix.findNewSingle = MagicMock(side_effect = [self.single_0, self.single_1, None])

		self.stg.solve(self.pMatrix, self.puzzle)

		self.assertEquals([call(), call(), call()], self.pMatrix.findNewSingle.mock_calls)
		self.single_0.update.assert_called_once_with(self.pMatrix)
		self.single_1.update.assert_called_once_with(self.pMatrix)
		self.single_0.updatePuzzle.assert_called_once_with(self.puzzle)
		self.single_1.updatePuzzle.assert_called_once_with(self.puzzle)
		pass


class TestPossibilityMatrixFindSingles(unittest.TestCase):
	def setUp(self):
		self.puzzle = MockObject()
		self.puzzle.change = MagicMock()
		pass

	def test_findNoSingle(self):
		self.pMatrix = PossibilityMatrix([[]], Grid(0, 0, 1, 1))
		self.assertEquals(None, self.pMatrix.findNewSingle())
		pass

	def test_findOneSingle(self):
		self.pMatrix = PossibilityMatrix([[{1}]], Grid(1, 1, 1, 1))
		single = self.pMatrix.findNewSingle()

		single.updatePuzzle(self.puzzle)
		self.puzzle.change.assert_called_once_with((0, 0), 1)
		pass

	def test_findSingleOnlyOnce(self):
		self.pMatrix = PossibilityMatrix([[{1}, {2}]], Grid(1, 2, 1, 1))
		single = self.pMatrix.findNewSingle()
		single.update(self.pMatrix)

		single = self.pMatrix.findNewSingle()
		single.updatePuzzle(self.puzzle)

		self.puzzle.change.assert_called_once_with((0, 1), 2)
		pass

	def test_updateRow(self):
		self.pMatrix = PossibilityMatrix([[{1}, {1, 2}]], Grid(1, 2, 1, 1))
		self.pMatrix.updateRow((0, 0), {1}, {(0, 0)})
		self.assertEquals([{1}, {2}], self.pMatrix.matrix[0])
		pass

	def test_updateColum(self):
		self.pMatrix = PossibilityMatrix([[{1}], [{1, 2}]], Grid(2, 1, 1, 1))
		self.pMatrix.updateColum((0, 0), {1}, {(0, 0)})
		self.assertEquals([[{1}],[{2}]], self.pMatrix.matrix)
		pass

	def test_updateBlock(self):
		self.pMatrix = PossibilityMatrix([[{1, 2}, {1, 2, 3}],
										  [{2, 4}, {1, 5}]], Grid(2, 2, 2, 2))
		self.pMatrix.updateBlock((0, 0), {1, 2}, {(0, 0)})
		self.assertEquals([[{1, 2}, {3}],[{4}, {5}]], self.pMatrix.matrix)		
		pass

	def test_nakedSingleUpdatePuzzleMatrix(self):
		single = Single((0, 0), 5)
		single.updatePuzzle(self.puzzle)
		self.puzzle.change.assert_called_once_with((0, 0), 5)

	def test_nakedSingleUpdatePossibilityMatrix(self):
		self.pMatrix = MockObject()
		self.pMatrix.updateRow = MagicMock()
		self.pMatrix.updateColum = MagicMock()
		self.pMatrix.updateBlock = MagicMock()
		self.pMatrix.addKnownSingle = MagicMock()
		self.pMatrix.setPossibilityAt = MagicMock()

		single = Single((0, 1), 5)

		single.update(self.pMatrix)

		self.pMatrix.updateRow.assert_called_once_with((0, 1), {5}, {(0,  1)})
		self.pMatrix.updateColum.assert_called_once_with((0, 1), {5}, {(0, 1)})
		self.pMatrix.updateBlock.assert_called_once_with((0, 1), {5}, {(0, 1)})
		self.pMatrix.addKnownSingle.assert_called_once_with(single)
		self.pMatrix.setPossibilityAt.assert_called_once_with((0, 1), {5})
		pass

	def test_findHiddenSingleInARow(self):
		self.pMatrix = PossibilityMatrix([[{1, 2}, {2, 3}]], Grid(1, 2, 1, 1))
		single = self.pMatrix.findNewSingle()

		single.updatePuzzle(self.puzzle)
		self.puzzle.change.assert_called_once_with((0, 0), 1)		
		pass

	def test_findHiddenSingleInAColumn(self):
		self.pMatrix = PossibilityMatrix([[{3, 2}, {2, 3}], [{2, 3, 4}, {2, 3, 4}]], Grid(2, 2, 1, 1))
		single = self.pMatrix.findNewSingle()

		single.updatePuzzle(self.puzzle)
		self.puzzle.change.assert_called_once_with((1, 0), 4)
		pass

	def test_findHiddenSingleInABlock(self):
		self.pMatrix = PossibilityMatrix([[{3, 2}, {2, 3}, {2, 3}, {2, 3}], 
			                             [{2, 3, 4}, {2, 3}, {2, 3, 4}, {2, 3, 4}],
			                             [{2, 3, 4}, {2, 3}, {2, 3, 4}, {2, 3, 4}],
			                             [{2, 3, 4}, {2, 3}, {2, 3, 4}, {2, 3, 4}]], Grid(4, 4, 2, 2))
		single = self.pMatrix.findNewSingle()

		single.updatePuzzle(self.puzzle)
		self.puzzle.change.assert_called_once_with((1, 0), 4)		
		pass

class TestTierOneStrategy(unittest.TestCase):
	def setUp(self):
		self.pMatrix = MockObject()
		self.puzzle = MockObject()
		self.stg_0 = MockObject()
		self.stg_0.solve = MagicMock()
		self.stg_1 = Tier_1_Strategy(self.stg_0)
		pass
		
	def test_noTier1Findings(self):
		self.pMatrix.findNewPairOrBlock = MagicMock(return_value = None)
		self.stg_1.solve(self.pMatrix, self.puzzle)
		self.pMatrix.findNewPairOrBlock.assert_called_once_with()
		pass

	def test_1Tier1Findings(self):
		self.finding = MockObject()
		self.finding.update = MagicMock()
		self.pMatrix.findNewPairOrBlock = MagicMock(side_effect = [self.finding, None])

		self.stg_1.solve(self.pMatrix, self.puzzle)

		self.assertEquals([call(), call], self.pMatrix.findNewPairOrBlock.mock_calls)
		pass

class TestPossibilityMatrixFindPairs(unittest.TestCase):
	def test_findNoPairs(self):
		pMatrix = PossibilityMatrix([[]], Grid(0, 0, 1, 1))
		self.assertEquals(None, pMatrix.findNewPairOrBlock())
		pass

	def test_findOneNakedPairInARow(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 3}, {1, 2}]], Grid(1, 3, 1, 1))
		pMatrix.updateRow = MagicMock()
		pMatrix.addKnownRowPair = MagicMock()
		pair = pMatrix.findNewPairOrBlock()
		pair.update(pMatrix)
		pMatrix.updateRow.assert_called_once_with((0, 0), {1, 2}, {(0, 0), (0, 2)})
		pMatrix.addKnownRowPair.assert_called_once_with(pair)
		pass

	def test_findOnePairOnlyOnceInARow(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 3}, {1, 2}]], Grid(1, 3, 1, 1))
		pMatrix.updateRow = MagicMock()
		pMatrix.addKnownRowPair = MagicMock()		
		pair = pMatrix.findNewPairOrBlock()
		pair.update(pMatrix)
		pMatrix.updateRow.assert_called_once_with((0, 0), {1, 2}, {(0, 0), (0, 2)})
		pass		
	pass
