import unittest
from unittest.mock import MagicMock
from unittest.mock import ANY
from unittest.mock import call
from humanSolver import *
from puzzle import *
from puzzle import _

class MockObject:
	pass

class TestNakedSingleFinder(unittest.TestCase):

	def testFindNoNakedSingle(self):
		grid = GridRow(1, 1)
		pMatrix = PossibilityMatrix([[{1, 2}]])
		self.finder = NakedFinder(1, grid, KnownResultTypeOne())		
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)
		pass

	def testFindNakedSingleIn2ndRow(self):
		grid = GridRow(2, 1)
		pMatrix = PossibilityMatrix([[{1, 2}], [{1}]])
		self.finder = NakedFinder(1, grid, KnownResultTypeOne())
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0)}, {1}), result)
		pass

	def testFind2ndNakedSingleAfter1stSingleHasBeenUpdated(self):
		grid = GridRow(1, 2)
		pMatrix = PossibilityMatrix([[{1}, {2}]])
		self.finder = NakedFinder(1, grid, KnownResultTypeOne())
		self.finder.update(Finding({(0, 0)}, {1}), pMatrix)
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1)}, {2}), result)
		pass

class TestNakedPairFinder(unittest.TestCase):
	def testFindNoNakedPairInRow(self):
		grid = GridRow(1, 2)
		pMatrix = PossibilityMatrix([[{1}, {2, 3}]])
		self.finder = NakedFinder(2, grid, KnownResultTypeOne())
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)
		pass

	def testFind2ndNakedPairInRowAfter1stPairHasBeenUpdated(self):
		grid = GridRow(1, 4)		
		pMatrix = PossibilityMatrix([[{2, 3}, {4, 5}, {4, 5}, {2, 3}]])
		self.finder = NakedFinder(2, grid, KnownResultTypeOne())
		self.finder.update(Finding({(0, 3), (0, 0)}, {2, 3}), pMatrix)
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1), (0, 2)}, {4, 5}), result)			
		pass

	def testFind2SingleAsOnePair(self):
		grid = GridRow(1, 4)
		pMatrix = PossibilityMatrix([[{2}, {3}, {4, 5}, {4, 5}]])
		knownResult = KnownResultTypeOne()
		knownResult.add(Finding({(0, 0)}, {2}))
		knownResult.add(Finding({(0, 1)}, {3}))
		self.finder = NakedFinder(2, grid, knownResult)	
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 2), (0, 3)}, {4, 5}), result)			
		pass

	def testFindNakedPairIn2ndRow(self):
		grid = GridRow(2, 2)		
		pMatrix = PossibilityMatrix([[{2, 3, 4}, {2, 3, 5}], [{1, 4}, {1, 4}]])
		self.finder = NakedFinder(2, grid, KnownResultTypeOne())
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0), (1, 1)}, {1, 4}), result)			
		pass		

class TestNakedTrippleFinder(unittest.TestCase):
	def testFind2ndNakedTrippleAfter1stHasBeenUpdated(self):
		grid = Grid(1, 6, 1, 1)
		pMatrix = PossibilityMatrix([[{1, 2}, {4, 5}, {5, 6}, {2, 3}, {4, 6}, {1, 3}]])
		self.finder = NakedFinder(3, grid.gridRow, KnownResultTypeOne())
		self.finder.update(Finding({(0, 0), (0, 3), (0, 5)}, {1, 2, 3}), pMatrix)
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1), (0, 2), (0, 4)}, {4, 5, 6}), result)
		pass

	def testFindNakedTrippleIn2ndLine(self):
		grid = Grid(2, 3, 1, 1)
		pMatrix = PossibilityMatrix([[{1, 4}, {2, 3}, {1, 3}], [{4, 5}, {5, 6}, {4, 6}]])
		self.finder = NakedFinder(3, grid.gridRow, KnownResultTypeOne())		
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0), (1, 1), (1, 2)}, {4, 5, 6}), result)
		pass

