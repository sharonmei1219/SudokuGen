class HoleDigger:
	def dig(self, table, puzzle, holeCount):
		pos = puzzle.numberedPos()
		posWithHole = self.randomlyRemoveOne(pos)
		result = self.solve(table, puzzle)
		if result.solutionCount() is 1:
			return self.createPuzzle(table, posWithHole)
	pass
		