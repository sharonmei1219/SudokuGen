import unittest
from unittest.mock import MagicMock
from unittest.mock import ANY
from unittest.mock import call
from humanSolver import *
from puzzle import *
from puzzle import _
import json

class MockObject:
	pass

class TestNakedSingleFinder(unittest.TestCase):

	def testFindNoNakedSingle(self):
		grid = GridRow(1, 1)
		pMatrix = PossibilityMatrix([[{1, 2}]])
		self.finder = NakedFinder(1, grid)		
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)
		pass

	def testFindNakedSingleIn2ndRow(self):
		grid = GridRow(2, 1)
		pMatrix = FinderContext([[{1, 2}], [{1}]], [])
		self.finder = NakedFinder(1, grid)
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0)}, {1}), result)
		pass

	def testFind2ndNakedSingleAfter1stSingleHasBeenUpdated(self):
		grid = GridRow(1, 2)
		pMatrix = FinderContext([[{1}, {2}]], [])
		self.finder = NakedFinder(1, grid)
		pMatrix.addKnownFinding(grid.zoneObjWithPosIn((0, 0)).id(), Finding({(0, 0)}, {1}))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1)}, {2}), result)
		pass

class TestNakedPairFinder(unittest.TestCase):
	def testFindNoNakedPairInRow(self):
		grid = GridRow(1, 2)
		pMatrix = PossibilityMatrix([[{1}, {2, 3}]])
		self.finder = NakedFinder(2, grid)
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)
		pass

	def testFind2ndNakedPairInRowAfter1stPairHasBeenUpdated(self):
		grid = GridRow(1, 4)		
		pMatrix = FinderContext([[{2, 3}, {4, 5}, {4, 5}, {2, 3}]], [])
		self.finder = NakedFinder(2, grid)
		pMatrix.addKnownFinding(grid.zoneObjWithPosIn((0, 3)).id(), Finding({(0, 3), (0, 0)}, {2, 3}))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1), (0, 2)}, {4, 5}), result)			
		pass

	def testFind2SingleAsOnePair(self):
		grid = GridRow(1, 4)
		pMatrix = FinderContext([[{2}, {3}, {4, 5}, {4, 5}]], [])
		pMatrix.addKnownFinding(grid.zoneObjWithPosIn((0, 0)).id(), Finding({(0, 0)}, {2}))
		pMatrix.addKnownFinding(grid.zoneObjWithPosIn((0, 0)).id(), Finding({(0, 1)}, {3}))
		self.finder = NakedFinder(2, grid)	
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 2), (0, 3)}, {4, 5}), result)			
		pass

	def testFindNakedPairIn2ndRow(self):
		grid = GridRow(2, 2)		
		pMatrix = FinderContext([[{2, 3, 4}, {2, 3, 5}], [{1, 4}, {1, 4}]], [])
		self.finder = NakedFinder(2, grid)
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0), (1, 1)}, {1, 4}), result)			
		pass		

class TestNakedTrippleFinder(unittest.TestCase):
	def testFind2ndNakedTrippleAfter1stHasBeenUpdated(self):
		grid = Grid(1, 6, 1, 1)
		pMatrix = FinderContext([[{1, 2}, {4, 5}, {5, 6}, {2, 3}, {4, 6}, {1, 3}]], [])
		self.finder = NakedFinder(3, grid.gridRow)
		pMatrix.addKnownFinding(grid.gridRow.zoneObjWithPosIn((0, 0)).id(), Finding({(0, 0), (0, 3), (0, 5)}, {1, 2, 3}))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 1), (0, 2), (0, 4)}, {4, 5, 6}), result)
		pass

	def testFindNakedTrippleIn2ndLine(self):
		grid = Grid(2, 3, 1, 1)
		pMatrix = FinderContext([[{1, 4}, {2, 3}, {1, 3}], [{4, 5}, {5, 6}, {4, 6}]], [])
		self.finder = NakedFinder(3, grid.gridRow)		
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0), (1, 1), (1, 2)}, {4, 5, 6}), result)
		pass

