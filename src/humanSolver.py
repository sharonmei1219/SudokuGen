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
		nakedSingleInRowFinder = self.NakedFinder(1, self.RowView())
		nakedSingleInColumnFinder = self.NakedFinder(1, self.ColumnView())
		nakedSingleInBlockFinder = self.NakedFinder(1, self.BlockView())
		hiddenSingleInRowFinder = self.HiddenSingleFinder(self.RowView())
		hiddenSingleInColumnFinder = self.HiddenSingleFinder(self.ColumnView())
		hiddenSingleInBlockFinder = self.HiddenSingleFinder(self.BlockView())

		finders = [nakedSingleInRowFinder, nakedSingleInColumnFinder, nakedSingleInBlockFinder, hiddenSingleInRowFinder,
					hiddenSingleInColumnFinder, hiddenSingleInBlockFinder]
		for finder in finders:
			finding = finder.find(self)
			if finding is not None: return finding

		return None

	class HiddenSingleFinder:
		def __init__(self, viewDirection):
			self.viewDir = viewDirection
			pass

		def find(self, pMatrix):
			for zone in self.viewDir.zones(pMatrix):
				valuePosMap = self.buildValuePosMapInZone(zone, pMatrix)
				single = self.findValueOnlyHasOnePossiblePosition(valuePosMap, pMatrix)
				if single is not None: return single
			return None

		def buildValuePosMapInZone(self, zone, pMatrix):
			valuePosMap = {}
			for pos in zone:
				for  value in pMatrix.possibilitieAt(pos):
					if value not in valuePosMap:
						valuePosMap[value] = []
					valuePosMap[value] += [pos]
			return valuePosMap		

		def findValueOnlyHasOnePossiblePosition(self, valuePosMap, pMatrix):
			for value in valuePosMap:
				if len(valuePosMap[value]) == 1:
					single = self.viewDir.createResult(valuePosMap[value], {value})
					if self.viewDir.isNewResultFound(single, pMatrix): return single
			return None

	def findNewPairOrLockedCell(self):
		nakedPairInRowFinder = self.NakedFinder(2, self.RowView())
		nakedPairInColumnFinder = self.NakedFinder(2, self.ColumnView())
		nakedPairInBlockFinder = self.NakedFinder(2, self.BlockView())

		finders = [nakedPairInRowFinder, nakedPairInColumnFinder, nakedPairInBlockFinder]

		for finder in finders:
			findings = finder.find(self)
			if findings is not None : return findings
		pass

	class NakedFinder:
		def __init__(self, criteria, viewDirection):
			self.criteria = criteria
			self.viewDir = viewDirection
			pass

		def find(self, pMatrix):
			for zone in self.viewDir.zones(pMatrix):
				finding = self.findPosMeetRequirementInRest(set(), [], zone, 0, pMatrix)
				if finding is not None: return finding
			return None

		def findPosMeetRequirementInRest(self, union, poses, rest, nth, pMatrix):
			if nth == self.criteria:
				return self.viewDir.createResult(poses, union)

			for i in range(len(rest)):
				pos = rest[i]
				possibilities = pMatrix.possibilitieAt(pos)
				if len(union | possibilities) > self.criteria : continue

				finding = self.findPosMeetRequirementInRest(union | possibilities, poses + [pos], rest[i+1:], nth + 1, pMatrix)
				if self.viewDir.isNewResultFound(finding, pMatrix): return finding
			pass

	class RowView:
		def zones(self, pMatrix):
			return pMatrix.grid.allRowsInIndex()

		def createResult(self, pos, value):
			return FindingInRow(pos, value)

		def isNewResultFound(self, result, pMatrix):
			return result is not None and result not in pMatrix.knownRowFindings

	class ColumnView:
		def zones(self, pMatrix):
			return pMatrix.grid.allColumnsInIndex()

		def createResult(self, pos, value):
			return FindingInColumn(pos, value)

		def isNewResultFound(self, result, pMatrix):
			return result is not None and result not in pMatrix.knownColumnFindings

	class BlockView:
		def zones(self, pMatrix):
			return pMatrix.grid.allBlocksInIndex()

		def createResult(self, poses, possibilities):
			return FindingInBlock(poses, possibilities)

		def isNewResultFound(self, result, pMatrix):
			return result is not None and result not in pMatrix.knownBlockFindings			

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