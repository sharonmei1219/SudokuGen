from functools import reduce
import operator

class PossibilityMatrix:
	def __init__(self, matrix):
		self.matrix = matrix
		pass

	def possibilitieAt(self, pos):
		return self.matrix[pos[0]][pos[1]]

	def erasePossibility(self, possibilities, poses):
		for (i, j) in poses:
			self.matrix[i][j] -= possibilities
		pass

	def setPossibility(self, possibilities, poses):
		for (i, j)  in poses:
			self.matrix[i][j] = possibilities
		pass

	def buildValuePosMapInZone(self, zone):
		valuePosMap = {}
		for pos in zone:
			for  value in self.possibilitieAt(pos):
				if value not in valuePosMap: valuePosMap[value] = set()
				valuePosMap[value] |= {pos}
		return valuePosMap

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

	def anyPos(self):
		return next(iter(self.pos))

class NakedFinder:
	def __init__(self, criteria, viewGrid, knownResult):
		self.criteria = criteria
		self.knownResult = knownResult
		self.viewGrid = viewGrid
		pass

	def find(self, pMatrix):
		for zone in self.viewGrid.zones():
			finding = self.findPosMeetRequirementInRest(set(), [], zone, 0, pMatrix)
			if finding is not None: return finding
		return None

	def findPosMeetRequirementInRest(self, union, poses, rest, nth, pMatrix):
		if nth == self.criteria:
			return Finding(set(poses), union)

		for i in range(len(rest)):
			pos = rest[i]
			possibilities = pMatrix.possibilitieAt(pos)
			if len(union | possibilities) > self.criteria : continue

			finding = self.findPosMeetRequirementInRest(union | possibilities, 
				                                        poses + [pos], 
				                                        rest[i+1:], 
				                                        nth + 1, 
				                                        pMatrix)
			
			if self.isNewResultFound(finding): return finding
		pass

	def isNewResultFound(self, result):
		return result is not None and result not in self.knownResult

	def addKnownFinding(self, result):
		self.knownResult.append(result)
		pass

	def update(self, finding, pMatrix):
		zone = self.viewGrid.zoneWithPosIn(finding.anyPos())
		pMatrix.erasePossibility(finding.possibilities, set(zone) - finding.pos)
		self.addKnownFinding(finding)
		pass

class HiddenFinder:
	def __init__(self, criteria, viewDirection, knownResult):
		self.viewDir = viewDirection
		self.criteria = criteria
		self.knownResult = knownResult
		pass

	def find(self, pMatrix):
		for zone in self.viewDir.zones():
			valuePosMap = pMatrix.buildValuePosMapInZone(zone)
			single = self.findHiddens(set(), set(), valuePosMap, pMatrix, list(valuePosMap), 0)
			if single is not None: return single
		pass

	def findHiddens(self, poses, possibilities, valuePosMap, pMatrix, restKeys, nth):
		if nth == self.criteria:
			finding = Finding(poses, possibilities)
			if self.isNewResultFound(finding): return finding

		for i in range(len(restKeys)):
			key = restKeys[i]
			if len(valuePosMap[key] | poses) > self.criteria: continue
			
			finding = self.findHiddens(valuePosMap[key] | poses, 
				                       possibilities | {key}, 
				                       valuePosMap, 
				                       pMatrix, 
				                       restKeys[i+1:], nth+1)

			if finding is not None: return finding
		pass

	def isNewResultFound(self, result):
		return result is not None and result not in self.knownResult

	def addKnownFinding(self, result):
		self.knownResult.append(result)
		pass

	def update(self, finding, pMatrix):
		pMatrix.setPossibility(finding.possibilities, finding.pos)
		self.addKnownFinding(finding)
		pass

class LockedCellFinder:
	def __init__(self, sourceViewDir, affectViewDir, knownResult):
		self.sourceViewDir = sourceViewDir
		self.affectViewDir = affectViewDir
		self.knownResult = knownResult
		pass

	def find(self, pMatrix):
		zones = self.sourceViewDir.zones()
		for zone in zones:
			valuePosMap = pMatrix.buildValuePosMapInZone(zone)
			
			for value in valuePosMap:
				poses = valuePosMap[value]
				
				if not self.affectViewDir.posesInSameZone(poses):
					continue
				
				finding = Finding(poses, {value})
				if not self.isNewResultFound(finding):
					continue

				return Finding(poses, {value})
		pass

	def addKnownFinding(self, result):
		self.knownResult.append(result)
		pass

	def isNewResultFound(self, result):
		return result is not None and result not in self.knownResult

	def update(self, finding, pMatrix):
		zone = self.affectViewDir.zoneWithPosIn(finding.anyPos())
		pMatrix.erasePossibility(finding.possibilities, set(zone) - finding.pos)
		self.addKnownFinding(finding)
		pass

class XWingFinder:
	def __init__(self, searchingDirection, impactDirection):
		self.searchingDirection = searchingDirection
		self.impactDirection = impactDirection
		pass

	def find(self, pMatrix):
		allpositions = [(i, j) for i in range(len(pMatrix.matrix)) for j in range(len(pMatrix.matrix[0]))]
		allPossibilities = set().union(*[pMatrix.matrix[i][j] for (i, j) in allpositions])

		for value in allPossibilities:
			poses = [(i, j) for (i, j) in allpositions if (value in pMatrix.matrix[i][j])]

			areas = self.searchingDirection.split(poses)

			for i in range(len(areas)):
				if len(areas[i]) == 2:
					for j in range(i+1, len(areas)):
						if len(areas[j]) != 2: continue
						mergedArea = areas[i] | areas[j]
						splitedInOtherDir = self.impactDirection.split(mergedArea)
						if len(splitedInOtherDir) == 2:
							return [Finding(splitedInOtherDir[0], {value}), Finding(splitedInOtherDir[1], {value})]

						pass
				pass
			pass
		return None