class TestHiddenSingleFinder(unittest.TestCase):

	def testFindNoHiddenSingle(self):
		grid = GridRow(1, 2)
		pMatrix = PossibilityMatrix([[{1, 2}, {2, 1}]])
		self.finder = HiddenFinder(1, grid)
		result = self.finder.find(pMatrix)
		self.assertEquals(None, result)		
		pass

	def testFind2ndHiddenSingleWhen1stSingleHasBeenUpdated(self):
		grid = GridRow(1, 3)
		pMatrix = FinderContext([[{1, 2}, {2, 3}, {2, 3, 4}]], [])
		self.finder = HiddenFinder(1, grid)
		pMatrix.addKnownFinding(grid.zoneObjWithPosIn((0, 0)).id(), Finding({(0, 0)}, {1}))
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(0, 2)}, {4}), result)
		pass

	def testFindHiddenSingleIn2ndRow(self):
		grid = GridRow(2, 2)
		pMatrix = FinderContext([[{1, 2}, {1, 2}], [{3, 4, 1}, {4, 1}]], [])
		self.finder = HiddenFinder(1, grid)
		result = self.finder.find(pMatrix)
		self.assertEquals(Finding({(1, 0)}, {3}), result)		
		pass

class TestHiddenPairFinder(unittest.TestCase):

	def test_findNoHiddenPair(self):
		grid = GridRow(1, 3)
		pMatrix = PossibilityMatrix([[{1, 2}, {1, 2}, {1, 2}]])
		self.finder = HiddenFinder(2, grid)
		self.assertEquals(None, self.finder.find(pMatrix))
		pass

	def test_findHiddenPairInARowOnlyOnce(self):
		grid = GridRow(1, 4)
		pMatrix = FinderContext([[{1, 2, 5}, {3, 4, 6}, {1, 2, 6}, {3, 4, 5}]], [])
		self.finder = HiddenFinder(2, grid)
		pMatrix.addKnownFinding(grid.zoneObjWithPosIn((0, 0)).id(), Finding({(0, 0), (0, 2)}, {1, 2}))
		self.assertEquals(Finding({(0, 1), (0, 3)}, {3, 4}), self.finder.find(pMatrix))		
		pass

	def test_findHiddenPairIn2ndRow(self):
		grid = GridRow(2, 3)
		pMatrix = FinderContext([[{1, 2, 4}, {1, 2, 4}, {1, 2, 7}], [{3, 4, 5}, {3, 4}, {5, 6}]], [])
		self.finder = HiddenFinder(2, grid)
		self.assertEquals(Finding({(1, 0), (1, 1)}, {3, 4}), self.finder.find(pMatrix))		
		pass

class TestHiddenTripple(unittest.TestCase):

	def testFindNoHiddenTripple(self):
		grid = GridRow(1, 4)
		pMatrix = PossibilityMatrix([[{1, 2, 3}, {1, 2, 3}, {1, 2, 3}, {1, 2, 3}]])
		self.finder = HiddenFinder(3, grid)
		self.assertEquals(None, self.finder.find(pMatrix))		
		pass

	def testFind2ndHiddenTrippleAfter1stHasBeenUpdated(self):
		grid = GridRow(1, 7)
		pMatrix = FinderContext([[{1, 2, 3}, {1, 2, 3}, {4, 5, 7, 8}, {5, 6, 7, 8}, {1, 2, 3}, {4, 6, 7, 8}, {7, 8}]], [])
		self.finder = HiddenFinder(3, grid)
		pMatrix.addKnownFinding(grid.zoneObjWithPosIn((0, 0)).id(), Finding({(0, 0), (0, 1), (0, 4)}, {1, 2, 3}))
		self.assertEquals(Finding({(0, 2), (0, 3), (0, 5)}, {4, 5, 6}), self.finder.find(pMatrix))		
		pass

	def testFindHiddenTrippleIn2ndRow(self):
		grid = GridRow(2, 4)
		pMatrix = FinderContext([[{1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}], 
			                         [{1, 2, 3, 4}, {1, 2, 3, 4}, {1, 2, 3, 4}, {4, 5}]], [])
		self.finder = HiddenFinder(3, grid)
		self.assertEquals(Finding({(1, 0), (1, 1), (1, 2)}, {1, 2, 3}), self.finder.find(pMatrix))		
		pass		