class TestHiddenSingleFinder(unittest.TestCase):

	def testFindNoHiddenSingle(self):
		grid = GridRow(1, 2)
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 1}]])
		self.finder = HiddenFinder(1, grid, KnownResultTypeOne())
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)		
		pass

	def testFind2ndHiddenSingleWhen1stSingleHasBeenUpdated(self):
		grid = GridRow(1, 3)
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 3}, {2, 3, 4}]])
		self.finder = HiddenFinder(1, grid, KnownResultTypeOne())
		self.finder.update(Finding({(0, 0)}, {1}), pMatrix)
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 2)}, {4}), result)
		pass

	def testFindHiddenSingleIn2ndRow(self):
		grid = GridRow(2, 2)
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}], [{3, 4, 1}, {4, 1}]])
		self.finder = HiddenFinder(1, grid, KnownResultTypeOne())
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0)}, {3}), result)		
		pass

class TestHiddenPairFinder(unittest.TestCase):

	def test_findNoHiddenPair(self):
		grid = GridRow(1, 3)
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}, {1, 2}]])
		self.finder = HiddenFinder(2, grid, KnownResultTypeOne())
		self.assertEquals(None, self.finder.find(pMatrix))
		pass

	def test_findHiddenPairInARowOnlyOnce(self):
		grid = GridRow(1, 4)
		pMatrix = PossibilityMatrix([[{1, 2, 5}, {3, 4, 6}, {1, 2, 6}, {3, 4, 5}]])
		self.finder = HiddenFinder(2, grid, KnownResultTypeOne())
		self.finder.update(Finding({(0, 0), (0, 2)}, {1, 2}), pMatrix)
		self.assertEquals(Finding({(0, 1), (0, 3)}, {3, 4}), self.finder.find(pMatrix))		
		pass

	def test_findHiddenPairIn2ndRow(self):
		grid = GridRow(2, 3)
		pMatrix = PossibilityMatrix([[{1, 2, 4}, {1, 2, 4}, {1, 2, 7}], [{3, 4, 5}, {3, 4}, {5, 6}]])
		self.finder = HiddenFinder(2, grid, KnownResultTypeOne())
		self.assertEquals(Finding({(1, 0), (1, 1)}, {3, 4}), self.finder.find(pMatrix))		
		pass

class TestHiddenTripple(unittest.TestCase):

	def testFindNoHiddenTripple(self):
		grid = GridRow(1, 4)
		pMatrix = PossibilityMatrix([[{1, 2, 3}, {1, 2, 3}, {1, 2, 3}, {1, 2, 3}]])
		self.finder = HiddenFinder(3, grid, KnownResultTypeOne())
		self.assertEquals(None, self.finder.find(pMatrix))		
		pass

	def testFind2ndHiddenTrippleAfter1stHasBeenUpdated(self):
		grid = GridRow(1, 7)
		pMatrix = PossibilityMatrix([[{1, 2, 3}, {1, 2, 3}, {4, 5, 7, 8}, {5, 6, 7, 8}, {1, 2, 3}, {4, 6, 7, 8}, {7, 8}]])
		self.finder = HiddenFinder(3, grid, KnownResultTypeOne())
		self.finder.update(Finding({(0, 0), (0, 1), (0, 4)}, {1, 2, 3}), pMatrix)
		self.assertEquals(Finding({(0, 2), (0, 3), (0, 5)}, {4, 5, 6}), self.finder.find(pMatrix))		
		pass

	def testFindHiddenTrippleIn2ndRow(self):
		grid = GridRow(2, 4)
		pMatrix = PossibilityMatrix([[{1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}], 
			                         [{1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}, {4, 5}]])
		self.finder = HiddenFinder(3, grid, KnownResultTypeOne())
		self.assertEquals(Finding({(1, 0), (1, 1), (1, 2)}, {1, 2, 3}), self.finder.find(pMatrix))		
		pass		

class TestLockedCellFinder(unittest.TestCase):
	def testFindLockedCellFromARow(self):
		grid = Grid(2, 4, 2, 2)
		pMatrix = PossibilityMatrix([[{1}, {1}, {2, 3, 4}, {3, 4, 5}],
									 [{1, 2}, {1, 3}, {4, 5, 6}, {5, 6, 7}]])
		finder = LockedCellFinder(grid.gridRow, grid.gridBlock, KnownResultTypeOne())
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

	def testAllPositions(self):
		pMatrix = PossibilityMatrix([[{1}, {1}], [{1}, {1}]])
		self.assertEquals([(0, 0), (0, 1), (1, 0), (1, 1)], pMatrix.allPositions())
		pass

	def testAllPossibilities(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 3}], [{3, 4}, {4, 1}]])
		self.assertEquals({1, 2, 3, 4}, pMatrix.allPossibilities())
		pass

	def testPositions(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 3}], [{3, 4}, {4, 1}]])
		self.assertEquals([(0, 0), (1, 1)], pMatrix.positionsOfValue(1))		
		pass

	def testMatrixObserver(self):
		observer = MockObject()
		observer.update = MagicMock()
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}]])
		pMatrix.register(observer)
		pMatrix.set({3, 4}, 0, 0)
		observer.update.assert_called_once_with({1, 2}, {3, 4}, 0, 0)
		pass

