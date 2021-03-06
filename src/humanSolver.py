import json
from functools import reduce
class HumanSolver:
	def __init__(self, grid):
		self._grid = grid
		self.observer = PossibilityMatrixUpdateObserver()
		self.scorer = Scorer()

		self.directioins = grid.allDirection()
		(self.gridRow, self.gridColumn, self.gridBlock) = (self.directioins)

		self.finders =  self.nakedSingle() \
						+ self.hiddenSingle() \
						+ self.nakedPair() \
						+ self.hiddenPair() \
						+ self.lockedCandidates() \
						+ self.nakedTriple() \
						+ self.hiddenTriple() \
						+ self.XWing() \
						+ self.nakedQuat() \
						+ self.hiddenQuat() \
						+ self.jellyFish() \
						+ self.swordFish()
		pass

	def nakedSingle(self): return  self.nakedRule(1);
	def nakedPair(self): return self.nakedRule(2);
	def nakedTriple(self): return self.nakedRule(3);
	def nakedQuat(self): return self.nakedRule(4);

	def nakedRule(self, length):
		return  [NakedFinder(length, self.gridRow),
				 NakedFinder(length, self.gridColumn),
				 NakedFinder(length, self.gridBlock)]
		pass

	def hiddenSingle(self):	return self.hiddenRule(1);
	def hiddenPair(self): return self.hiddenRule(2);
	def hiddenTriple(self):	return self.hiddenRule(3);
	def hiddenQuat(self): return self.hiddenRule(4);


	def hiddenRule(self, length):
		return [HiddenFinder(length, self.gridRow),
				HiddenFinder(length, self.gridColumn),
				HiddenFinder(length, self.gridBlock)]
		pass

	def lockedCandidates(self):
		return [LockedCellFinder(self.gridRow, self.gridBlock),
				LockedCellFinder(self.gridColumn, self.gridBlock),
				LockedCellFinder(self.gridBlock, self.gridRow),
				LockedCellFinder(self.gridBlock, self.gridColumn)]
		pass

	def XWing(self): return self.crossRule(2)
	def jellyFish(self): return self.crossRule(3)
	def swordFish(self): return self.crossRule(4)

	def crossRule(self, length):
		return [XWingFinder(length, self.gridRow, self.gridColumn),
				XWingFinder(length, self.gridColumn, self.gridRow)]
		pass

	def buildSolvingContextNewVersion(self, puzzle):
		context = FinderContext(puzzle.possibilityMatrix(), puzzle.knownPart())
		context.register(self.observer)
		return context

	def solveWithOnlySingleRule(self, puzzle):
		context = self.buildSolvingContextNewVersion(puzzle)
		finders = self.nakedSingle() + self.hiddenSingle()
		self.solvePuzzleWithinContextWithFinder(context, finders)
		return context

	def solve(self, puzzle):
		context = self.buildSolvingContextNewVersion(puzzle)
		self.solvePuzzleWithinContext(context)
		return context

	def hint(self, puzzle):
		context = self.buildSolvingContextNewVersion(puzzle)
		print('possibilityMatrix')
		print(context.matrix)
		print(context.zoneFindingMap)
		teller = SingleFinderTeller()
		result = []
		while True:
			self.observer.clear()
			updator, finder = self.loopSearch(context, self.finders)
			updator.update(context)
			if self.observer.isMatrixChanged() or teller.tellSingleFinder(finder):
				result += [(updator, finder)]
				if teller.tellSingleFinder(finder):break

		return result

	def loopSearch(self, context, finderList):
		for finder in finderList:
			updator = finder.findUpdator(context)
			if updator != None: return updator, finder
		return None, None

	def solvePuzzleWithinContext(self, context):
		updator, finder = self.loopSearch(context, self.finders)
		while updator != None:
			self.observer.clear()
			updator.update(context)
			if self.observer.isMatrixChanged():
				finder.accept(self.scorer)
			updator, finder = self.loopSearch(context, self.finders)
		pass

	def solvePuzzleWithinContextWithFinder(self, context, finders):
		updator, finder = self.loopSearch(context, finders)
		while updator != None:
			self.observer.clear()
			updator.update(context)
			if self.observer.isMatrixChanged():
				finder.accept(self.scorer)
			updator, finder = self.loopSearch(context, finders)
		pass

	def rank(self):
		return self.scorer.result()