class TestLockedCellFinder(unittest.TestCase):
	def testFindLockedCellFromARow(self):
		grid = Grid(2, 4, 2, 2)
		pMatrix = FinderContext([[{1}, {1}, {2, 3, 4}, {3, 4, 5}],
									 [{1, 2}, {1, 3}, {4, 5, 6}, {5, 6, 7}]], [])
		finder = LockedCellFinder(grid.gridRow, grid.gridBlock)
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

	def testMostUncertainPosWithAllPosesDetermined(self):
		pMatrix = PossibilityMatrix([[{1}, {2}], [{3}, {4}]])
		self.assertEquals([], pMatrix.mostUncertainPoses())
		pass	

	def testMostUncertainPosWithOnePosHas2PossibilitiesAndRestDetermined(self):
		pMatrix = PossibilityMatrix([[{1, 2}, {2}], [{3}, {4}]])
		self.assertEquals([(0, 0)], pMatrix.mostUncertainPoses())
		pass

class TestNakedFinderUpdateItsResult(unittest.TestCase):

	def testNakedFinderConstructUpdator(self):
		finding = Finding({(0, 0), (0, 1)}, {1, 2})
		finder = NakedFinder(1, GridRow(1, 3))
		updator = finder.constructUpdator(finding)

		pMatrix = MockObject()
		pMatrix.erasePossibility = MagicMock()
		pMatrix.addKnownFinding = MagicMock()

		updator.update(pMatrix)

		pMatrix.erasePossibility.assert_called_once_with({1, 2}, {(0, 2)})
		pMatrix.addKnownFinding.assert_called_once_with('GridRow_0', finding)
		pass
	pass

class TestHiddenFinderUpdateItsResult(unittest.TestCase):

	def testHiddenFinderConstructUpdator(self):
		finding = Finding({(0, 0), (0, 1)}, {1, 2})
		finder = HiddenFinder(1, GridRow(1, 3))
		updator = finder.constructUpdator(finding)

		pMatrix = MockObject()
		pMatrix.setPossibility = MagicMock()
		pMatrix.addKnownFinding = MagicMock()

		updator.update(pMatrix)

		pMatrix.setPossibility.assert_called_once_with({1, 2}, {(0, 0), (0, 1)})
		pMatrix.addKnownFinding.assert_called_once_with('GridRow_0', finding)
		pass
	pass

class TestLockedCellFinderUpdate(unittest.TestCase):

	def testLockedCandidatesConstructUpdator(self):
		pMatrix = MockObject()
		pMatrix.erasePossibility = MagicMock()
		pMatrix.addKnownFinding = MagicMock()

		finding = Finding({(0, 0), (0, 1)}, {1})
		gridRow = GridRow(4, 4)
		gridBlock = GridBlock(4, 4, 2, 2)
		finder = LockedCellFinder(gridRow, gridBlock)
		
		updator = finder.constructUpdator(finding)

		updator.update(pMatrix)

		pMatrix.erasePossibility.assert_called_once_with({1}, {(1,0), (1,1)})
		pMatrix.addKnownFinding.assert_called_once_with('GridBlock_0', finding)
		pass

