import unittest
from unittest.mock import MagicMock
from unittest.mock import ANY
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
		self.stg.updatePuzzle = MagicMock()
		self.puzzle = MockObject()
		self.pMatrix = MockObject()
		self.single_0 = MockObject()
		self.single_0.update = MagicMock()
		self.single_1 = MockObject()
		self.single_1.update = MagicMock()
		pass

	def test_NoSingleFound(self):
		self.stg.findNewSingle = MagicMock(return_value = None)
		self.stg.solve(self.pMatrix, self.puzzle)
		self.stg.findNewSingle.assert_called_once_with(self.pMatrix)
		pass

	def test_TwoSingleFound(self):
		self.stg.findNewSingle = MagicMock(side_effect = [self.single_0, self.single_1, None])
		self.stg.solve(self.pMatrix, self.puzzle)

		self.assertEquals([call(self.pMatrix), call(self.pMatrix), call(self.pMatrix)], self.stg.findNewSingle.mock_calls)
		self.single_0.update.assert_called_once_with(self.pMatrix)
		self.single_1.update.assert_called_once_with(self.pMatrix)
		self.assertEquals([call(self.single_0, self.puzzle), call(self.single_1, self.puzzle)], self.stg.updatePuzzle.mock_calls)
		pass

	def test_useSingleToUpdatePuzzle(self):
		stg = Tier_0_Strategy()
		puzzle = MockObject()
		puzzle.change = MagicMock()
		single = FindingInRow([(0, 1)], {2}, RowView())
		stg.updatePuzzle(single, puzzle)
		puzzle.change.assert_called_once_with((0, 1), 2)
		pass

