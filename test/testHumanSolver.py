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
		grid = GridRow(1, 1)
		pMatrix = PossibilityMatrix([[{1, 2}]])
		self.finder = NakedFinder(1, grid, [])		
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)
		pass

	def testFindNakedSingleIn2ndRow(self):
		grid = GridRow(2, 1)
		pMatrix = PossibilityMatrix([[{1, 2}], [{1}]])
		self.finder = NakedFinder(1, grid, [])
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0)}, {1}), result)
		pass

	def testFind2ndNakedSingleAfter1stSingleHasBeenUpdated(self):
		grid = GridRow(1, 2)
		pMatrix = PossibilityMatrix([[{1}, {2}]])
		self.finder = NakedFinder(1, grid, [])
		self.finder.addKnownFinding(Finding({(0, 0)}, {1}))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1)}, {2}), result)
		pass

class TestNakedPairFinder(unittest.TestCase):
	def testFindNoNakedPairInRow(self):
		grid = GridRow(1, 2)
		pMatrix = PossibilityMatrix([[{1}, {2, 3}]])
		self.finder = NakedFinder(2, grid, [])
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)
		pass

	def testFind2ndNakedPairInRowAfter1stPairHasBeenUpdated(self):
		grid = GridRow(1, 4)		
		pMatrix = PossibilityMatrix([[{2, 3}, {4, 5}, {4, 5}, {2, 3}]])
		self.finder = NakedFinder(2, grid, [])
		self.finder.addKnownFinding(Finding({(0, 3), (0, 0)}, {2, 3}))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1), (0, 2)}, {4, 5}), result)			
		pass

	def testFindNakedPairIn2ndRow(self):
		grid = GridRow(2, 2)		
		pMatrix = PossibilityMatrix([[{2, 3, 4}, {2, 3, 5}], [{1, 4}, {1, 4}]])
		self.finder = NakedFinder(2, grid, [])
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0), (1, 1)}, {1, 4}), result)			
		pass		

class TestNakedTrippleFinder(unittest.TestCase):
	def testFind2ndNakedTrippleAfter1stHasBeenUpdated(self):
		grid = Grid(1, 6, 1, 1)
		pMatrix = PossibilityMatrix([[{1, 2}, {4, 5}, {5, 6}, {2, 3}, {4, 6}, {1, 3}]])
		self.finder = NakedFinder(3, grid.gridRow, [])
		self.finder.addKnownFinding(Finding({(0, 0), (0, 3), (0, 5)}, {1, 2, 3}))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1), (0, 2), (0, 4)}, {4, 5, 6}), result)
		pass

	def testFindNakedTrippleIn2ndLine(self):
		grid = Grid(2, 3, 1, 1)
		pMatrix = PossibilityMatrix([[{1, 4}, {2, 3}, {1, 3}], [{4, 5}, {5, 6}, {4, 6}]])
		self.finder = NakedFinder(3, grid.gridRow, [])		
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0), (1, 1), (1, 2)}, {4, 5, 6}), result)
		pass

class TestHiddenSingleFinder(unittest.TestCase):

	def testFindNoHiddenSingle(self):
		grid = GridRow(1, 2)
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 1}]])
		self.finder = HiddenFinder(1, grid, [])
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)		
		pass

	def testFind2stHiddenSingleWhen1stSingleHasBeenUpdated(self):
		grid = GridRow(1, 3)
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 3}, {2, 3, 4}]])
		self.finder = HiddenFinder(1, grid, [])
		self.finder.addKnownFinding(Finding({(0, 0)}, {1}))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 2)}, {4}), result)
		pass

	def testFindHiddenSingleIn2ndRow(self):
		grid = GridRow(2, 2)
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}], [{3, 4, 1}, {4, 1}]])
		self.finder = HiddenFinder(1, grid, [])
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0)}, {3}), result)		
		pass

