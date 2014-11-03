import unittest
from unittest.mock import MagicMock
from unittest.mock import ANY
from unittest.mock import call
from humanSolver import *
from puzzle import *

class MockObject:
	pass

class TestNakedSingleFinder(unittest.TestCase):

	def testFindNoNakedSingle(self):
		pMatrix = PossibilityMatrix([[{1, 2}]], Grid(1, 1, 1, 1))
		self.finder = NakedFinder(1, pMatrix.grid.gridRow, [])		
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)
		pass

	def testFindNakedSingleIn2ndRow(self):
		pMatrix = PossibilityMatrix([[{1, 2}], [{1}]], Grid(2, 1, 1, 1))
		self.finder = NakedFinder(1, pMatrix.grid.gridRow, [])
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0)}, {1}), result)
		pass

	def testFind2ndNakedSingleAfter1stSingleHasBeenUpdated(self):
		pMatrix = PossibilityMatrix([[{1}, {2}]], Grid(1, 2, 1, 1))
		self.finder = NakedFinder(1, pMatrix.grid.gridRow, [])
		self.finder.addKnownFinding(Finding({(0, 0)}, {1}))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1)}, {2}), result)
		pass

class TestNakedPairFinder(unittest.TestCase):
	def testFindNoNakedPairInRow(self):
		pMatrix = PossibilityMatrix([[{1}, {2, 3}]], Grid(1, 2, 1, 1))
		self.finder = NakedFinder(2, pMatrix.grid.gridRow, [])
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)
		pass

	def testFind2ndNakedPairInRowAfter1stPairHasBeenUpdated(self):
		pMatrix = PossibilityMatrix([[{2, 3}, {4, 5}, {4, 5}, {2, 3}]], Grid(1, 4, 1, 1))
		self.finder = NakedFinder(2, pMatrix.grid.gridRow, [])
		self.finder.addKnownFinding(Finding({(0, 3), (0, 0)}, {2, 3}))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1), (0, 2)}, {4, 5}), result)			
		pass

	def testFindNakedPairIn2ndRow(self):
		pMatrix = PossibilityMatrix([[{2, 3, 4}, {2, 3, 5}], [{1, 4}, {1, 4}]], Grid(2, 2, 1, 1))
		self.finder = NakedFinder(2, pMatrix.grid.gridRow, [])
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0), (1, 1)}, {1, 4}), result)			
		pass		

class TestNakedTrippleFinder(unittest.TestCase):
	def testFind2ndNakedTrippleAfter1stHasBeenUpdated(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {4, 5}, {5, 6}, {2, 3}, {4, 6}, {1, 3}]], Grid(1, 6, 1, 1))
		self.finder = NakedFinder(3, pMatrix.grid.gridRow, [])
		self.finder.addKnownFinding(Finding({(0, 0), (0, 3), (0, 5)}, {1, 2, 3}))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1), (0, 2), (0, 4)}, {4, 5, 6}), result)
		pass

	def testFindNakedTrippleIn2ndLine(self):
		pMatrix = PossibilityMatrix([[{1, 4}, {2, 3}, {1, 3}], [{4, 5}, {5, 6}, {4, 6}]], Grid(2, 3, 1, 1))
		self.finder = NakedFinder(3, pMatrix.grid.gridRow, [])		
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0), (1, 1), (1, 2)}, {4, 5, 6}), result)
		pass

class TestHiddenSingleFinder(unittest.TestCase):

	def testFindNoHiddenSingle(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 1}]], Grid(1, 2, 1, 1))
		self.finder = HiddenFinder(1, pMatrix.grid.gridRow, [])
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)		
		pass

	def testFind2stHiddenSingleWhen1stSingleHasBeenUpdated(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 3}, {2, 3, 4}]], Grid(1, 3, 1, 1))
		self.finder = HiddenFinder(1, pMatrix.grid.gridRow, [])
		self.finder.addKnownFinding(Finding({(0, 0)}, {1}))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 2)}, {4}), result)
		pass

	def testFindHiddenSingleIn2ndRow(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}], [{3, 4, 1}, {4, 1}]], Grid(2, 2, 1, 1))
		self.finder = HiddenFinder(1, pMatrix.grid.gridRow, [])
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0)}, {3}), result)		
		pass