class TestPossibilityMatrixFindSingles(unittest.TestCase):
	def setUp(self):
		self.puzzle = MockObject()
		self.puzzle.change = MagicMock()
		self.stg_0 = Tier_0_Strategy()
		pass

	def test_findNoSingle(self):
		self.pMatrix = PossibilityMatrix([[]], Grid(0, 0, 1, 1))
		self.assertEquals(None, self.stg_0.findNewSingle(self.pMatrix))
		pass

	def test_findOneSingle(self):
		self.pMatrix = PossibilityMatrix([[{1}]], Grid(1, 1, 1, 1))
		single = self.stg_0.findNewSingle(self.pMatrix)
		self.assertEqual(FindingInRow({(0, 0)}, {1}, RowView()), single)
		pass

	def test_findSingleOnlyOnce(self):
		self.pMatrix = PossibilityMatrix([[{1}, {2}]], Grid(1, 2, 1, 1))
		single = self.stg_0.findNewSingle(self.pMatrix)
		single.update(self.pMatrix)

		single = self.stg_0.findNewSingle(self.pMatrix)
		self.assertEqual(FindingInRow({(0, 1)}, {2}, RowView()), single)
		pass

	def test_findSingleInColumn(self):
		self.pMatrix = PossibilityMatrix([[{1}]], Grid(1, 1, 1, 1))
		self.pMatrix.addKnownRowFindings(Finding({(0, 0)}, {1}, RowView()))

		self.pMatrix.update = MagicMock(name="updateColum")
		single = self.stg_0.findNewSingle(self.pMatrix)
		single.update(self.pMatrix)

		self.pMatrix.update.assert_called_once_with((0, 0), {1}, {(0, 0)}, ANY)
		pass

	def test_findSingleInColumnOnlyOnce(self):
		self.pMatrix = PossibilityMatrix([[{1}], [{2}]], Grid(2, 1, 1, 1))
		self.pMatrix.addKnownRowFindings(Finding({(0, 0)}, {1}, RowView()))
		self.pMatrix.addKnownRowFindings(Finding({(1, 0)}, {2}, RowView()))
		self.pMatrix.addKnownColumnFindings(FindingInColumn({(0, 0)}, {1}, ColumnView()))

		self.pMatrix.update = MagicMock(name="updateColum")
		single = self.stg_0.findNewSingle(self.pMatrix)
		single.update(self.pMatrix)

		self.pMatrix.update.assert_called_once_with((1, 0), {2}, {(1, 0)}, ANY)
		pass

	def test_findSingleInABlock(self):
		self.pMatrix = PossibilityMatrix([[{1}, {3, 4}], [{2, 3}, {5}]], Grid(2, 2, 2, 2))
		self.pMatrix.addKnownRowFindings(Finding({(0, 0)}, {1}, RowView()))
		self.pMatrix.addKnownColumnFindings(Finding({(0, 0)}, {1}, ColumnView()))
		self.pMatrix.addKnownRowFindings(Finding({(1, 1)}, {5}, RowView()))
		self.pMatrix.addKnownColumnFindings(Finding({(1, 1)}, {5}, ColumnView()))

		self.pMatrix.update = MagicMock(name="updateBlock")

		single = self.stg_0.findNewSingle(self.pMatrix)

		single.update(self.pMatrix)
		self.pMatrix.update.assert_called_once_with((0, 0), {1}, {(0, 0)}, ANY)
		pass

	def test_findSingleInABlockOnlyOnce(self):
		self.pMatrix = PossibilityMatrix([[{1}, {3, 4}], [{2, 3}, {5}]], Grid(2, 2, 2, 2))
		self.pMatrix.addKnownRowFindings(Finding({(0, 0)}, {1}, RowView()))
		self.pMatrix.addKnownColumnFindings(Finding({(0, 0)}, {1}, ColumnView()))
		self.pMatrix.addKnownRowFindings(Finding({(1, 1)}, {5}, RowView))
		self.pMatrix.addKnownColumnFindings(Finding({(1, 1)}, {5}, ColumnView()))
		self.pMatrix.addKnownBlockFindings(Finding({(0, 0)}, {1}, BlockView()))

		self.pMatrix.update = MagicMock(name="updateBlock")

		single = self.stg_0.findNewSingle(self.pMatrix)

		single.update(self.pMatrix)
		self.pMatrix.update.assert_called_once_with((1, 1), {5}, {(1, 1)}, ANY)
		pass


	def test_updateRow(self):
		self.pMatrix = PossibilityMatrix([[{1}, {1, 2}]], Grid(1, 2, 1, 1))
		self.pMatrix.update((0, 0), {1}, {(0, 0)}, RowView())
		self.assertEquals([{1}, {2}], self.pMatrix.matrix[0])
		pass

	def test_updateColum(self):
		self.pMatrix = PossibilityMatrix([[{1}], [{1, 2}]], Grid(2, 1, 1, 1))
		self.pMatrix.update((0, 0), {1}, {(0, 0)}, ColumnView())
		self.assertEquals([[{1}],[{2}]], self.pMatrix.matrix)
		pass

	def test_updateBlock(self):
		self.pMatrix = PossibilityMatrix([[{1, 2}, {1, 2, 3}],
										  [{2, 4}, {1, 5}]], Grid(2, 2, 2, 2))
		self.pMatrix.update((0, 0), {1, 2}, {(0, 0)}, BlockView())
		self.assertEquals([[{1, 2}, {3}],[{4}, {5}]], self.pMatrix.matrix)		
		pass

	def test_nakedSingleUpdatePossibilityMatrix(self):
		self.pMatrix = MockObject()
		self.pMatrix.update = MagicMock(name="updateRow")
		self.pMatrix.addKnownRowFindings = MagicMock()
		self.pMatrix.setPossibilityAt = MagicMock()

		single = FindingInRow([(0, 1)], {5}, RowView())

		single.update(self.pMatrix)

		self.pMatrix.update.assert_called_once_with((0, 1), {5}, {(0,  1)}, ANY)
		self.pMatrix.addKnownRowFindings.assert_called_once_with(single)
		self.pMatrix.setPossibilityAt.assert_called_once_with((0, 1), {5})
		pass

	def test_nakedColumnSingleUpdatePossibilityMatrix(self):
		self.pMatrix = MockObject()
		self.pMatrix.update = MagicMock(name="updateColum")
		self.pMatrix.addKnownColumnFindings = MagicMock(name = "addKnownColumnFindings")
		self.pMatrix.setPossibilityAt = MagicMock()

		single = FindingInColumn([(0, 1)], {5}, RowView())
		single.update(self.pMatrix)

		self.pMatrix.update.assert_called_once_with((0, 1), {5}, {(0, 1)}, ANY)
		self.pMatrix.addKnownColumnFindings.assert_called_once_with(single)
		self.pMatrix.setPossibilityAt.assert_called_once_with((0, 1), {5})		
		pass

	def test_nakedBlockSingleUpdatePossibilityMatrix(self):
		self.pMatrix = MockObject()
		self.pMatrix.update = MagicMock(name="updateBlock")
		self.pMatrix.addKnownBlockFindings = MagicMock(name = "addKnownBlockSingle")
		self.pMatrix.setPossibilityAt = MagicMock()

		single = FindingInBlock([(0, 1)], {5}, RowView())
		single.update(self.pMatrix)

		self.pMatrix.update.assert_called_once_with((0, 1), {5}, {(0, 1)}, ANY)
		self.pMatrix.addKnownBlockFindings.assert_called_once_with(single)
		self.pMatrix.setPossibilityAt.assert_called_once_with((0, 1), {5})		
		pass		

	def test_findHiddenSingleInARow(self):
		self.pMatrix = PossibilityMatrix([[{1, 2}, {2, 3}]], Grid(1, 2, 1, 1))
		single = self.stg_0.findNewSingle(self.pMatrix)
		self.assertEqual(FindingInRow({(0, 0)}, {1}, RowView()), single)	
		pass

	def test_findHiddenSingleInAColumn(self):
		self.pMatrix = PossibilityMatrix([[{3, 2}, {2, 3}], [{2, 3, 4}, {2, 3, 4}]], Grid(2, 2, 1, 1))
		single = self.stg_0.findNewSingle(self.pMatrix)
		self.assertEqual(FindingInRow({(1, 0)}, {4}, RowView()), single)
		pass

	def test_findHiddenSingleInABlock(self):
		self.pMatrix = PossibilityMatrix([[{3, 2}, {2, 3}, {2, 3}, {2, 3}], 
			                             [{2, 3, 4}, {2, 3}, {2, 3, 4}, {2, 3, 4}],
			                             [{2, 3, 4}, {2, 3}, {2, 3, 4}, {2, 3, 4}],
			                             [{2, 3, 4}, {2, 3}, {2, 3, 4}, {2, 3, 4}]], Grid(4, 4, 2, 2))
		single = self.stg_0.findNewSingle(self.pMatrix)

		self.assertEqual(FindingInRow({(1, 0)}, {4}, RowView()), single)		
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
		self.stg_1.findNewPairOrLockedCell = MagicMock(return_value = None)
		self.stg_1.solve(self.pMatrix, self.puzzle)
		self.stg_1.findNewPairOrLockedCell.assert_called_once_with(self.pMatrix)
		pass

	def test_1Tier1Findings(self):
		self.finding = MockObject()
		self.finding.update = MagicMock()
		self.stg_1.findNewPairOrLockedCell = MagicMock(side_effect = [self.finding, None])

		self.stg_1.solve(self.pMatrix, self.puzzle)

		self.assertEquals([call(self.pMatrix), call(self.pMatrix)], self.stg_1.findNewPairOrLockedCell.mock_calls)
		pass

