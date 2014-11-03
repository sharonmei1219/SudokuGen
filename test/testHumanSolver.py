import unittest
from unittest.mock import MagicMock
from unittest.mock import ANY
from unittest.mock import call
from humanSolver import *
from puzzle import Grid

class MockObject:
	pass

class TestNakedSingleFinder(unittest.TestCase):
	def setUp(self):
		self.finder = NakedFinder(1, RowView(), [])
		pass

	def testFindNoNakedSingle(self):
		pMatrix = PossibilityMatrix([[{1, 2}]], Grid(1, 1, 1, 1))
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)
		pass

	def testFindNakedSingleIn2ndRow(self):
		pMatrix = PossibilityMatrix([[{1, 2}], [{1}]], Grid(2, 1, 1, 1))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0)}, {1}, RowView()), result)
		pass

	def testFind2ndNakedSingleAfter1stSingleHasBeenUpdated(self):
		pMatrix = PossibilityMatrix([[{1}, {2}]], Grid(1, 2, 1, 1))
		self.finder.addKnownFinding(Finding({(0, 0)}, {1}, RowView()))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1)}, {2}, RowView()), result)
		pass

class TestNakedPairFinder(unittest.TestCase):
	def setUp(self):
		self.finder = NakedFinder(2, RowView(), [])
		pass

	def testFindNoNakedPairInRow(self):
		pMatrix = PossibilityMatrix([[{1}, {2, 3}]], Grid(1, 2, 1, 1))
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)
		pass

	def testFind2ndNakedPairInRowAfter1stPairHasBeenUpdated(self):
		pMatrix = PossibilityMatrix([[{2, 3}, {4, 5}, {4, 5}, {2, 3}]], Grid(1, 4, 1, 1))
		self.finder.addKnownFinding(Finding({(0, 3), (0, 0)}, {2, 3}, RowView()))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1), (0, 2)}, {4, 5}, RowView()), result)			
		pass

	def testFindNakedPairIn2ndRow(self):
		pMatrix = PossibilityMatrix([[{2, 3, 4}, {2, 3, 5}], [{1, 4}, {1, 4}]], Grid(2, 2, 1, 1))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0), (1, 1)}, {1, 4}, RowView()), result)			
		pass		

class TestNakedTrippleFinder(unittest.TestCase):
	def setUp(self):
		self.finder = NakedFinder(3, RowView(), [])
		pass

	def testFind2ndNakedTrippleAfter1stHasBeenUpdated(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {4, 5}, {5, 6}, {2, 3}, {4, 6}, {1, 3}]], Grid(1, 6, 1, 1))
		self.finder.addKnownFinding(Finding({(0, 0), (0, 3), (0, 5)}, {1, 2, 3}, RowView()))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1), (0, 2), (0, 4)}, {4, 5, 6}, RowView()), result)
		pass

	def testFindNakedTrippleIn2ndLine(self):
		pMatrix = PossibilityMatrix([[{1, 4}, {2, 3}, {1, 3}], [{4, 5}, {5, 6}, {4, 6}]], Grid(2, 3, 1, 1))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0), (1, 1), (1, 2)}, {4, 5, 6}, RowView()), result)
		pass

class TestHiddenSingleFinder(unittest.TestCase):
	def setUp(self):
		self.finder = HiddenFinder(1, RowView(), [])
		pass

	def testFindNoHiddenSingle(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 1}]], Grid(1, 2, 1, 1))
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)		
		pass

	def testFind2stHiddenSingleWhen1stSingleHasBeenUpdated(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 3}, {2, 3, 4}]], Grid(1, 3, 1, 1))
		self.finder.addKnownFinding(Finding({(0, 0)}, {1}, RowView()))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 2)}, {4}, RowView()), result)
		pass

	def testFindHiddenSingleIn2ndRow(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}], [{3, 4, 1}, {4, 1}]], Grid(2, 2, 1, 1))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0)}, {3}, RowView()), result)		
		pass


