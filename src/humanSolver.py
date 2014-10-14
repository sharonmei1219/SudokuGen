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
	def solve(self, pMatrix, puzzle):
		single = pMatrix.findNewSingle()
		while single is not None:
			single.update(pMatrix)
			self.updatePuzzle(single, puzzle)
			single = pMatrix.findNewSingle()

	def updatePuzzle(self, single, puzzle):
		pos = single.pos[0]
		value = next(iter(single.possibilities))
		puzzle.change(pos, value)
		pass

class Tier_1_Strategy:
	def __init__(self, strategy):
		self.strategy = strategy
		pass

	def solve(self, pMatrix, puzzle):
		finding = pMatrix.findNewPairOrLockedCell()
		while finding is not None:
			finding.update(pMatrix)
			self.strategy.solve(pMatrix, puzzle)
			finding = pMatrix.findNewPairOrLockedCell()
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

	def findNewSingle(self):
		nakedSingleInRowFinder = self.NakedInRowFinder(1)
		nakedSingleInColumnFinder = self.NakedInColumnFinder(1)

		finders = [nakedSingleInRowFinder, nakedSingleInColumnFinder]
		for finder in finders:
			finding = finder.find(self)
			if finding is not None: return finding

		single = self.findHiddenSingle()
		if single is not None: return single

		return None

	def findHiddenSingle(self):
		for zone in self.grid.allRowsInIndex() + self.grid.allColumnsInIndex() + self.grid.allBlocksInIndex():
			valuePosMap = self.buildValuePosMapInZone(zone)
			single = self.findValueOnlyHasOnePossiblePosition(valuePosMap)
			if single is not None: return single
		return None		

	def buildValuePosMapInZone(self, zone):
		valuePosMap = {}
		for pos in zone:
			for  value in self.possibilitieAt(pos):
				if value not in valuePosMap: 
					valuePosMap[value] = []
				valuePosMap[value] += [pos]
		return valuePosMap

	def findValueOnlyHasOnePossiblePosition(self, valuePosMap):
		for value in valuePosMap:
			if len(valuePosMap[value]) == 1:
				single = FindingInRow(valuePosMap[value][0], value)
				if single in self.knownRowFindings: continue
				return single
		return None

	def findNewPairOrLockedCell(self):
		nakedPairInRowFinder = self.NakedInRowFinder(2)
		nakedPairInColumnFinder = self.NakedInColumnFinder(2)
		nakedPairInBlockFinder = self.NakedInBlockFinder(2)

		finders = [nakedPairInRowFinder, nakedPairInColumnFinder, nakedPairInBlockFinder]

		for finder in finders:
			findings = finder.find(self)
			if findings is not None : return findings
		pass

	class NakedFinder:
		def __init__(self, criteria):
			self.criteria = criteria
			pass

		def find(self, pMatrix):
			for zone in self.zones(pMatrix):
				finding = self.findPosMeetRequirementInRest(set(), [], zone, 0, pMatrix)
				if finding is not None: return finding
			return None

		def findPosMeetRequirementInRest(self, union, poses, rest, nth, pMatrix):
			if nth == self.criteria:
				return self.createResult(poses, union)

			for i in range(len(rest)):
				pos = rest[i]
				possibilities = pMatrix.possibilitieAt(pos)
				if len(union | possibilities) > self.criteria : continue

				finding = self.findPosMeetRequirementInRest(union | possibilities, poses + [pos], rest[i+1:], nth + 1, pMatrix)
				if self.isNewResultFound(finding, pMatrix): return finding
			pass

	class NakedInRowFinder(NakedFinder):
		def zones(self, pMatrix):
			return pMatrix.grid.allRowsInIndex()

		def createResult(self, pos, value):
			return FindingInRow(pos, value)

		def isNewResultFound(self, result, pMatrix):
			return result is not None and result not in pMatrix.knownRowFindings

	class NakedInColumnFinder(NakedFinder):
		def zones(self, pMatrix):
			return pMatrix.grid.allColumnsInIndex()

		def createResult(self, pos, value):
			return FindingInColumn(pos, value)

		def isNewResultFound(self, result, pMatrix):
			return result is not None and result not in pMatrix.knownColumnFindings

	class NakedInBlockFinder(NakedFinder):
		def zones(self, pMatrix):
			return pMatrix.grid.allBlocksInIndex()

		def createResult(self, poses, possibilities):
			return FindingInBlock(poses, possibilities)

		def isNewResultFound(self, result, pMatrix):
			return result is not None and result not in pMatrix.knownBlockFindings

		pass
			

	def updateRow(self, pos, possibilities, excepts):
		coords = self.grid.coordsOfRow(pos[0], pos[1])
		self.updateGroupOfCellsExcept(coords, possibilities, excepts)
		pass

	def updateColum(self, pos, possibilities, excepts):
		coords = self.grid.coordsOfColumn(pos[0], pos[1])
		self.updateGroupOfCellsExcept(coords, possibilities, excepts)
		pass

	def updateBlock(self, pos, possibilities, excepts):
		coords = self.grid.coordsOfBlock(pos[0], pos[1])
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

class Finding:
	def __init__(self, pos, value):
		self.pos = pos
		self.possibilities = value
		pass

	def __eq__(self, finding):
		return self.pos == finding.pos and self.possibilities == finding.possibilities

	def __str__(self):
		return str(self.pos) + " " + str(self.possibilities)

class FindingInRow(Finding):
	def update(self, pMatrix):
		pMatrix.updateRow(self.pos[0], self.possibilities, set(self.pos))
		pMatrix.addKnownRowFindings(self)
		for p in self.pos:
			pMatrix.setPossibilityAt(p, self.possibilities)
		pass

class FindingInColumn(Finding):
	def update(self, pMatrix):
		pMatrix.updateColum(self.pos[0], self.possibilities, set(self.pos))
		pMatrix.addKnownColumnFindings(self)
		for p in self.pos:
			pMatrix.setPossibilityAt(p, self.possibilities)
		pass

class FindingInBlock(Finding):
	def update(self, pMatrix):
		pMatrix.updateBlock(self.pos[0], self.possibilities, set(self.pos))
		pMatrix.addKnownBlockFindings(self)
		for p in self.pos:
			pMatrix.setPossibilityAt(p, self.possibilities)
		pass