class TestXWingFinder(unittest.TestCase):
	def testFindNoXWing(self):
		searchingDirection = GridRow(1, 1)
		impactedDirection = GridColumn(1, 1)
		finder = XWingFinder(2, searchingDirection, impactedDirection)
		pMatrix = PossibilityMatrix([[{1}]])
		self.assertEquals(None, finder.find(pMatrix))
		pass

	def testFind2ndXWing(self):
		searchingDirection = GridRow(3, 4)
		impactedDirection = GridColumn(3, 4)

		finder = XWingFinder(2, searchingDirection, impactedDirection)
		pMatrix = FinderContext([[{1, 2, 3, 4}, {1, 2, 3, 4}, {6, 2, 3, 4}, {6, 2, 3, 4}],
								 [{1, 2, 3, 4}, {1, 2, 3, 4}, {4, 2, 3}, {2, 3, 4}],
								 [{7, 8, 9}, {7, 8, 9}, {6, 8}, {6, 2}]], []);

		pMatrix.addKnownFinding(impactedDirection.zoneObjWithPosIn((0, 0)).id(), Finding({(0, 0), (1, 0)}, {1}))
		pMatrix.addKnownFinding(impactedDirection.zoneObjWithPosIn((0, 1)).id(), Finding({(0, 1), (1, 1)}, {1}))
		finding = finder.find(pMatrix)
		self.assertEquals([Finding({(0, 2), (2, 2)}, {6}), Finding({(0, 3), (2, 3)}, {6})], finding)
		pass

	def testXWingConstructUpdator(self):
		pMatrix = MockObject()
		pMatrix.erasePossibility = MagicMock()
		pMatrix.addKnownFinding = MagicMock()

		searchingDirection = GridRow(3, 4)
		impactedDirection = GridColumn(3, 4)
		findings = [Finding({(0, 0), (1, 0)}, {1}), Finding({(0, 1), (1, 1)}, {1})]
		finder = XWingFinder(2, searchingDirection, impactedDirection)

		updator = finder.constructUpdator(findings)
		updator.update(pMatrix)
		self.assertEquals([call({1}, {(2, 0)}), call({1}, {(2, 1)})], pMatrix.erasePossibility.mock_calls)
		self.assertEquals([call('GridColumn_0', Finding({(0, 0), (1, 0)}, {1})), call('GridColumn_1', Finding({(0, 1), (1, 1)}, {1}))], pMatrix.addKnownFinding.mock_calls)
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

	def testFinderFindUpdator(self):
		pMatrix = MockObject()
		finding = MockObject()
		updator = MockObject()
		finder = Finder()
		finder.find = MagicMock(return_value = finding)
		finder.constructUpdator = MagicMock(return_value = updator)

		self.assertEquals(updator, finder.findUpdator(pMatrix))

		finder.find.assert_called_once_with(pMatrix)
		finder.constructUpdator.assert_called_once_with(finding)
		pass

	def testFinderFindUpdatorNothingFind(self):
		pMatrix = MockObject()
		finder = Finder()
		finder.find = MagicMock(return_value = None)
		self.assertEquals(None, finder.findUpdator(pMatrix))
		finder.find.assert_called_once_with(pMatrix)
		pass

class TestScorer(unittest.TestCase):
	def testScoreerCreation(self):
		ranking = Scorer()
		self.assertEquals(0, ranking.result())
		pass

	def testRecordScoreForPairTripleQuat(self):
		ranking = Scorer()
		ranking.visitNakedFinder(2)
		self.assertEquals(1, ranking.result())
		pass

	def testRecordHighestScore(self):
		ranking = Scorer()
		ranking.visitHiddenFinder(3)
		ranking.visitNakedFinder(2)
		self.assertEquals(2, ranking.result())
		pass

	def testRecordLockCandidates(self):
		ranking = Scorer()
		ranking.visitLockedCandidates()
		self.assertEquals(1, ranking.result())
		pass

	def testRecordXWingJellyFishSwordFish(self):
		ranking = Scorer()
		ranking.visitXWingJellyFishSwordFish(2)
		self.assertEquals(2, ranking.result())
		pass


	def testNakedFinderScore(self):
		ranking = MockObject()
		ranking.visitNakedFinder = MagicMock()
		finder = NakedFinder(1, GridRow(1, 1))
		finder.accept(ranking)
		ranking.visitNakedFinder.assert_called_once_with(1)
		pass

	def testHiddenFinderScore(self):
		ranking = MockObject()
		ranking.visitHiddenFinder = MagicMock()
		finder = HiddenFinder(1, GridRow(1, 1))
		finder.accept(ranking)
		ranking.visitHiddenFinder.assert_called_once_with(1)
		pass

	def testLockCandidatesScore(self):
		ranking = MockObject()
		ranking.visitLockedCandidates = MagicMock()
		finder = LockedCellFinder(GridRow(1, 1), GridBlock(1, 1, 1, 1))
		finder.accept(ranking)
		ranking.visitLockedCandidates.assert_called_once_with()
		pass

	def testXWingJellyFishSwordFishScore(self):
		ranking = MockObject()
		ranking.visitXWingJellyFishSwordFish = MagicMock()
		finder = XWingFinder(2, GridRow(1, 1), GridColumn(1, 1))
		finder.accept(ranking)
		ranking.visitXWingJellyFishSwordFish.assert_called_once_with(2)
		pass
	pass