class TestNakedFinderUpdateItsResult(unittest.TestCase):
	def testNakedFinderUpdateInRow(self):
		pMatrix = MockObject()
		pMatrix.erasePossibility = MagicMock()
		knownResult = KnownResultTypeOne()

		finding = Finding({(0, 0), (0, 1)}, {1, 2})
		finder = NakedFinder(1, GridRow(1, 3), knownResult)
		finder.update(finding, pMatrix)

		pMatrix.erasePossibility.assert_called_once_with({1, 2}, {(0, 2)})
		self.assertFalse(knownResult.isNewResult(finding))
		pass
	pass

class TestHiddenFinderUpdateItsResult(unittest.TestCase):
	def testHiddenFinderUpdateInRow(self):
		pMatrix = MockObject()
		pMatrix.setPossibility = MagicMock()
		knownResult = KnownResultTypeOne()

		finding = Finding({(0, 0), (0, 1)}, {1, 2})
		finder = HiddenFinder(1, GridRow(1, 3), knownResult)
		finder.update(finding, pMatrix)

		pMatrix.setPossibility.assert_called_once_with({1, 2}, {(0, 0), (0, 1)})
		self.assertFalse(knownResult.isNewResult(finding))	
		pass
	pass

class TestLockedCellFinderUpdate(unittest.TestCase):
	def testLockedCellFinderUpdate(self):
		pMatrix = MockObject()
		pMatrix.erasePossibility = MagicMock()
		knownResult = KnownResultTypeOne()

		finding = Finding({(0, 0), (0, 1)}, {1})

		gridRow = GridRow(4, 4)
		gridBlock = GridBlock(4, 4, 2, 2)
		finder = LockedCellFinder(gridRow, gridBlock, knownResult)
		finder.update(finding, pMatrix)

		pMatrix.erasePossibility.assert_called_once_with({1}, {(1, 0), (1, 1)})
		self.assertFalse(knownResult.isNewResult(finding))
		pass

class TestXWingFinder(unittest.TestCase):
	def testFindNoXWing(self):
		searchingDirection = GridRow(1, 1)
		impactedDirection = GridColumn(1, 1)
		finder = XWingFinder(2, searchingDirection, impactedDirection, [])
		pMatrix = PossibilityMatrix([[{1}]])
		self.assertEquals(None, finder.find(pMatrix))
		pass

	def testFind2ndXWing(self):
		searchingDirection = GridRow(3, 4)
		impactedDirection = GridColumn(3, 4)

		finder = XWingFinder(2, searchingDirection, impactedDirection, KnownResultTypeOne())
		pMatrix = PossibilityMatrix([[{1, 2, 3, 4}, {1, 2, 3, 4}, {6, 2, 3, 4}, {6, 2, 3, 4}],
									 [{1, 2, 3, 4}, {1, 2, 3, 4}, {4, 2, 3}, {2, 3, 4}],
									 [{7, 8, 9}, {7, 8, 9}, {6, 8}, {6, 2}]]);

		finder.update([Finding({(0, 0), (1, 0)}, {1}), Finding({(0, 1), (1, 1)}, {1})], pMatrix)
		finding = finder.find(pMatrix)
		self.assertEquals([Finding({(0, 2), (2, 2)}, {6}), Finding({(0, 3), (2, 3)}, {6})], finding)
		pass

	def testXWingFinderUpdate(self):
		pMatrix = MockObject()
		pMatrix.erasePossibility = MagicMock()

		searchingDirection = GridRow(3, 4)
		impactedDirection = GridColumn(3, 4)
		knownResult = KnownResultTypeOne()

		finder = XWingFinder(2, searchingDirection, impactedDirection, knownResult)

		finder.update([Finding({(0, 0), (1, 0)}, {1}), Finding({(0, 1), (1, 1)}, {1})], pMatrix)

		self.assertEquals([call({1}, {(2, 0)}), call({1}, {(2, 1)})], pMatrix.erasePossibility.mock_calls)
		self.assertFalse(knownResult.isNewResult(Finding({(0, 0), (1, 0)}, {1})))
		self.assertFalse(knownResult.isNewResult(Finding({(0, 1), (1, 1)}, {1})))
		pass
	pass

