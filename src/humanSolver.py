from functools import reduce
import operator

class Ranker:
	def __init__(self, strategys):
		self.strategys = strategys
		pass

	def rank(self, puzzle):
		pMatrix = self.createPossibilityMatrix(puzzle)
		for strategy in self.strategys:
			strategy.solve(pMatrix, puzzle)
			if puzzle.solved():
				return strategy.rank()
		pass

class Tier_0_Strategy:
	def __init__(self):
		nakedSingleInRowFinder = NakedFinder(1, RowView())
		nakedSingleInColumnFinder = NakedFinder(1, ColumnView())
		nakedSingleInBlockFinder = NakedFinder(1, BlockView())
		hiddenSingleInRowFinder = HiddenFinder(1, RowView())
		hiddenSingleInColumnFinder = HiddenFinder(1, ColumnView())
		hiddenSingleInBlockFinder = HiddenFinder(1, BlockView())

		self.finders = [nakedSingleInRowFinder, 
		                nakedSingleInColumnFinder, 
		                nakedSingleInBlockFinder, 
		                hiddenSingleInRowFinder,
						hiddenSingleInColumnFinder, 
						hiddenSingleInBlockFinder]
		pass

	def solve(self, pMatrix, puzzle):
		single = self.findNewSingle(pMatrix)
		while single is not None:
			single.update(pMatrix)
			self.updatePuzzle(single, puzzle)
			single = self.findNewSingle(pMatrix)

	def updatePuzzle(self, single, puzzle):
		pos = single.pos[0]
		value = next(iter(single.possibilities))
		puzzle.change(pos, value)
		pass

	def findNewSingle(self, pMatrix):
		findings = pMatrix.findWithFinders(self.finders)
		if findings is not None : return findings
		pass	


class Tier_1_Strategy:
	def __init__(self, strategy):
		self.strategy = strategy
		nakedPairInRowFinder = NakedFinder(2, RowView())
		nakedPairInColumnFinder = NakedFinder(2, ColumnView())
		nakedPairInBlockFinder = NakedFinder(2, BlockView())

		self.finders = [nakedPairInRowFinder, 
				   		nakedPairInColumnFinder, 
						nakedPairInBlockFinder]		
		pass

	def solve(self, pMatrix, puzzle):
		finding = self.findNewPairOrLockedCell(pMatrix)
		while finding is not None:
			finding.update(pMatrix)
			self.strategy.solve(pMatrix, puzzle)
			finding = self.findNewPairOrLockedCell(pMatrix)
		pass

	def findNewPairOrLockedCell(self, pMatrix):
		findings = pMatrix.findWithFinders(self.finders)
		if findings is not None : return findings
		pass		

class PossibilityMatrix:
	def __init__(self, matrix, grid):
		self.matrix = matrix
		self.knownRowFindings = []
		self.knownColumnFindings = []
		self.knownBlockFindings = []
		self.grid = grid
		pass

	def possibilitieAt(self, pos):
		return self.matrix[pos[0]][pos[1]]
	
	def setPossibilityAt(self, pos, possibilities):
		self.matrix[pos[0]][pos[1]] = possibilities
		pass

	def findWithFinders(self, finders):
		for finder in finders:
			findings = finder.find(self)
			if findings is not None : return findings
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

	def addKnownRowFindings(self, single):
		self.knownRowFindings += [single]
		pass

	def addKnownColumnFindings(self, single):
		self.knownColumnFindings += [single]
		pass

	def addKnownBlockFindings(self, finding):
		self.knownBlockFindings += [finding]
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

	def anyPos(self):
		return next(iter(self.pos))

	def update(self, pMatrix):
		pMatrix.update(self.anyPos(), self.possibilities, set(self.pos), self.view)
		self.view.addKnownFindingsToPossibilityMatrix(self, pMatrix)
		for p in self.pos:
			pMatrix.setPossibilityAt(p, self.possibilities)
		pass

class RowView:
	def zones(self, grid):
		return grid.allRowsInIndex()

	def zoneWithPosIn(self, pos, grid):
		return grid.coordsOfRow(pos[0], pos[1])

	def isNewResultFound(self, result, pMatrix):
		return result is not None and result not in pMatrix.knownRowFindings

	def addKnownFindingsToPossibilityMatrix(self, result, pMatrix):
		pMatrix.addKnownRowFindings(result)
		pass

class ColumnView:
	def zones(self, grid):
		return grid.allColumnsInIndex()

	def zoneWithPosIn(self, pos, grid):
		return grid.coordsOfColumn(pos[0], pos[1])

	def isNewResultFound(self, result, pMatrix):
		return result is not None and result not in pMatrix.knownColumnFindings

	def addKnownFindingsToPossibilityMatrix(self, result, pMatrix):
		pMatrix.addKnownColumnFindings(result)
		pass

class BlockView:
	def zones(self, grid):
		return grid.allBlocksInIndex()

	def zoneWithPosIn(self, pos, grid):
		return grid.coordsOfBlock(pos[0], pos[1])

	def isNewResultFound(self, result, pMatrix):
		return result is not None and result not in pMatrix.knownBlockFindings

	def addKnownFindingsToPossibilityMatrix(self, result, pMatrix):
		pMatrix.addKnownBlockFindings(result)
		pass


class NakedFinder:
	def __init__(self, criteria, viewDirection):
		self.criteria = criteria
		self.viewDir = viewDirection
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
			if self.viewDir.isNewResultFound(finding, pMatrix): return finding
		pass


class HiddenFinder:
	def __init__(self, criteria, viewDirection):
		self.viewDir = viewDirection
		self.criteria = criteria
		pass

	def find(self, pMatrix):
		for zone in self.viewDir.zones(pMatrix.grid):
			valuePosMap = pMatrix.buildValuePosMapInZone(zone)
			single = self.findHiddens(set(), set(), valuePosMap, pMatrix, list(valuePosMap), 0)
			if single is not None: return single
		pass

	def findHiddens(self, poses, possibilities, valuePosMap, pMatrix, restKeys, nth):
		if nth == self.criteria:
			finding = Finding(poses, possibilities,self.viewDir)
			if self.viewDir.isNewResultFound(finding, pMatrix): return finding

		for i in range(len(restKeys)):
			key = restKeys[i]
			if len(valuePosMap[key] | poses) > self.criteria: continue
			finding = self.findHiddens(valuePosMap[key] | poses, possibilities | {key}, valuePosMap, pMatrix, restKeys[i+1:], nth+1)
			if finding is not None: return finding
		pass