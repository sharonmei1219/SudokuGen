#has huge side effect, need to be one humanSolver Per Puzzle
class HumanSolver:
	def __init__(self, grid):
		self._grid = grid
		self.observer = PossibilityMatrixUpdateObserver()
		self.scorer = Scorer()
		self.results = [KnownResultTypeOne(), KnownResultTypeOne(), KnownResultTypeOne()]
		(self.knownResultInRow, self.knownResultInColumn, self.knownResultInBlock) = (self.results)

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
		return  [NakedFinder(length, self.gridRow, self.knownResultInRow),
				 NakedFinder(length, self.gridColumn, self.knownResultInColumn),
				 NakedFinder(length, self.gridBlock, self.knownResultInBlock)]
		pass

	def hiddenSingle(self):	return self.hiddenRule(1);
	def hiddenPair(self): return self.hiddenRule(2);
	def hiddenTriple(self):	return self.hiddenRule(3);
	def hiddenQuat(self): return self.hiddenRule(4);


	def hiddenRule(self, length):
		return [HiddenFinder(length, self.gridRow, self.knownResultInRow),
				HiddenFinder(length, self.gridColumn, self.knownResultInColumn),
				HiddenFinder(length, self.gridBlock, self.knownResultInBlock)]
		pass

	def lockedCandidates(self):
		return [LockedCellFinder(self.gridRow, self.gridBlock, self.knownResultInBlock),
				LockedCellFinder(self.gridColumn, self.gridBlock, self.knownResultInBlock),
				LockedCellFinder(self.gridBlock, self.gridRow, self.knownResultInRow),
				LockedCellFinder(self.gridBlock, self.gridColumn, self.knownResultInColumn)]
		pass

	def XWing(self): return self.crossRule(2)
	def jellyFish(self): return self.crossRule(3)
	def swordFish(self): return self.crossRule(4)

	def crossRule(self, length):
		return [XWingFinder(length, self.gridRow, self.gridColumn, self.knownResultInColumn),
				XWingFinder(length, self.gridColumn, self.gridRow, self.knownResultInRow)]
		pass

	def buildPossibilityMatrix(self, puzzle):
		pHeight, pWidth = puzzle.dim()
		matrix = [[set()] * pWidth for i in range(pHeight)]
		candidates = puzzle.allCandidates()
		for (i, j) in self._grid.allPos():
			matrix[i][j] = set(candidates)

		knownPart = puzzle.knownPart()
		for (i, j) in knownPart:
			matrix[i][j] = {knownPart[(i, j)]}

		return PossibilityMatrix(matrix)

	def createContextForPuzzleToSolve(self, puzzle):
		pMatrix = self.buildPossibilityMatrix(puzzle)
		pMatrix.register(self.observer)
		return pMatrix

	def solve(self, puzzle):
		pMatrix = self.createContextForPuzzleToSolve(puzzle)
		self.solvePossibilityMatrix(pMatrix)
		return(pMatrix)

	def solvePossibilityMatrix(self, pMatrix):
		self.observer.set()

		while self.observer.isMatrixChanged():
			self.observer.clear()
			for finder in self.finders:
				finder.findAndUpdate(pMatrix)
				if self.observer.isMatrixChanged():
					finder.score(self.scorer)
					break
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

class Finding:
	def __init__(self, pos, value):
		self.pos = pos
		self.possibilities = value
		pass

	def __eq__(self, finding):
		return self.pos == finding.pos and self.possibilities == finding.possibilities

	def __str__(self):
		return str(self.pos) + " " + str(self.possibilities)
	
	def __repr__(self):
		return self.__str__()

	def __add__(self, otherFinding):
		return Finding(self.pos | otherFinding.pos, self.possibilities | otherFinding.possibilities)

	def anyPos(self):
		return next(iter(self.pos))

	def moreAccurateThan(self, otherFinding):
		if self.pos < otherFinding.pos: return True
		if len(self.pos) == len(otherFinding.pos):
			if len(self.possibilities) > len(otherFinding.possibilities):
				return True
		return False