class TestHumanSolver(unittest.TestCase):
	def setUp(self):
		self.grid = Grid(2, 2, 1, 1)
		pass

	def testSolveNewVersion(self):
		puzzle = Puzzle(PuzzleMatrix([[1, _],
									  [_, _]]), 
						Grid(2, 2, 1, 1),
						Validator(),
						CandidatesGen([1, 2]))		
		hs = HumanSolver(self.grid)		
		context = hs.solve(puzzle)
		self.assertEquals([[{1}, {2}], [{2}, {1}]], context.matrix)
		pass

	def testHint(self):
		puzzle = Puzzle(PuzzleMatrix([[1, _],
									  [_, _]]), 
						Grid(2, 2, 1, 1),
						Validator(),
						CandidatesGen([1, 2]))		
		hs = HumanSolver(self.grid)		
		result = hs.hint(puzzle)
		# print(result[0][0])
		# self.assertFalse(True)
		pass

class TestSelfUpdateFinding(unittest.TestCase):
	def testExclusiveUpdatorUpdateMatrix(self):
		pMatrix = MockObject()
		pMatrix.erasePossibility = MagicMock()
		pMatrix.addKnownFinding = MagicMock()
		finding = Finding({(0, 0)}, {1})
		updator = ExclusiveUpdater(finding, Zone('GridRow_0', ((0, 0), (0, 1))))
		updator.update(pMatrix)
		pMatrix.erasePossibility.assert_called_once_with({1}, {(0, 1)})
		pMatrix.addKnownFinding.assert_called_once_with('GridRow_0', finding)

	def testOccupationUpdatorUpdateMatrix(self):
		pMatrix = MockObject()
		pMatrix.setPossibility = MagicMock()
		pMatrix.addKnownFinding = MagicMock()
		finding = Finding({(0, 0), (0, 1)}, {1, 2})
		updator = OccupationUpdator(finding, Zone('GridRow_0', ((0, 0), (0, 1))))
		updator.update(pMatrix)
		pMatrix.setPossibility.assert_called_once_with({1, 2}, {(0, 0), (0, 1)})
		pMatrix.addKnownFinding.assert_called_once_with('GridRow_0', finding)
		pass

	def testComposedUpdator(self):
		pMatrix = MockObject()
		updator_0 = MockObject()
		updator_0.update = MagicMock()
		updator_1 = MockObject()
		updator_1.update = MagicMock()
		composedUpdator = ComposedUpdator([updator_0, updator_1])
		composedUpdator.update(pMatrix)
		updator_1.update.assert_called_once_with(pMatrix)
		updator_0.update.assert_called_once_with(pMatrix)
		pass