class TestHiddenPairFinder(unittest.TestCase):

	def test_findNoHiddenPair(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}, {1, 2}]], Grid(1, 3, 1, 1))
		self.finder = HiddenFinder(2, pMatrix.grid.gridRow, [])
		self.assertEquals(None, self.finder.find(pMatrix))
		pass

	def test_findHiddenPairInARowOnlyOnce(self):
		pMatrix = PossibilityMatrix([[{1, 2, 5}, {3, 4, 6}, {1, 2, 6}, {3, 4, 5}]], Grid(1, 4, 1, 1))
		self.finder = HiddenFinder(2, pMatrix.grid.gridRow, [])
		self.finder.addKnownFinding(Finding({(0, 0), (0, 2)}, {1, 2}))
		self.assertEquals(Finding({(0, 1), (0, 3)}, {3, 4}), self.finder.find(pMatrix))		
		pass

	def test_findHiddenPairIn2ndRow(self):
		pMatrix = PossibilityMatrix([[{1, 2, 4}, {1, 2, 4}, {1, 2, 7}], [{3, 4, 5}, {3, 4}, {5, 6}]], Grid(2, 3, 1, 1))
		self.finder = HiddenFinder(2, pMatrix.grid.gridRow, [])
		self.assertEquals(Finding({(1, 0), (1, 1)}, {3, 4}), self.finder.find(pMatrix))		
		pass

class TestHiddenTripple(unittest.TestCase):
	def setUp(self):
		
		pass

	def testFindNoHiddenTripple(self):
		pMatrix = PossibilityMatrix([[{1, 2, 3}, {1, 2, 3}, {1, 2, 3}, {1, 2, 3}]], Grid(1, 4, 1, 1))
		self.finder = HiddenFinder(3, pMatrix.grid.gridRow, [])
		self.assertEquals(None, self.finder.find(pMatrix))		
		pass

	def testFind2ndHiddenTrippleAfter1stHasBeenUpdated(self):
		pMatrix = PossibilityMatrix([[{1, 2, 3}, {1, 2, 3}, {4, 5, 7, 8}, {5, 6, 7, 8}, {1, 2, 3}, {4, 6, 7, 8}, {7, 8}]], Grid(1, 7, 1, 1))
		self.finder = HiddenFinder(3, pMatrix.grid.gridRow, [])
		self.finder.addKnownFinding(Finding({(0, 0), (0, 1), (0, 4)}, {1, 2, 3}))
		self.assertEquals(Finding({(0, 2), (0, 3), (0, 5)}, {4, 5, 6}), self.finder.find(pMatrix))		
		pass

	def testFindHiddenTrippleIn2ndRow(self):
		pMatrix = PossibilityMatrix([[{1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}], 
			                         [{1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}, {4, 5}]], Grid(2, 4, 1, 1))
		self.finder = HiddenFinder(3, pMatrix.grid.gridRow, [])
		self.assertEquals(Finding({(1, 0), (1, 1), (1, 2)}, {1, 2, 3}), self.finder.find(pMatrix))		
		pass		

class TestPossibilityMatrix:
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

class TestLockedCellFinder(unittest.TestCase):
	def testFindLockedCellFromARow(self):
		pMatrix = PossibilityMatrix([[{1}, {1}, {2, 3, 4}, {3, 4, 5}],
									 [{1, 2}, {1, 3}, {4, 5, 6}, {5, 6, 7}]], Grid(2, 4, 2, 2))
		finder = LockedCellFinder(pMatrix.grid.gridRow, pMatrix.grid.gridBlock, [])
		result = finder.findNewClue(pMatrix)

		self.assertEquals(Finding({(0, 0), (0, 1)}, {1}), result)
		pass
	pass

class TestViewDirectionPosesInSameZone(unittest.TestCase):
	def testPosesInSameBlock(self):
		# grid = Grid(4, 4, 2, 2)
		view = GridBlock(4, 4, 2, 2)
		poses = {(0, 0), (0, 1)}
		self.assertTrue(view.posesInSameZone(poses))
		pass
	pass
		