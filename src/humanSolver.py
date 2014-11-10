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
		if len(self.pos) < len(otherFinding.pos): return True
		if len(self.pos) == len(otherFinding.pos):
			if len(self.possibilities) > len(otherFinding.possibilities):
				return True
		return False

class Finder:
	def findAndUpdate(self, pMatrix):
		foundSomething = False
		finding = self.find(pMatrix)

		while finding != None:
			self.update(finding, pMatrix)
			foundSomething = True;
			finding = self.find(pMatrix)
		
		return foundSomething
		

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
			possibilities = pMatrix.possibilitieAt(pos)
			f2 = Finding({pos}, possibilities)
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
			posesOfkey = valuePosMap[key]
			f2 = Finding(posesOfkey, {key})
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
			return [Finding(splits[0], {value}), Finding(splits[1], {value})]

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

		