class TestKnownResult(unittest.TestCase):
	def setUp(self):
		self.knownResult = KnownResultTypeOne()
		pass
	def testAnyFindingIsNewFindingAfterKnownResultCreation(self):
		self.assertTrue(self.knownResult.isNewResult(Finding({(0, 0)}, {1})))
		pass

	def testFindingBecomesKnown_AKA_NotNew_afterItsAddInKnownResult(self):
		self.knownResult.add(Finding({(0, 0)}, {1}))
		self.assertFalse(self.knownResult.isNewResult(Finding({(0, 0)}, {1})))
		pass

	def testFindPairFirstWillNotImpactFindNewSingleLater(self):
		self.knownResult.add(Finding({(0, 0), (0, 1)}, {1, 2}))
		self.assertTrue(self.knownResult.isNewResult(Finding({(0, 0)}, {1})))
		pass

	def testFindSingleFirstWillImpactFindNewPair(self):
		self.knownResult.add(Finding({(0, 0)}, {1}))
		self.assertFalse(self.knownResult.isNewResult(Finding({(0, 0), (0, 1)}, {1, 2})))
		pass

	def testFindPairFirstAndThenFindSingle(self):
		self.knownResult.add(Finding({(0, 0), (0, 1)}, {1, 2}))
		self.knownResult.add(Finding({(0, 0)}, {1}))
		self.assertFalse(self.knownResult.isNewResult(Finding({(0, 0), (0, 1)}, {1, 2})))
		self.assertFalse(self.knownResult.isNewResult(Finding({(0, 0)}, {1})))
		pass
	pass
		
class TestFinding(unittest.TestCase):
	def testFindingAdd(self):
		f1 = Finding({(0, 0)}, {1})
		f2 = Finding({(0, 1)}, {2})
		self.assertEquals(Finding({(0, 0), (0, 1)}, {1, 2}), f1 + f2)
		pass
	pass

class TestMatrixUpdateObserver(unittest.TestCase):
	def testAfterCreationItObservesNoChange(self):
		observer = PossibilityMatrixUpdateObserver()
		self.assertFalse(observer.isMatrixChanged())
		pass

	def testObservesChange(self):
		observer = PossibilityMatrixUpdateObserver()
		observer.update({1}, {2}, 0, 0)
		self.assertTrue(observer.isMatrixChanged())
		pass

	def testClearObservasions(self):
		observer = PossibilityMatrixUpdateObserver()
		observer.update({1}, {2}, 0, 0)
		observer.clear()
		self.assertFalse(observer.isMatrixChanged())
		pass

	def testObserveNonEffectiveChange(self):
		observer = PossibilityMatrixUpdateObserver()
		observer.update({1}, {1}, 0, 0)
		self.assertFalse(observer.isMatrixChanged())		
		pass

class TestFindAndUpdate(unittest.TestCase):
	def testFindNothing(self):
		pMatrix = MockObject()
		finder = Finder()
		finder.find = MagicMock(return_value = None)
		self.assertFalse(finder.findAndUpdate(pMatrix))
		pass

	def testFindTwoFinding(self):
		pMatrix = MockObject()
		finding1 = MockObject()
		finding2 = MockObject()
		finder = Finder()
		finder.update = MagicMock()
		finder.find = MagicMock(side_effect = [finding1, finding2, None])
		self.assertTrue(finder.findAndUpdate(pMatrix))
		self.assertEquals([call(pMatrix), call(pMatrix), call(pMatrix)], finder.find.mock_calls)
		self.assertEquals([call(finding1, pMatrix), call(finding2, pMatrix)], finder.update.mock_calls)
		pass

