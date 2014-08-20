from collections import Counter

class Puzzle():
	def __init__(self, grid, validator, candidates):
		self.grid = grid
		self.validator = validator
		self.candidatesGen = candidates

	def solved(self):
		return self.grid.full() and self.validator.validate(self.grid)
	
	def candidates(self):
		return self.candidatesGen.getCandidates(self.grid)

	def fill(self, number):
		return Puzzle(self.grid.fill(number), self.validator, self.candidates)

class Validator:
	def validate(self, grid):
		zones = grid.allRows()
		zones.extend(grid.allColumns())
		zones.extend(grid.allBlocks())
		return all(not self.detectDuplication(zone) for zone in zones)


	def detectDuplication(self, numberList):
		counter = Counter(numberList)
		return not all(counter[number] == 1 for number in counter)

class Grid:
	pass
		