class PossibilityMatrix:
	def __init__(self, matrix):
		self.matrix = matrix
		self.observers = []
		pass

	def possibilitieAt(self, pos):
		return self.matrix[pos[0]][pos[1]]

	def erasePossibility(self, possibilities, poses):
		for (i, j) in poses:
			newPossibility = self.matrix[i][j] - possibilities
			self.set(newPossibility, i, j)
		pass

	def setPossibility(self, possibilities, poses):
		for (i, j) in poses:
			self.set(possibilities, i, j)
		pass

	def set(self, possibilities, i, j):
		self.update(self.matrix[i][j], possibilities, i, j)
		self.matrix[i][j] = possibilities
		pass

	def buildValuePosMapInZone(self, zone):
		valuePosMap = {}
		for pos in zone:
			for  value in self.possibilitieAt(pos):
				if value not in valuePosMap: valuePosMap[value] = set()
				valuePosMap[value] |= {pos}
		return valuePosMap

	def allPositions(self):
		return [(i, j) for i in range(len(self.matrix)) for j in range(len(self.matrix[0]))]

	def allPossibilities(self):
		return set.union(*(set.union(*self.matrix[i]) for i in range(len(self.matrix))))

	def positionsOfValue(self, value):
		return [(i, j) for (i, j) in self.allPositions() if value in self.matrix[i][j]]

	def register(self, observer):
		self.observers.append(observer)
		pass

	def update(self, originPossibilities, updatedPossibilities, i, j):
		for observer in self.observers:
			observer.update(originPossibilities, updatedPossibilities, i, j)
		pass

	def mostUncertainPoses(self):
		theMax = max([len(self.matrix[i][j]) for (i, j) in self.allPositions()])
		if theMax is 1:
			return []
		else:
			posWithMostPossibilities = [(i,j) for (i, j) in self.allPositions() if len(self.matrix[i][j]) == theMax] 
			return posWithMostPossibilities
		pass

class Finding:
	def __init__(self, pos, value):
		self.pos = pos
		self.possibilities = value
		pass

	def __eq__(self, finding):
		return self.pos == finding.pos and self.possibilities == finding.possibilities

	def __str__(self):
		output = {'pos': str(self.pos), 'possibilities': str(self.possibilities)}
		return json.dumps(output)
	
	def __repr__(self):
		return self.__str__()

	def __add__(self, otherFinding):
		return Finding(self.pos | otherFinding.pos, self.possibilities | otherFinding.possibilities)

	def anyPos(self):
		return next(iter(self.pos))

	def moreAccurateThan(self, otherFinding):
		if self.pos < otherFinding.pos: return True
		if self.pos == otherFinding.pos:
			if self.possibilities >= otherFinding.possibilities:
				return True
		return False

	def accept(self, visitor):
		return visitor.visitFinding(self.possibilities, self.pos)

class ExclusiveUpdater:
	def __init__(self, finding, zone):
		self._finding = finding
		self._zone = zone
		pass

	def update(self, context):
		context.erasePossibility(self._finding.possibilities, set(self._zone.poses()) - self._finding.pos)
		context.addKnownFinding(self._zone.id(), self._finding)
		pass

	def __str__(self):
		return str(self._finding) + ', grid: ' + self._zone.id()

	def accept(self, visitor):
		return visitor.visiteExclusiveUpdator(self._finding, self._zone)

class OccupationUpdator:
	def __init__(self, finding, zone):
		self._finding = finding
		self._zone = zone
		pass

	def update(self, context):
		context.setPossibility(self._finding.possibilities, self._finding.pos)
		context.addKnownFinding(self._zone.id(), self._finding)
		pass

	def accept(self, visitor):
		return visitor.visitOccupationUpdator(self._finding, self._zone)

class ComposedUpdator:
	def __init__(self, updators):
		self._upds = updators
		pass

	def update(self, context):
		for updator in self._upds:
			updator.update(context)
		pass

	def accept(self, visitor):
		return visitor.visitComposedUpdator(self._upds)

class Finder:
	def findAndUpdate(self, pMatrix):
		foundSomething = False
		finding = self.find(pMatrix)

		while finding is not None:
			self.update(finding, pMatrix)
			foundSomething = True;
			finding = self.find(pMatrix)
		
		return foundSomething

	def findUpdator(self, pMatrix):
		finding = self.find(pMatrix)
		if finding is None: return None
		return self.constructUpdator(finding)
		