class TestScorer(unittest.TestCase):
	def testScoreerCreation(self):
		ranking = Scorer()
		self.assertEquals(0, ranking.result())
		pass

	def testRecordScoreForPairTripleQuat(self):
		ranking = Scorer()
		ranking.recordPairTripleQuat(2)
		self.assertEquals(1, ranking.result())
		pass

	def testRecordHighestScore(self):
		ranking = Scorer()
		ranking.recordPairTripleQuat(3)
		ranking.recordPairTripleQuat(2)
		self.assertEquals(2, ranking.result())
		pass

	def testRecordLockCandidates(self):
		ranking = Scorer()
		ranking.recordLockedCandidates()
		self.assertEquals(1, ranking.result())
		pass

	def testRecordXWingJellyFishSwordFish(self):
		ranking = Scorer()
		ranking.recordXWingJellyFishSwordFish(2)
		self.assertEquals(2, ranking.result())
		pass


	def testNakedFinderScore(self):
		ranking = MockObject()
		ranking.recordPairTripleQuat = MagicMock()
		finder = NakedFinder(1, GridRow(1, 1), KnownResultTypeOne())
		finder.score(ranking)
		ranking.recordPairTripleQuat.assert_called_once_with(1)
		pass

	def testHiddenFinderScore(self):
		ranking = MockObject()
		ranking.recordPairTripleQuat = MagicMock()
		finder = HiddenFinder(1, GridRow(1, 1), KnownResultTypeOne())
		finder.score(ranking)
		ranking.recordPairTripleQuat.assert_called_once_with(1)
		pass

	def testLockCandidatesScore(self):
		ranking = MockObject()
		ranking.recordLockedCandidates = MagicMock()
		finder = LockedCellFinder(GridRow(1, 1), GridBlock(1, 1, 1, 1), KnownResultTypeOne())
		finder.score(ranking)
		ranking.recordLockedCandidates.assert_called_once_with()
		pass

	def testXWingJellyFishSwordFishScore(self):
		ranking = MockObject()
		ranking.recordXWingJellyFishSwordFish = MagicMock()
		finder = XWingFinder(2, GridRow(1, 1), GridColumn(1, 1), KnownResultTypeOne())
		finder.score(ranking)
		ranking.recordXWingJellyFishSwordFish.assert_called_once_with(2)
		pass
	pass

class TestHumanSolver(unittest.TestCase):
	def setUp(self):
		self.grid = Grid(2, 2, 1, 1)
		pass

	def testBuildPossibilityMatrix(self):
		puzzle = Puzzle(PuzzleMatrix([[1, 2],
									  [_, _]]), 
						self.grid,
						Validator(),
						CandidatesGen([1, 2, 3]))		
		hs = HumanSolver(self.grid)
		pMatrix = hs.buildPossibilityMatrix(puzzle)
		self.assertEquals({1}, pMatrix.possibilitieAt((0, 0)))
		self.assertEquals({2}, pMatrix.possibilitieAt((0, 1)))
		self.assertEquals({2, 3}, pMatrix.possibilitieAt((1, 0)))
		self.assertEquals({1, 3}, pMatrix.possibilitieAt((1, 1)))
		pass

	def testBuildKnownResults(self):
		puzzle = Puzzle(PuzzleMatrix([[1, 2],
									  [_, _]]), 
						self.grid,
						Validator(),
						CandidatesGen([1, 2]))		
		hs = HumanSolver(self.grid)
		hs.buildKnownResults(puzzle)
		self.assertFalse(hs.knownResultInRow.isNewResult(Finding({(0, 0)}, {1})))
		self.assertFalse(hs.knownResultInColumn.isNewResult(Finding({(0, 1)}, {2})))
		self.assertTrue(hs.knownResultInBlock.isNewResult(Finding({(1, 0)}, {2})))
		self.assertTrue(hs.knownResultInRow.isNewResult(Finding({(1, 1)}, {1})))
		pass

	def testSolve(self):
		puzzle = Puzzle(PuzzleMatrix([[1, _],
									  [_, _]]), 
						Grid(2, 2, 1, 1),
						Validator(),
						CandidatesGen([1, 2]))		
		hs = HumanSolver(self.grid)		
		hs.solve(puzzle)
		# self.assertFalse(True)
		pass
		