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

class Tier_0_Strategy:
	def solve(self, pMatrix, puzzle):
		single = pMatrix.findNewSingle()
		while single is not None:
			single.update(pMatrix)
			self.updatePuzzle(single, puzzle)
			single = pMatrix.findNewSingle()

	def updatePuzzle(self, single, puzzle):
		pos = single.pos
		value = single.value
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


class PossibilityMatrix:
	def __init__(self, matrix, grid):
		self.matrix = matrix
		self.knownRowSingle = []
		self.knownColumnSingle = []
		self.knownRowPair = []
		self.knownColumnPair = []
		self.grid = grid
		pass

	def possibilitieAt(self, pos):
		return self.matrix[pos[0]][pos[1]]
	
	def setPossibilityAt(self, pos, possibilities):
		self.matrix[pos[0]][pos[1]] = possibilities
		pass

	def findNewSingle(self):
		single = self.NakedRowSingleFinder().find(self)
		if single is not None: return single

		single = self.NakedColumnSingleFinder().find(self)
		if single is not None: return single

		single = self.findHiddenSingle()
		if single is not None: return single

		return None

	class NakedSingleFinder:
		def find(self, pMatrix):
			for zone in self.zones(pMatrix):
				for pos in zone:
					if len(pMatrix.possibilitieAt(pos)) is 1:
						value = next(iter(pMatrix.possibilitieAt(pos)))
						single = self.createResult(pos, value)
						if self.isNewResultFound(single, pMatrix): return single

			return None
		
	class NakedRowSingleFinder(NakedSingleFinder):
		def zones(self, pMatrix):
			return pMatrix.grid.allRowsInIndex()

		def createResult(self, pos, value):
			return SingleInRow(pos, value)

		def isNewResultFound(self, result, pMatrix):
			return result is not None and result not in pMatrix.knownRowSingle
	
	class NakedColumnSingleFinder(NakedSingleFinder):
		def zones(self, pMatrix):
			return pMatrix.grid.allColumnsInIndex()

		def createResult(self, pos, value):
			return SingleInColumn(pos, value)

		def isNewResultFound(self, result, pMatrix):
			return result is not None and result not in pMatrix.knownColumnSingle

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
				single = SingleInRow(valuePosMap[value][0], value)
				if single in self.knownRowSingle: continue
				return single
		return None

	def findNewPairOrLockedCell(self):
		finders = [self.NakedRowPairFinder(), self.NakedColumnPairFinder()]
		for finder in finders:
			findings = finder.find(self)
			if findings is not None : return findings

	class NakedPairFinder:
		def find(self, pMatrix):
			for zone in self.zones(pMatrix):
				pair = self.findPosMeetRequirementInRest(set(), [], zone, 0, pMatrix)
				if pair is not None: return pair
			return None

		def findPosMeetRequirementInRest(self, union, poses, rest, nth, pMatrix):
			if nth == 2:
				return self.createPair(poses, union)

			for i in range(len(rest)):
				pos = rest[i]
				possibilities = pMatrix.possibilitieAt(pos)
				if len(union | possibilities) > 2: continue

				pair = self.findPosMeetRequirementInRest(union | possibilities, poses + [pos], rest[i+1:], nth + 1, pMatrix)
				if self.isNewPairFound(pair, pMatrix): return pair

			
	class NakedRowPairFinder(NakedPairFinder):
		def zones(self, pMatrix):
			return pMatrix.grid.allRowsInIndex()

		def createPair(self, pos, possibilities):
			return PairInRow(pos, possibilities)

		def isNewPairFound(self, pair, pMatrix):
			return pair is not None and pair not in pMatrix.knownRowPair
	
	class NakedColumnPairFinder(NakedPairFinder):
		def zones(self, pMatrix):
			return pMatrix.grid.allColumnsInIndex()

		def createPair(self, pos, possibilities):
			return PairInColumn(pos, possibilities)

		def isNewPairFound(self, pair, pMatrix):
			return pair is not None and pair not in pMatrix.knownColumnPair

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

	def addKnownRowSingle(self, single):
		self.knownRowSingle += [single]
		pass

	def addKnownColumnSingle(self, single):
		self.knownColumnSingle += [single]
		pass

	def addKnownRowPair(self, pair):
		self.knownRowPair += [pair]
		pass

	def addKnownColumnPair(self, pair):
		self.knownColumnPair += [pair]
		pass

class Single:
	def __init__(self, pos, value):
		self.pos = pos;
		self.value = value
		pass

	def __eq__(self, single):
		return self.pos == single.pos and self.value == single.value

	def __str__(self):
		return str(self.pos) + " " + str(self.value)

class SingleInRow(Single):
	def update(self, pMatrix):
		pMatrix.updateRow(self.pos, {self.value}, {self.pos})
		pMatrix.addKnownRowSingle(self)
		pMatrix.setPossibilityAt(self.pos, {self.value})
		pass

class SingleInColumn(Single):
	def update(self, pMatrix):
		pMatrix.updateColum(self.pos, {self.value}, {self.pos})
		pMatrix.addKnownColumnSingle(self)
		pMatrix.setPossibilityAt(self.pos, {self.value})		
		pass
	pass

class SingleInBlock(Single):
	def update(self, pMatrix):
		pMatrix.updateBlock(self.pos, {self.value}, {self.pos})
		pMatrix.addKnownBlockSingle(self)
		pMatrix.setPossibilityAt(self.pos, {self.value})
		pass
	pass

class Pair:
	def __init__(self, pos, possibilities):
		self.pos = pos
		self.possibilities = possibilities

	def __eq__(self, pair):
		return self.pos == pair.pos	

class PairInRow(Pair):
	def update(self, pMatrix):
		pMatrix.updateRow(self.pos[0], self.possibilities, set(self.pos))
		pMatrix.addKnownRowPair(self)

class PairInColumn(Pair):
	def update(self, pMatrix):
		pMatrix.updateColum(self.pos[0], self.possibilities, set(self.pos))
		pMatrix.addKnownColumnPair(self)