class NakedFinder(Finder):
	def __init__(self, criteria, viewGrid):
		self.criteria = criteria
		self.viewGrid = viewGrid
		pass

	def find(self, pMatrix):
		for zone in self.viewGrid.zones():
			finding = self.iterativelyFind(Finding(set(), set()), zone, 0, pMatrix)
			if finding is not None: return finding
		return None

	def iterativelyFind(self, f1, restPos, nth, pMatrix):
		if nth == self.criteria:
			return f1

		for i in range(len(restPos)):
			pos = restPos[i]
			f2 = Finding({pos}, pMatrix.possibilitieAt(pos))
			if len((f1 + f2).possibilities) > self.criteria : continue

			finding = self.iterativelyFind(f1 + f2,
				                           restPos[i+1:], 
				                           nth + 1, 
				                           pMatrix)
			
			if self.isNewResultFound(finding, pMatrix): return finding
		pass

	def isNewResultFound(self, result, pMatrix):
		return result is not None and (self.isNewResultInContext(result, pMatrix))

	def isNewResultInContext(self, result, pMatrix):
		updator = self.constructUpdator(result)
		zoneID = self.viewGrid.zoneObjWithPosIn(result.anyPos()).id()
		return not pMatrix.moreAccurateFound(zoneID, result)

	def accept(self, scorer):
		return scorer.visitNakedFinder(self.criteria)
		pass

	def constructUpdator(self, finding):
		return ExclusiveUpdater(finding, self.viewGrid.zoneObjWithPosIn(finding.anyPos()))

class HiddenFinder(Finder):
	def __init__(self, criteria, viewDirection):
		self.viewDir = viewDirection
		self.criteria = criteria
		pass

	def find(self, pMatrix):
		for zone in self.viewDir.zones():
			valuePosMap = pMatrix.buildValuePosMapInZone(zone)
			single = self.iterativelyFind(Finding(set(), set()), list(valuePosMap), 0, valuePosMap, pMatrix)
			if single is not None: return single
		pass

	def iterativelyFind(self, f1, restKeys, nth, valuePosMap, pMatrix):	
		if nth == self.criteria:
			finding = f1
			if self.isNewResultFound(finding, pMatrix): return finding

		for i in range(len(restKeys)):
			key = restKeys[i]
			f2 = Finding(valuePosMap[key], {key})
			if len((f1 + f2).pos) > self.criteria: continue
			
			finding = self.iterativelyFind(f1 + f2, 
				                           restKeys[i+1:], 
				                           nth+1,
				                           valuePosMap,
				                           pMatrix)

			if finding is not None: return finding
		pass

	def isNewResultFound(self, result, pMatrix):
		return result is not None and (self.isNewResultInContext(result, pMatrix))

	def isNewResultInContext(self, result, pMatrix):
		updator = self.constructUpdator(result)
		zoneID = self.viewDir.zoneObjWithPosIn(result.anyPos()).id()
		return not pMatrix.moreAccurateFound(zoneID, result)		

	def accept(self, scorer):
		return scorer.visitHiddenFinder(self.criteria)
		pass

	def constructUpdator(self, finding):
		return OccupationUpdator(finding, self.viewDir.zoneObjWithPosIn(finding.anyPos()))

class LockedCellFinder(Finder):
	def __init__(self, sourceViewDir, affectViewDir):
		self.sourceViewDir = sourceViewDir
		self.affectViewDir = affectViewDir
		pass

	def find(self, pMatrix):
		for value in pMatrix.allPossibilities():
			zones = self.sourceViewDir.split(pMatrix.positionsOfValue(value))
			for zone in zones:
				if not self.affectViewDir.posesInSameZone(zone):
					continue
				
				finding = Finding(zone, {value})
				if not self.isNewResultFound(finding, pMatrix):
					continue

				return Finding(zone, {value})				
		pass

	def isNewResultFound(self, result, pMatrix):
		return result is not None and (self.isNewResultInContext(result, pMatrix))

	def isNewResultInContext(self, result, pMatrix):
		updator = self.constructUpdator(result)
		zoneID = self.affectViewDir.zoneObjWithPosIn(result.anyPos()).id()
		return not pMatrix.moreAccurateFound(zoneID, result)		

	def constructUpdator(self, finding):
		return ExclusiveUpdater(finding, self.affectViewDir.zoneObjWithPosIn(finding.anyPos()))

	def accept(self, scorer):
		return scorer.visitLockedCandidates()
		pass

class XWingFinder(Finder):
	def __init__(self, criteria, searchingDirection, impactDirection):
		self.searchingDirection = searchingDirection
		self.impactDirection = impactDirection
		self.criteria = criteria
		pass

	def find(self, pMatrix):
		allPossibilities = pMatrix.allPossibilities()

		for value in allPossibilities:
			poses = pMatrix.positionsOfValue(value)
			areas = self.searchingDirection.split(poses)
			result = self.iterativelyFind(areas, 0, set(), value, 0, pMatrix)
			if result is not None: return result

		return None

	def iterativelyFind(self, areas, startingPoint, mergedArea, value, cnt, pMatrix):
		if cnt == self.criteria:
			splits = self.impactDirection.split(mergedArea)
			return [Finding(split, {value}) for split in splits]

		for j in range(startingPoint, len(areas)):
			splits = self.impactDirection.split(mergedArea | areas[j])
			if len(splits) > self.criteria: continue
			result = self.iterativelyFind(areas, j + 1, mergedArea | areas[j], value, cnt + 1, pMatrix)
			if self.isNewResultFound(result, pMatrix): return result
		pass

	def constructUpdator(self, findings):
		updators = [ExclusiveUpdater(finding, self.impactDirection.zoneObjWithPosIn(finding.anyPos())) for finding in findings]
		return ComposedUpdator(updators)

	def isNewResultFound(self, result, pMatrix):
		return result is not None and (self.isNewResultInContext(result, pMatrix))

	def isNewResultInContext(self, result, pMatrix):
		for r in result:
			zoneID = self.impactDirection.zoneObjWithPosIn(r.anyPos()).id()
			if not pMatrix.moreAccurateFound(zoneID, r): return True
		return False

	def accept(self, scorer):
		return scorer.visitXWingJellyFishSwordFish(self.criteria)

