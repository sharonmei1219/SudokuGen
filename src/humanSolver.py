from functools import reduce
import operator

knownRowFindings = []
knownColumnFindings = []
knownBlockFindings = []

class PossibilityMatrix:
	def __init__(self, matrix, grid):
		self.matrix = matrix
		self.grid = grid
		pass

	def possibilitieAt(self, pos):
		return self.matrix[pos[0]][pos[1]]
	
	def setPossibilityAt(self, pos, possibilities):
		self.matrix[pos[0]][pos[1]] = possibilities
		pass

	def update(self, pos, possibilities, excepts, viewDirection):
		coords = viewDirection.zoneWithPosIn(pos, self.grid)
		self.updateGroupOfCellsExcept(coords, possibilities, excepts)
		pass

	def updateGroupOfCellsExcept(self, coords, possibilities, excepts):
		for pos in coords:
			if pos in excepts: continue
			self.setPossibilityAt(pos, self.possibilitieAt(pos) - possibilities)
		pass

	def buildValuePosMapInZone(self, zone):
		valuePosMap = {}
		for pos in zone:
			for  value in self.possibilitieAt(pos):
				if value not in valuePosMap: valuePosMap[value] = set()
				valuePosMap[value] |= {pos}
		return valuePosMap

class Finding:
	def __init__(self, pos, value, viewDir):
		self.pos = pos
		self.possibilities = value
		self.view = viewDir
		pass

	def __eq__(self, finding):
		return self.pos == finding.pos and self.possibilities == finding.possibilities

	def __str__(self):
		return str(self.pos) + " " + str(self.possibilities)
	
	def __repr__(self):
		return self.__str__()

	def anyPos(self):
		return next(iter(self.pos))

	def update(self, pMatrix):
		pMatrix.update(self.anyPos(), self.possibilities, set(self.pos), self.view)
		self.view.addKnownFindingsToPossibilityMatrix(self, pMatrix)
		for p in self.pos:
			pMatrix.setPossibilityAt(p, self.possibilities)
		pass

class ViewDirection:
	def posesInSameZone(self, poses, grid):
		return any([all([pos in zone for pos in poses]) for zone in self.zones(grid)])

class RowView(ViewDirection):
	def zones(self, grid):
		return grid.gridRow.zones()

	def zoneWithPosIn(self, pos, grid):
		return grid.gridRow.zoneWithPosIn(pos)

class ColumnView(ViewDirection):
	def zones(self, grid):
		return grid.allColumnsInIndex()

	def zoneWithPosIn(self, pos, grid):
		return grid.coordsOfColumn(pos[0], pos[1])

class BlockView(ViewDirection):
	def zones(self, grid):
		return grid.allBlocksInIndex()

	def zoneWithPosIn(self, pos, grid):
		return grid.coordsOfBlock(pos[0], pos[1])


class NakedFinder:
	def __init__(self, criteria, viewDirection, knownResult):
		self.criteria = criteria
		self.viewDir = viewDirection
		self.knownResult = knownResult
		pass

	def find(self, pMatrix):
		for zone in self.viewDir.zones(pMatrix.grid):
			finding = self.findPosMeetRequirementInRest(set(), [], zone, 0, pMatrix)
			if finding is not None: return finding
		return None

	def findPosMeetRequirementInRest(self, union, poses, rest, nth, pMatrix):
		if nth == self.criteria:
			return Finding(set(poses), union, self.viewDir)

		for i in range(len(rest)):
			pos = rest[i]
			possibilities = pMatrix.possibilitieAt(pos)
			if len(union | possibilities) > self.criteria : continue

			finding = self.findPosMeetRequirementInRest(union | possibilities, poses + [pos], rest[i+1:], nth + 1, pMatrix)
			if self.isNewResultFound(finding): return finding
		pass

	def isNewResultFound(self, result):
		return result is not None and result not in self.knownResult

	def addKnownFinding(self, result):
		self.knownResult.append(result)

class HiddenFinder:
	def __init__(self, criteria, viewDirection, knownResult):
		self.viewDir = viewDirection
		self.criteria = criteria
		self.knownResult = knownResult
		pass

	def find(self, pMatrix):
		for zone in self.viewDir.zones(pMatrix.grid):
			valuePosMap = pMatrix.buildValuePosMapInZone(zone)
			single = self.findHiddens(set(), set(), valuePosMap, pMatrix, list(valuePosMap), 0)
			if single is not None: return single
		pass

	def findHiddens(self, poses, possibilities, valuePosMap, pMatrix, restKeys, nth):
		if nth == self.criteria:
			finding = Finding(poses, possibilities, self.viewDir)
			if self.isNewResultFound(finding): return finding

		for i in range(len(restKeys)):
			key = restKeys[i]
			if len(valuePosMap[key] | poses) > self.criteria: continue
			finding = self.findHiddens(valuePosMap[key] | poses, possibilities | {key}, valuePosMap, pMatrix, restKeys[i+1:], nth+1)
			if finding is not None: return finding
		pass

	def isNewResultFound(self, result):
		return result is not None and result not in self.knownResult
		pass

	def addKnownFinding(self, result):
		self.knownResult.append(result)

	def update(self, finding, pMatrix):
		for pos in finding.pos:
			pMatrix.setPossibilityAt(pos, finding.possibilities)
		self.knownResult.append(finding)
		pass

class LockedCellFinder:
	def __init__(self, sourceViewDir, affectViewDir, knownResult):
		self.sourceViewDir = sourceViewDir
		self.affectViewDir = affectViewDir
		self.knownResult = knownResult
		pass

	def findNewClue(self, pMatrix):
		zones = self.sourceViewDir.zones(pMatrix.grid)
		for zone in zones:
			valuePosMap = pMatrix.buildValuePosMapInZone(zone)
			
			for value in valuePosMap:
				poses = valuePosMap[value]
				
				if not self.affectViewDir.posesInSameZone(poses, pMatrix.grid):
					continue
				
				finding = Finding(poses, {value}, self.affectViewDir)
				if not self.isNewResultFound(finding):
					continue

				return Finding(poses, {value}, self.affectViewDir)
		pass

	def isNewResultFound(self, result):
		return result is not None and result not in self.knownResult
