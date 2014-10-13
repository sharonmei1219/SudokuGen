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
			single = pMatrix.findNewSingle()


class PossibilityMatrix:
	def __init__(self, matrix, grid):
		self.matrix = matrix
		self.knownSingle = []
		self.grid = grid
		pass

	def findNewSingle(self):
		for i in range(len(self.matrix)):
			for j in range(len(self.matrix[i])):
				if len(self.matrix[i][j]) is 1:
					value = next(iter(self.matrix[i][j]))
					single = NakedSingle(i, j, value)
					if single in self.knownSingle: continue
					return single
		return None

	def updateRow(self, pos, possibilities, excepts):
		coords = self.grid.coordsOfRow(pos[0], pos[1])
		for pos in coords:
			if pos in excepts: continue
			self.matrix[pos[0]][pos[1]] = self.matrix[pos[0]][pos[1]] - possibilities

	def updateColum(self, pos, possibilities, excepts):
		coords = self.grid.coordsOfColumn(pos[0], pos[1])
		for pos in coords:
			if pos in excepts: continue
			self.matrix[pos[0]][pos[1]] = self.matrix[pos[0]][pos[1]] - possibilities		

	def updateBlock(self, pos, possibilities, excepts):
		pass

	def addKnownSingle(self, single):
		self.knownSingle += [single]
		pass

	pass

class NakedSingle:
	def __init__(self, i, j, value):
		self.i = i;
		self.j = j;
		self.value = value
		pass

	def __eq__(self, single):
		return self.i == single.i and self.j == single.j

	def update(self, pMatrix):
		pMatrix.updateRow((self.i, self.j), {self.value}, {(self.i, self.j)})
		pMatrix.updateColum((self.i, self.j), {self.value}, {(self.i, self.j)})
		pMatrix.updateBlock((self.i, self.j), {self.value}, {(self.i, self.j)})
		pMatrix.addKnownSingle(self)
		pass

	def updatePuzzle(self, puzzle):
		puzzle.change((self.i, self.j), self.value)
		pass
				