class TestPossibilityMatrixFindPairs(unittest.TestCase):

	def setUp(self):
		self.stg_0 = Tier_0_Strategy()
		self.stg_1 = Tier_1_Strategy(self.stg_0)
		pass

	def test_findNoPairs(self):
		pMatrix = PossibilityMatrix([[]], Grid(0, 0, 1, 1))
		self.assertEquals(None, self.stg_1.findNewPairOrLockedCell(pMatrix))
		pass

	def test_findOneNakedPairInARow(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 3}, {1, 2}]], Grid(1, 3, 1, 1))
		pMatrix.update = MagicMock()
		pMatrix.addKnownRowFindings = MagicMock()
		pair = self.stg_1.findNewPairOrLockedCell(pMatrix)
		pair.update(pMatrix)
		pMatrix.update.assert_called_once_with((0, 0), {1, 2}, {(0, 0), (0, 2)}, ANY)
		pMatrix.addKnownRowFindings.assert_called_once_with(pair)
		pass

	def test_findOnePairOnlyOnceInARow(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {3, 4}, {1, 2}, {3, 4}]], Grid(1, 4, 1, 1))
		pMatrix.update = MagicMock()
		pair = self.stg_1.findNewPairOrLockedCell(pMatrix)
		pMatrix.addKnownRowFindings(pair)
		pair = self.stg_1.findNewPairOrLockedCell(pMatrix)
		pair.update(pMatrix)

		pMatrix.update.assert_called_once_with((0, 1), {3, 4}, {(0, 1), (0, 3)}, ANY)
		pass

	def test_findOneNakedPairInAColumn(self):
		pMatrix = PossibilityMatrix([[{1, 2}],[{3, 4}],[{1, 2}]], Grid(3, 1, 1, 1))
		pMatrix.update = MagicMock(name="updateColumn")
		pMatrix.addKnownColumnFindings = MagicMock()

		pair = self.stg_1.findNewPairOrLockedCell(pMatrix)
		pair.update(pMatrix)
		pMatrix.update.assert_called_once_with(next(iter({(0, 0), (2, 0)})), {1, 2}, {(0, 0), (2, 0)}, ANY)
		pMatrix.addKnownColumnFindings.assert_called_once_with(pair)
		pass

	def test_findNakedPairOnceInAColumn(self):
		pMatrix = PossibilityMatrix([[{1, 2}],[{3, 4}],[{1, 2}], [{3, 4}]], Grid(4, 1, 1, 1))
		pMatrix.addKnownColumnFindings(FindingInColumn({(0, 0), (2, 0)}, {1, 2}, ColumnView()))
		pair = self.stg_1.findNewPairOrLockedCell(pMatrix)
		self.assertEquals(FindingInColumn({(1, 0), (3, 0)}, {3, 4}, ColumnView()), pair)
		pass

	def test_findOneNakedPairInABlock(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {3, 4}], [{3, 4}, {1, 2}]], Grid(2, 2, 2, 2))
		pair = self.stg_1.findNewPairOrLockedCell(pMatrix)
		self.assertEquals(FindingInBlock({(0, 0), (1, 1)}, {1, 2}, BlockView()), pair)		
		pass

	def test_findNakedPairInABlockOnlyOnce(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {3, 4}], [{3, 4}, {1, 2}]], Grid(2, 2, 2, 2))
		pMatrix.addKnownBlockFindings(FindingInBlock({(0, 0), (1, 1)}, {1, 2}, BlockView()))
		pair = self.stg_1.findNewPairOrLockedCell(pMatrix)
		self.assertEquals(FindingInBlock({(0, 1), (1, 0)}, {3, 4}, BlockView()), pair)		
		pass