class TestHiddenPairFinder(unittest.TestCase):

	def test_findNoHiddenPair(self):
		grid = GridRow(1, 3)
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}, {1, 2}]])
		self.finder = HiddenFinder(2, grid, [])
		self.assertEquals(None, self.finder.find(pMatrix))
		pass

	def test_findHiddenPairInARowOnlyOnce(self):
		grid = GridRow(1, 4)
		pMatrix = PossibilityMatrix([[{1, 2, 5}, {3, 4, 6}, {1, 2, 6}, {3, 4, 5}]])
		self.finder = HiddenFinder(2, grid, [])
		self.finder.addKnownFinding(Finding({(0, 0), (0, 2)}, {1, 2}))
		self.assertEquals(Finding({(0, 1), (0, 3)}, {3, 4}), self.finder.find(pMatrix))		
		pass

	def test_findHiddenPairIn2ndRow(self):
		grid = GridRow(2, 3)
		pMatrix = PossibilityMatrix([[{1, 2, 4}, {1, 2, 4}, {1, 2, 7}], [{3, 4, 5}, {3, 4}, {5, 6}]])
		self.finder = HiddenFinder(2, grid, [])
		self.assertEquals(Finding({(1, 0), (1, 1)}, {3, 4}), self.finder.find(pMatrix))		
		pass

class TestHiddenTripple(unittest.TestCase):

	def testFindNoHiddenTripple(self):
		grid = GridRow(1, 4)
		pMatrix = PossibilityMatrix([[{1, 2, 3}, {1, 2, 3}, {1, 2, 3}, {1, 2, 3}]])
		self.finder = HiddenFinder(3, grid, [])
		self.assertEquals(None, self.finder.find(pMatrix))		
		pass

	def testFind2ndHiddenTrippleAfter1stHasBeenUpdated(self):
		grid = GridRow(1, 7)
		pMatrix = PossibilityMatrix([[{1, 2, 3}, {1, 2, 3}, {4, 5, 7, 8}, {5, 6, 7, 8}, {1, 2, 3}, {4, 6, 7, 8}, {7, 8}]])
		self.finder = HiddenFinder(3, grid, [])
		self.finder.addKnownFinding(Finding({(0, 0), (0, 1), (0, 4)}, {1, 2, 3}))
		self.assertEquals(Finding({(0, 2), (0, 3), (0, 5)}, {4, 5, 6}), self.finder.find(pMatrix))		
		pass

	def testFindHiddenTrippleIn2ndRow(self):
		grid = GridRow(2, 4)
		pMatrix = PossibilityMatrix([[{1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}], 
			                         [{1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}, {4, 5}]])
		self.finder = HiddenFinder(3, grid, [])
		self.assertEquals(Finding({(1, 0), (1, 1), (1, 2)}, {1, 2, 3}), self.finder.find(pMatrix))		
		pass		


class TestLockedCellFinder(unittest.TestCase):
	def testFindLockedCellFromARow(self):
		grid = Grid(2, 4, 2, 2)
		pMatrix = PossibilityMatrix([[{1}, {1}, {2, 3, 4}, {3, 4, 5}],
									 [{1, 2}, {1, 3}, {4, 5, 6}, {5, 6, 7}]])
		finder = LockedCellFinder(grid.gridRow, grid.gridBlock, [])
		result = finder.find(pMatrix)

		self.assertEquals(Finding({(0, 0), (0, 1)}, {1}), result)
		pass
	pass


class TestPossibilityMatrix(unittest.TestCase):
	def testErasePossibility(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}, {1}]])
		pMatrix.erasePossibility({1}, {(0, 0), (0, 1)})
		self.assertEquals({2}, pMatrix.possibilitieAt((0, 0)))
		self.assertEquals({2}, pMatrix.possibilitieAt((0, 1)))
		self.assertEquals({1}, pMatrix.possibilitieAt((0, 2)))
		pass

	def testSetPossibility(self):
		pMatrix = PossibilityMatrix([[{1, 2, 3}, {1, 2, 3}, {3, 4, 5}]])
		pMatrix.setPossibility({1, 2}, {(0, 0), (0, 1)})
		self.assertEquals({1, 2}, pMatrix.possibilitieAt((0, 0)))
		self.assertEquals({1, 2}, pMatrix.possibilitieAt((0, 1)))
		self.assertEquals({3, 4, 5}, pMatrix.possibilitieAt((0, 2)))
		pass

		