class TestKnownFindingMapVersion(unittest.TestCase):

	def testMoreAccurateFindingFoundInTheSameZone(self):
		finding = MockObject()
		newFinding = MockObject()
		finding.moreAccurateThan = MagicMock(return_value = True)
		knownFinding = KnownFinding([])
		knownFinding.hasDetermined = MagicMock(return_value = False)
		knownFinding.addKnownFinding('GridRow_0', finding)
		self.assertTrue(knownFinding.moreAccurateFound('GridRow_0', newFinding))
		pass

	def testOneFindingExistMoreAccurateFindingFoundInTheSameZone(self):
		finding_0 = MockObject()
		finding_1 = MockObject()
		newFinding = MockObject()
		finding_0.moreAccurateThan = MagicMock(return_value = True)
		finding_1.moreAccurateThan = MagicMock(return_value = False)
		knownFinding = KnownFinding([])
		knownFinding.hasDetermined = MagicMock(return_value = False)
		knownFinding.addKnownFinding('GridRow_0', finding_0)
		knownFinding.addKnownFinding('GridRow_0', finding_1)
		self.assertTrue(knownFinding.moreAccurateFound('GridRow_0', newFinding))
		pass

	def testNoFindingExistMoreAccurateFindingFoundInTheSameZone(self):
		finding_0 = MockObject()
		finding_1 = MockObject()
		newFinding = MockObject()
		finding_0.moreAccurateThan = MagicMock(return_value = False)
		finding_1.moreAccurateThan = MagicMock(return_value = False)
		knownFinding = KnownFinding([])
		knownFinding.hasDetermined = MagicMock(return_value = False)
		knownFinding.addKnownFinding('GridRow_0', finding_0)
		knownFinding.addKnownFinding('GridRow_0', finding_1)
		self.assertFalse(knownFinding.moreAccurateFound('GridRow_0', newFinding))
		pass

	def testNewFindingInASeperateZone(self):
		finding_0 = MockObject()
		newFinding = MockObject()
		finding_0.moreAccurateThan = MagicMock(return_value = True)
		knownFinding = KnownFinding([])
		knownFinding.addKnownFinding('GridRow_0', finding_0)
		knownFinding.hasDetermined = MagicMock(return_value = False)
		self.assertFalse(knownFinding.moreAccurateFound('GridRow_1', newFinding))
		pass

class TestSingleFinder(unittest.TestCase):
	def testReturnTrue(self):
		teller = SingleFinderTeller()
		self.assertTrue(teller.tellSingleFinder(NakedFinder(1, GridRow(1, 1))))
		self.assertTrue(teller.tellSingleFinder(HiddenFinder(1, GridRow(1, 1))))
		pass

	def testReturnFalse(self):
		teller = SingleFinderTeller()
		self.assertFalse(teller.tellSingleFinder(NakedFinder(2, GridRow(1, 1))))
		self.assertFalse(teller.tellSingleFinder(HiddenFinder(2, GridRow(1, 1))))
		self.assertFalse(teller.tellSingleFinder(XWingFinder(2, GridRow(1, 1), GridColumn(1, 1))))
		self.assertFalse(teller.tellSingleFinder(LockedCellFinder(GridBlock(1, 1, 1, 1), GridColumn(1, 1))))
		pass

class TestNamer(unittest.TestCase):
	def testNamesOfAllFinder(self):
		name = FinderName()
		self.assertEquals('Naked Single', name.name(NakedFinder(1, None)))
		self.assertEquals('Naked Pair', name.name(NakedFinder(2, None)))
		self.assertEquals('Naked Triple', name.name(NakedFinder(3, None)))
		self.assertEquals('Naked Quat', name.name(NakedFinder(4, None)))
		self.assertEquals('Hidden Single', name.name(HiddenFinder(1, None)))
		self.assertEquals('Hidden Pair', name.name(HiddenFinder(2, None)))
		self.assertEquals('Hidden Triple', name.name(HiddenFinder(3, None)))
		self.assertEquals('Hidden Quat', name.name(HiddenFinder(4, None)))
		self.assertEquals('Locked Candidates', name.name(LockedCellFinder(None, None)))
		self.assertEquals('XWing', name.name(XWingFinder(2, None, None)))
		self.assertEquals('Jelly Fish', name.name(XWingFinder(3, None, None)))
		self.assertEquals('Sword Fish', name.name(XWingFinder(4, None, None)))
		pass