class TestHiddenPairFinder(unittest.TestCase):
	def setUp(self):
		self.finder = HiddenFinder(2, RowView(), [])
		pass

	def test_findNoHiddenPair(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}, {1, 2}]], Grid(1, 3, 1, 1))
		self.assertEquals(None, self.finder.find(pMatrix))
		pass

	def test_findHiddenPairInARowOnlyOnce(self):
		pMatrix = PossibilityMatrix([[{1, 2, 5}, {3, 4, 6}, {1, 2, 6}, {3, 4, 5}]], Grid(1, 4, 1, 1))
		self.finder.addKnownFinding(Finding({(0, 0), (0, 2)}, {1, 2}, RowView()))
		self.assertEquals(Finding({(0, 1), (0, 3)}, {3, 4}, RowView()), self.finder.find(pMatrix))		
		pass

	def test_findHiddenPairIn2ndRow(self):
		pMatrix = PossibilityMatrix([[{1, 2, 4}, {1, 2, 4}, {1, 2, 7}], [{3, 4, 5}, {3, 4}, {5, 6}]], Grid(2, 3, 1, 1))
		self.assertEquals(Finding({(1, 0), (1, 1)}, {3, 4}, RowView()), self.finder.find(pMatrix))		
		pass

class TestHiddenTripple(unittest.TestCase):
	def setUp(self):
		self.finder = HiddenFinder(3, RowView(), [])
		pass

	def testFindNoHiddenTripple(self):
		pMatrix = PossibilityMatrix([[{1, 2, 3}, {1, 2, 3}, {1, 2, 3}, {1, 2, 3}]], Grid(1, 4, 1, 1))
		self.assertEquals(None, self.finder.find(pMatrix))		
		pass

	def testFind2ndHiddenTrippleAfter1stHasBeenUpdated(self):
		pMatrix = PossibilityMatrix([[{1, 2, 3}, {1, 2, 3}, {4, 5, 7, 8}, {5, 6, 7, 8}, {1, 2, 3}, {4, 6, 7, 8}, {7, 8}]], Grid(1, 7, 1, 1))
		self.finder.addKnownFinding(Finding({(0, 0), (0, 1), (0, 4)}, {1, 2, 3}, RowView()))
		self.assertEquals(Finding({(0, 2), (0, 3), (0, 5)}, {4, 5, 6}, RowView()), self.finder.find(pMatrix))		
		pass

	def testFindHiddenTrippleIn2ndRow(self):
		pMatrix = PossibilityMatrix([[{1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}], 
			                         [{1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}, {4, 5}]], Grid(2, 4, 1, 1))
		self.assertEquals(Finding({(1, 0), (1, 1), (1, 2)}, {1, 2, 3}, RowView()), self.finder.find(pMatrix))		
		pass		

class TestPossibilityMatrix:
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

class TestLockedCellFinder(unittest.TestCase):
	def testFindLockedCellFromARow(self):
		pMatrix = PossibilityMatrix([[{1}, {1}, {2, 3, 4}, {3, 4, 5}],
									 [{1, 2}, {1, 3}, {4, 5, 6}, {5, 6, 7}]], Grid(2, 4, 2, 2))
		finder = LockedCellFinder(RowView(), BlockView())
		result = finder.findNewClue(pMatrix)

		self.assertEquals(Finding({(0, 0), (0, 1)}, {1}, BlockView()), result)
		pass
	pass

class TestViewDirectionPosesInSameZone(unittest.TestCase):
	def testPosesInSameBlock(self):
		grid = Grid(4, 4, 2, 2)
		view = BlockView()
		poses = {(0, 0), (0, 1)}
		self.assertTrue(view.posesInSameZone(poses, grid))
		pass
	pass

class TestHiddenFinderUpdateFindings(unittest.TestCase):
	def testHiddenFinderUpdateFindings(self):
		pMatrix = MockObject()
		pMatrix.setPossibilityAt = MagicMock()
		knownResult = []
		finding = Finding({(0, 0), (0, 1)}, {1, 2}, RowView())
		finder = HiddenFinder(2, RowView(), knownResult)
		finder.update(finding, pMatrix)
		self.assertTrue(call((0, 0), {1, 2}) in pMatrix.setPossibilityAt.mock_calls)
		self.assertTrue(call((0, 1), {1, 2}) in pMatrix.setPossibilityAt.mock_calls)
		self.assertEquals(finding, knownResult[0])
		pass

class TestNakedFinderUpdateFindings(unittest.TestCase):
	def testNakedFinderUpdateFindings(self):
		pMatrix = MagicMock()
		view = RowView()
		pMatrix.update = MagicMock()
		knownResult = []
		finding = Finding({(0, 0), (0, 1)}, {1, 2}, view)
		finder = NakedFinder(2, RowView(), knownResult)
		pass
	pass
	
		
		
		