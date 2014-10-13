from functools import reduce
import operator
import copy

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

class Tier_0_Strategy:
	def solve(self, pMatrix, puzzle):
		single = pMatrix.findNewSingle()
		while single is not None:
			single.update(pMatrix)
			single.updatePuzzle(puzzle)
			single = pMatrix.findNewSingle()

class Tier_1_Strategy:
	def __init__(self, strategy):
		self.strategy = strategy
		pass

	def solve(self, pMatrix, puzzle):
		finding = pMatrix.findNewPairOrBlock()
		while finding is not None:
			finding.update(pMatrix)
			self.strategy.solve(pMatrix, puzzle)
			finding = pMatrix.findNewPairOrBlock()


class PossibilityMatrix:
	def __init__(self, matrix, grid):
		self.matrix = matrix
		self.knownSingle = []
		self.grid = grid
		pass

	def possibilitieAt(self, pos):
		return self.matrix[pos[0]][pos[1]]
	
	def setPossibilityAt(self, pos, possibilities):
		self.matrix[pos[0]][pos[1]] = possibilities
		pass

	def findNewSingle(self):
		single = self.findNakedSingle()
		if single is not None: return single

		single = self.findHiddenSingle()
		if single is not None: return single

		return None

	def findNakedSingle(self):
		for pos in self.grid.allPos():
			if len(self.possibilitieAt(pos)) is 1:
				value = next(iter(self.possibilitieAt(pos)))
				single = Single(pos, value)
				if single in self.knownSingle: continue
				return single		
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
				pass
			pass		
		return valuePosMap

	def findValueOnlyHasOnePossiblePosition(self, valuePosMap):
		for value in valuePosMap:
			if len(valuePosMap[value]) == 1:
				single = Single(valuePosMap[value][0], value)
				if single in self.knownSingle: continue
				return single
		return None

	def findNewPairOrBlock(self):
		pairFinder = self.RowPairFinder()
		pair = pairFinder.findPair(self)
		if pair is not None : return pair
		return None

	class PairFinder:
		def findPair(self, pMatrix):
			for zone in self.zones(pMatrix):
				pair = self.findPosMeetRequirementInRest(set(), [], zone, 0, pMatrix)
				if pair is not None: return pair
			return None


		def findPosMeetRequirementInRest(self, union, poses, rest, nth, pMatrix):
			if nth == 2:
				return self.createPair(poses, union)

			for pos in rest:
				possibilities = pMatrix.possibilitieAt(pos)
				if len(union | possibilities) > 2: continue
				return self.findPosMeetRequirementInRest(union | possibilities, poses + [pos], rest[1:], nth + 1, pMatrix)
			
			pass	
			
	class RowPairFinder(PairFinder):
		def zones(self, pMatrix):
			return pMatrix.grid.allRowsInIndex()

		def createPair(self, pos, possibilities):
			return PairInRow(pos, possibilities)
			

	def updateRow(self, pos, possibilities, excepts):
		coords = self.grid.coordsOfRow(pos[0], pos[1])
		self.updateGroupOfCellsExcept(coords, possibilities, excepts)

	def updateColum(self, pos, possibilities, excepts):
		coords = self.grid.coordsOfColumn(pos[0], pos[1])
		self.updateGroupOfCellsExcept(coords, possibilities, excepts)

	def updateBlock(self, pos, possibilities, excepts):
		coords = self.grid.coordsOfBlock(pos[0], pos[1])
		self.updateGroupOfCellsExcept(coords, possibilities, excepts)		

	def updateGroupOfCellsExcept(self, coords, possibilities, excepts):
		for pos in coords:
			if pos in excepts: continue
			self.setPossibilityAt(pos, self.possibilitieAt(pos) - possibilities)

	def addKnownSingle(self, single):
		self.knownSingle += [single]
		pass

class Single:
	def __init__(self, pos, value):
		self.pos = pos;
		self.value = value
		pass

	def __eq__(self, single):
		return self.pos == single.pos

	def update(self, pMatrix):
		pMatrix.updateRow(self.pos, {self.value}, {self.pos})
		pMatrix.updateColum(self.pos, {self.value}, {self.pos})
		pMatrix.updateBlock(self.pos, {self.value}, {self.pos})
		pMatrix.addKnownSingle(self)
		pMatrix.setPossibilityAt(self.pos, {self.value})
		pass

	def updatePuzzle(self, puzzle):
		puzzle.change(self.pos, self.value)
		pass

class PairInRow:
	def __init__(self, pos, possibilities):
		self.pos = pos
		self.possibilities = possibilities
		pass

	def update(self, pMatrix):
		pMatrix.updateRow(self.pos[0], self.possibilities, set(self.pos))
		pMatrix.addKnownRowPair(self)
		pass
		