class TestSerialization(unittest.TestCase):
	def setUp(self):
		self.se = Serializor()
		self.zone = Zone('Row_0', {(0, 0)})
		self.finding = Finding({(0, 0)}, {1})

		self.zone_1 = Zone('Row_1', {(1, 0)})
		self.finding_1 = Finding({(1, 0)}, {2})

		pass
	def testSerializeZone(self):
		self.assertEquals([(0, 0)], self.se.serialize(self.zone))

	def testSerializeFinding(self):
		self.assertEquals({'possibilities':[1], 'poses':[(0, 0)]}, self.se.serialize(self.finding))

	def testSerializeExclusiveUpdator(self):
		upd = ExclusiveUpdater(self.finding, self.zone)
		jsonData = self.se.serialize(upd)
		self.assertEquals({'finding':{'possibilities':[1], 'poses':[(0, 0)]}, 'zone':[(0, 0)]}, jsonData)
		pass

	def testSerializeOccupationUpdator(self):
		upd = OccupationUpdator(self.finding, self.zone)
		jsonData = self.se.serialize(upd)
		self.assertEquals({'finding':{'possibilities':[1], 'poses':[(0, 0)]}, 'zone':[(0, 0)]}, jsonData)
		pass

	def testSerializeComposedUpdator(self):
		upd_0 = OccupationUpdator(self.finding, self.zone)
		upd_1 = OccupationUpdator(self.finding_1, self.zone_1)
		upd = ComposedUpdator([upd_0, upd_1])
		jsonData = self.se.serialize(upd)
		self.assertEquals([{'finding':{'possibilities':[1], 'poses':[(0, 0)]}, 'zone':[(0, 0)]},
			               {'finding':{'possibilities':[2], 'poses':[(1, 0)]}, 'zone':[(1, 0)]}], jsonData)
		pass

class testGetHint(unittest.TestCase):
	def setUp(self):
		self.msg = '[["/",1,"/","/","/","/","/",6,"/"],[4,"/","/","/","/","/","/","/",8],[9,"/",8,"/","/","/",5,"/",2],["/","/","/","/",3,"/","/","/","/"],["/","/","/",7,5,"/","/","/","/"],[1,"/",6,"/","/","/","/","/",4],["/","/",4,"/","/",1,9,"/","/"],[6,"/","/",3,"/",2,"/","/","/"],[5,"/",9,"/",6,"/",1,"/","/"]]'
		self.factory = PuzzleFactory(9, 3, 3)
		self.matrix = json.loads(self.msg)
		pass

	def testLoadJsonData(self):
		expectedMatrix = [['/', 1, '/', '/', '/', '/', '/', 6, '/'],
		                  [4, '/', '/', '/', '/', '/', '/', '/', 8],
		                  [9, '/', 8, '/', '/', '/', 5, '/', 2],
		                  ['/', '/', '/', '/', 3, '/', '/', '/', '/'],
					      ['/', '/', '/', 7, 5, '/', '/', '/', '/'],
					      [1, '/', 6, '/', '/', '/', '/', '/', 4],
					      ['/', '/', 4, '/', '/', 1, 9, '/', '/'],
					      [6, '/', '/', 3, '/', 2, '/', '/', '/'],
					      [5, '/', 9, '/', 6, '/', 1, '/', '/']]
		self.assertEquals(expectedMatrix, self.matrix)   
		pass

	def testCreatePuzzle(self):
		puzzle = self.factory.creatPuzzleByMatrix(self.matrix)
		self.assertEquals({2, 3, 7}, puzzle.unknownPart()[(0,0)])
		pass

	def testsolveWithSingleRule(self):
		matrix = [[1, 3, '/', 9, '/', 8, 5, '/', 7],
 				  [8, '/', '/', '/', 3, 5, '/', 1, 9],
 				  ['/', 5, 9, 2, '/', '/', 8, 3, 6],
 				  ['/', '/', 4, 8, '/', '/', 6, 5, 3],
 				  [6, 1, 5, 3, '/', 2, 7, '/', '/'],
 				  [3, '/', 8, '/', 5, 6, '/', '/', 1],
 				  ['/', 6, 7, 1, '/', 9, 3, '/', '/'],
 				  ['/', '/', 3, '/', '/', 4, 1, 6, '/'],
 				  ['/', '/', 1, '/', '/', 3, 9, 7, '/']]
		puzzle = self.factory.creatPuzzleByMatrix(matrix)
		humanSolver = HumanSolver(Grid(9, 9, 3, 3))
		hint = humanSolver.hint(puzzle)
		encoder = HintMessage()
		msg = encoder.getMsg(hint)
		self.assertEquals([{'finder': 'Naked Pair', 'updator': {'finding': {'possibilities': [2, 6], 'poses': [(1, 2), (0, 2)]}, 'zone': [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]}}, {'finder': 'Locked Candidates', 'updator': {'finding': {'possibilities': [2], 'poses': [(3, 0), (3, 1)]}, 'zone': [(3, 0), (3, 1), (3, 2), (4, 0), (4, 1), (4, 2), (5, 0), (5, 1), (5, 2)]}}, {'finder': 'Locked Candidates', 'updator': {'finding': {'possibilities': [2], 'poses': [(8, 8), (7, 8), (6, 8)]}, 'zone': [(6, 6), (6, 7), (6, 8), (7, 6), (7, 7), (7, 8), (8, 6), (8, 7), (8, 8)]}}, {'finder': 'XWing', 'updator': [{'finding': {'possibilities': [7], 'poses': [(5, 1), (1, 1)]}, 'zone': [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1)]}, {'finding': {'possibilities': [7], 'poses': [(1, 3), (5, 3)]}, 'zone': [(0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3)]}]}, {'finder': 'Naked Single', 'updator': {'finding': {'possibilities': [5], 'poses': [(7, 3)]}, 'zone': [(7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7), (7, 8)]}}]