class TestHiddenPairFinder(unittest.TestCase):
	def setUp(self):
		self.finder = HiddenFinder(2, RowView())
		pass

	def test_findNoHiddenPair(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}, {1}]], Grid(1, 3, 1, 1))
		self.assertEquals(None, self.finder.find(pMatrix))
		pass

	def test_findOneHiddenPairInARow(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}]], Grid(1, 2, 1, 1))
		self.assertEquals(Finding({(0, 0), (0, 1)}, {1, 2}, RowView()), self.finder.find(pMatrix))
		pass

	def test_findHiddenPairInARowOnlyOnce(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {3, 4}, {1, 2}, {3, 4}]], Grid(1, 4, 1, 1))
		pMatrix.addKnownRowFindings(Finding({(0, 0), (0, 2)}, {1, 2}, RowView()))
		self.assertEquals(Finding({(0, 1), (0, 3)}, {3, 4}, RowView()), self.finder.find(pMatrix))		
		pass

class TestViewDirection(unittest.TestCase):

	def setUp(self):
		self.grid = MockObject()
		self.grid.coordsOfRow = MagicMock(return_value = [(0, 0), (0, 1)])
		self.grid.coordsOfColumn = MagicMock(return_value = [(0, 0), (0, 1)])
		self.grid.coordsOfBlock = MagicMock(return_value = [(0, 0), (0, 1)])
		pass

	def testGetRowWithPosIn(self):
		view = RowView()
		zone = view.zoneWithPosIn((0, 0), self.grid)
		self.grid.coordsOfRow.assert_called_once_with(0, 0)
		self.assertEquals([(0, 0), (0, 1)], zone)
		pass

	def testGetColumnWithPosIn(self):
		view = ColumnView()
		zone = view.zoneWithPosIn((0, 0), self.grid)
		self.grid.coordsOfColumn.assert_called_once_with(0, 0)
		pass

	def testGetBlockWithPosIn(self):
		view = BlockView()
		zone = view.zoneWithPosIn((0, 0), self.grid)
		self.grid.coordsOfBlock.assert_called_once_with(0, 0)
		pass

class TestViewDirectionUpdate(unittest.TestCase):
	def setUp(self):
		self.finding = MockObject()
		self.pMatrix = MockObject()
		self.pMatrix.addKnownRowFindings = MagicMock()
		self.pMatrix.addKnownColumnFindings = MagicMock()
		self.pMatrix.addKnownBlockFindings = MagicMock()
		pass

	def testAddKnownFindingsInRow(self):
		view = RowView()
		view.addKnownFindingsToPossibilityMatrix(self.finding, self.pMatrix)
		self.pMatrix.addKnownRowFindings.assert_called_once_with(self.finding)
		pass

	def testAddKnownFindingsInColumn(self):
		view = ColumnView()
		view.addKnownFindingsToPossibilityMatrix(self.finding, self.pMatrix)
		self.pMatrix.addKnownColumnFindings.assert_called_once_with(self.finding)
		pass

	def testAddKnownFindingsInBlock(self):
		view = BlockView()
		view.addKnownFindingsToPossibilityMatrix(self.finding, self.pMatrix)
		self.pMatrix.addKnownBlockFindings.assert_called_once_with(self.finding)
		pass
	pass