class PossibilityMatrixUpdateObserver:
	def __init__(self):
		self.changed = False
		pass

	def isMatrixChanged(self):
		return self.changed

	def update(self, originPossibilities, updatedPossibilities, i, j):
		if originPossibilities != updatedPossibilities:
			self.changed = True
		pass

	def clear(self):
		self.changed = False
		pass

	def set(self):
		self.changed = True
		pass

class Scorer:
	def __init__(self):
		self.rank = 0
		pass

	def result(self):
		return self.rank

	def visitNakedFinder(self, criteria):
		self.record(criteria - 1)
		pass

	def visitHiddenFinder(self, criteria):
		self.record(criteria - 1)
		pass

	def visitLockedCandidates(self):
		self.record(1)
		pass

	def visitXWingJellyFishSwordFish(self, criteria):
		self.record(criteria)
		pass

	def record(self, rank):
		if rank > self.rank:
			self.rank = rank
		pass

class KnownFinding:
	def __init__(self, knownPartOfPuzzle):
		self.zoneFindingMap = dict()
		self.determinedPart = knownPartOfPuzzle
		pass

	def addKnownFinding(self, zoneID, finding):
		if zoneID in self.zoneFindingMap:
			self.zoneFindingMap[zoneID] += [finding]
		else:
			self.zoneFindingMap[zoneID] = [finding]
		pass

	def moreAccurateFound(self, zoneID, finding):
		if (self.hasDetermined(finding)): return True
		if zoneID not in self.zoneFindingMap: return False
		existFindings = self.zoneFindingMap[zoneID]
		for existFinding in existFindings:
			if existFinding.moreAccurateThan(finding): return True
		return False

	def hasDetermined(self, finding):
		for pos in finding.pos:
			if pos in self.determinedPart: return True
		return False

class FinderContext(PossibilityMatrix, KnownFinding):
	def __init__(self, matrix, puzzleKnownPart):
		PossibilityMatrix.__init__(self, matrix)
		KnownFinding.__init__(self, puzzleKnownPart)
		pass

class SingleFinderTeller:
	def tellSingleFinder(self, finder):
		return finder.accept(self)

	def visitNakedFinder(self, criteria):
		return criteria == 1

	def visitHiddenFinder(self, criteria):
		return criteria == 1

	def visitLockedCandidates(self):
		return False

	def visitXWingJellyFishSwordFish(self, criteria):
		return False

class FinderName:
	def name(self, finder):
		return finder.accept(self)
	
	def visitNakedFinder(self, criteria):
		result = ['Naked Single', 'Naked Pair', 'Naked Triple', 'Naked Quat']
		return result[criteria - 1]

	def visitHiddenFinder(self, criteria):
		result = ['Hidden Single', 'Hidden Pair', 'Hidden Triple', 'Hidden Quat']
		return result[criteria - 1]

	def visitLockedCandidates(self):
		return 'Locked Candidates'

	def visitXWingJellyFishSwordFish(self, criteria):
		result = ['XWing', 'Jelly Fish', 'Sword Fish']
		return result[criteria - 2]

class Serializor:
	def serialize(self, obj):
		return obj.accept(self)

	def visitZone(self, id, zone):
		return list(zone)

	def visitFinding(self, possibilities, poses):
		return {'possibilities':list(possibilities), 'poses':list(poses)}

	def visiteExclusiveUpdator(self, finding, zone):
		return {'finding':finding.accept(self), 'zone':zone.accept(self)}
		
	def visitOccupationUpdator(self, finding, zone):
		return {'finding':finding.accept(self), 'zone':zone.accept(self)}

	def visitComposedUpdator(self, updators):
		return [upd.accept(self) for upd in updators]

class HintMessage:
	def __init__(self):
		self.se = Serializor()
		self.fn = FinderName()
		pass

	def getMsg(self, results):
		msg = []
		for result in results:
			(updator, finder) = result
			msg.append({"finder":self.fn.name(finder), "updator":self.se.serialize(updator)})
		return msg
	pass