, msg)
		pass
		
	# def testTrickyPuzzle(self):
	# 	matrix = [[ 6 , 5 , 4 , 7 , 3 , 8 , 2 ,"/", 1],
	# 			  [ 3 , 7 , 2 , 9 , 4 , 1 , 5 , 6 , 8],
	# 			  [ 9 , 1 , 8 , 2 , 6 , 5 , 3 , 4 ,"/"],
	# 			  [ 1 , 2 , 3 ,"/", 5 ,"/", 8 , 7 , 9],
	# 			  ["/", 4 , 5 ,"/", 8 , 9 , 6 ,"/", 3],
	# 			  [ 8 , 6 , 9 ,"/", 2 , 7 , 4 , 1 , 5],
	# 			  ["/", 3 ,"/", 6 , 7 , 4 , 9 , 8 , 2],
	# 			  [ 4 , 8 , 7 , 5 , 9 , 2 , 1 , 3 , 6],
	# 			  [ 2 , 9 , 6 ,"/", 1 , 3 , 7 , 5 ,"/"]]
	# 	puzzle = self.factory.creatPuzzleByMatrix(matrix)
	# 	humanSolver = HumanSolver(Grid(9, 9, 3, 3))
	# 	hint = humanSolver.hint(puzzle)
	# 	encoder = HintMessage()
	# 	msg = encoder.getMsg(hint)
	# 	self.assertEquals([], msg)
	# 	pass

	def testPuzzleWithAllSingles(self):
		matrix = [[1, '/'], ['/', 1]]
		factory = PuzzleFactory(2, 1, 1)
		puzzle = factory.creatPuzzleByMatrix(matrix)
		humanSolver = HumanSolver(Grid(2, 2, 1, 1))
		# hint = humanSolver.hint(puzzle)
		pass

	def testBuildKnownResultFromPuzzle(self):
		matrix = [[1, '/'], ['/', 1]]
		factory = PuzzleFactory(2, 1, 1)
		puzzle = factory.creatPuzzleByMatrix(matrix)
		knownPart = puzzle.knownPart()
		knownFinding = KnownFinding(knownPart)
		self.assertTrue(knownFinding.moreAccurateFound('GridRow_0', Finding({(0, 0)}, {1})))
		self.assertFalse(knownFinding.moreAccurateFound('GridRow_0', Finding({(0, 1)}, {2})))
		pass