class ExclusiveUpdater:
	def __init__(self, finding, zone):
		self._finding = finding
		self._zone = zone
		pass

	def update(self, pMatrix):
		pMatrix.erasePossibility(self._finding.possibilities, set(self._zone.poses()) - self._finding.pos)
		pMatrix.addKnownFinding(self._zone.id(), self._finding)
		pass

class OccupationUpdator:
	def __init__(self, finding, zone):
		self._finding = finding
		self._zone = zone
		pass

	def update(self, pMatrix):
		pMatrix.setPossibility(self._finding.possibilities, self._finding.pos)
		pMatrix.addKnownFinding(self._zone.id(), self._finding)
		pass

class NullUpdator:
	def update(self, pMatrix):
		pass

class ComposedUpdator:
	def __init__(self, updators):
		self._upds = updators
		pass

	def update(self, pMatrix):
		for updator in self._upds:
			updator.update(pMatrix)
		pass


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
		return self.constructUpdator(finding)
		
class NakedFinder(Finder):
	def __init__(self, criteria, viewGrid, knownResult):
		self.criteria = criteria
		self.knownResult = knownResult
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
			
			if self.isNewResultFound(finding): return finding
		pass

	def isNewResultFound(self, result):
		return result is not None and self.knownResult.isNewResult(result)

	def update(self, finding, pMatrix):
		zone = self.viewGrid.zoneWithPosIn(finding.anyPos())
		pMatrix.erasePossibility(finding.possibilities, set(zone) - finding.pos)
		self.knownResult.add(finding)
		pass

	def score(self, scorer):
		scorer.recordPairTripleQuat(self.criteria)
		pass

	def constructUpdator(self, finding):
		return ExclusiveUpdater(finding, self.viewGrid.zoneObjWithPosIn(finding.anyPos()))

class HiddenFinder(Finder):
	def __init__(self, criteria, viewDirection, knownResult):
		self.viewDir = viewDirection
		self.criteria = criteria
		self.knownResult = knownResult
		pass

	def find(self, pMatrix):
		for zone in self.viewDir.zones():
			valuePosMap = pMatrix.buildValuePosMapInZone(zone)
			single = self.iterativelyFind(Finding(set(), set()), list(valuePosMap), 0, valuePosMap)
			if single is not None: return single
		pass

	def iterativelyFind(self, f1, restKeys, nth, valuePosMap):	
		if nth == self.criteria:
			finding = f1
			if self.isNewResultFound(finding): return finding

		for i in range(len(restKeys)):
			key = restKeys[i]
			f2 = Finding(valuePosMap[key], {key})
			if len((f1 + f2).pos) > self.criteria: continue
			
			finding = self.iterativelyFind(f1 + f2, 
				                           restKeys[i+1:], 
				                           nth+1,
				                           valuePosMap)

			if finding is not None: return finding
		pass

	def isNewResultFound(self, result):
		return result is not None and self.knownResult.isNewResult(result)

	def update(self, finding, pMatrix):
		pMatrix.setPossibility(finding.possibilities, finding.pos)
		self.knownResult.add(finding)
		pass

	def score(self, scorer):
		scorer.recordPairTripleQuat(self.criteria)
		pass

	def constructUpdator(self, finding):
		return OccupationUpdator(finding, self.viewDir.zoneObjWithPosIn(finding.anyPos()))
		pass

class LockedCellFinder(Finder):
	def __init__(self, sourceViewDir, affectViewDir, knownResult):
		self.sourceViewDir = sourceViewDir
		self.affectViewDir = affectViewDir
		self.knownResult = knownResult
		pass

	def find(self, pMatrix):
		for value in pMatrix.allPossibilities():
			zones = self.sourceViewDir.split(pMatrix.positionsOfValue(value))
			for zone in zones:
				if not self.affectViewDir.posesInSameZone(zone):
					continue
				
				finding = Finding(zone, {value})
				if not self.isNewResultFound(finding):
					continue

				return Finding(zone, {value})				
		pass

	def isNewResultFound(self, result):
		return result is not None and self.knownResult.isNewResult(result)

	def update(self, finding, pMatrix):
		zone = self.affectViewDir.zoneWithPosIn(finding.anyPos())
		pMatrix.erasePossibility(finding.possibilities, set(zone) - finding.pos)
		self.knownResult.add(finding)
		pass

	def constructUpdator(self, finding):
		return ExclusiveUpdater(finding, self.affectViewDir.zoneObjWithPosIn(finding.anyPos()))

	def score(self, scorer):
		scorer.recordLockedCandidates()
		pass

class XWingFinder(Finder):
	def __init__(self, criteria, searchingDirection, impactDirection, knownResult):
		self.searchingDirection = searchingDirection
		self.impactDirection = impactDirection
		self.criteria = criteria
		self.knownResult = knownResult
		pass

	def find(self, pMatrix):
		allPossibilities = pMatrix.allPossibilities()

		for value in allPossibilities:
			poses = pMatrix.positionsOfValue(value)
			areas = self.searchingDirection.split(poses)
			result = self.iterativelyFind(areas, 0, set(), value, 0)
			if result is not None: return result

		return None

	def iterativelyFind(self, areas, startingPoint, mergedArea, value, cnt):
		if cnt == self.criteria:
			splits = self.impactDirection.split(mergedArea)
			return [Finding(split, {value}) for split in splits]

		for j in range(startingPoint, len(areas)):
			splits = self.impactDirection.split(mergedArea | areas[j])
			if len(splits) > self.criteria: continue
			result = self.iterativelyFind(areas, j + 1, mergedArea | areas[j], value, cnt + 1)
			if self.isNewResultFound(result): return result
		pass

	def update(self, findings, pMatrix):
		for finding in findings:
			zone = self.impactDirection.zoneWithPosIn(finding.anyPos())
			pMatrix.erasePossibility(finding.possibilities, set(zone) - finding.pos)
			self.knownResult.add(finding)
		pass

	def constructUpdator(self, findings):
		updators = [ExclusiveUpdater(finding, self.impactDirection.zoneObjWithPosIn(finding.anyPos())) for finding in findings]
		return ComposedUpdator(updators)
		pass

	def isNewResultFound(self, result):
		return result is not None and self.knownResult.isNewResult(result[0])

	def score(self, scorer):
		scorer.recordXWingJellyFishSwordFish(self.criteria)
		pass

class KnownResultTypeOne:
	def __init__(self):
		self.knownFindings = {}
		pass

	def add(self, finding):
		for pos in finding.pos:
			self.knownFindings[pos] = finding
		pass

	def isNewResult(self, finding):
		return all([self.moreAccurateFound(pos, finding) for pos in finding.pos])

	def moreAccurateFound(self, pos, finding):
		if pos not in self.knownFindings: return True
		return finding.moreAccurateThan(self.knownFindings[pos])

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

	def recordPairTripleQuat(self, criteria):
		self.record(criteria - 1)
		pass

	def recordLockedCandidates(self):
		self.record(1)
		pass

	def recordXWingJellyFishSwordFish(self, criteria):
		self.record(criteria)
		pass

	def record(self, rank):
		if rank > self.rank:
			self.rank = rank
		pass

class KnownFindingZoneMapVersion:
	def __init__(self):
		self.zoneFindingMap = dict()
		pass

	def add(self, zoneID, finding):
		if zoneID in self.zoneFindingMap:
			self.zoneFindingMap[zoneID] += [finding]
		else:
			self.zoneFindingMap[zoneID] = [finding]
		pass

	def moreAccurateFound(self, zoneID, finding):
		if zoneID not in self.zoneFindingMap: return False
		existFindings = self.zoneFindingMap[zoneID]
		for existFinding in existFindings:
			if existFinding.moreAccurateThan(finding): return True
		return False

class FinderContext(PossibilityMatrix, KnownFindingZoneMapVersion):
	def __init__(self, matrix):
		PossibilityMatrix.__init__(self, matrix)
		KnownFindingZoneMapVersion.__init__(self)
		pass