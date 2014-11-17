from collections import Counter
from functools import reduce
import operator
import random
import json
import copy

_ = "/"

class Puzzle():
	def __init__(self, puzzleMatrix, grid, validator, candidates):
		self.grid = grid
		self.puzzleMatrix = puzzleMatrix

		self.validator = validator
		self.candidatesGen = candidates

	def solved(self):
		return self.full() and self.validator.validate(self.grid, self.puzzleMatrix)

	def candidatesAt(self, pos):
		return self.candidatesGen.getCandidatesAt(self.grid, pos, self.puzzleMatrix)		

	def clone(self):
		return Puzzle(self.puzzleMatrix.clone(), self.grid, self.validator, self.candidatesGen)

	def toString(self):
		return self.puzzleMatrix.toString()

	def getNumbersInPos(self, pos):
		return self.puzzleMatrix.getNumbersInPos(pos)

	def differences(self, theOtherOne):
		return self.puzzleMatrix.differences(theOtherOne.puzzleMatrix)

	def full(self):
		return self.puzzleMatrix.full()

	def firstEmptyCell(self):
		return self.puzzleMatrix.firstEmptyCell()

	def clear(self, pos):
		self.puzzleMatrix.clear(pos)

	def change(self, pos, value):
		self.puzzleMatrix.change(pos, value)

	def compare(self, theOtherGrid):
		return self.puzzleMatrix.compare(theOtherGrid.puzzleMatrix)

	def knownPart(self):
		return self.puzzleMatrix.knownPart()

	def unknownPart(self):
		emptyPos = self.puzzleMatrix.emptyList
		return {pos:set(self.candidatesAt(pos)) for pos in emptyPos}

	def dim(self):
		return self.puzzleMatrix.dim()

class PuzzleMatrix:
	def __init__(self, matrix):
		self.matrix = matrix
		self.mHeight = len(matrix)
		self.mWidth = len(matrix[0])
		self.emptyList = [(i, j) for i in range(self.mHeight) for j in range(self.mWidth) if matrix[i][j] is _]
		pass

	def change(self, pos, value):
		(i, j) = pos
		self.matrix[i][j] = value
		pass

	def clear(self, pos):
		(i, j) = pos
		self.matrix[i][j] = _
		self.emptyList = [pos] + self.emptyList	
		pass

	def firstEmptyCell(self):
		result = self.emptyList[0]
		del self.emptyList[0]
		return result
	
	def full(self):
		return len(self.emptyList) is 0

	def getNumbersInPos(self, pos):
		return [self.matrix[i][j] for (i, j) in pos]

	def differences(self, theOtherOne):
		m1, m2 = self.matrix, theOtherOne.matrix
		diff =  [(i, j) for i in range(len(self.matrix)) for j in range(len(self.matrix[0])) if m1[i][j] is not m2[i][j]]
		index = random.randint(0, len(diff) - 1)
		return diff[index]

	def compare(self, theOtherGrid):
		for i in range(self.mHeight):
			for j in range(self.mWidth):
				if self.matrix[i][j] != theOtherGrid.matrix[i][j]:
					return self.compareElement(self.matrix[i][j], theOtherGrid.matrix[i][j])
		return 0

	def compareElement(self, x, y):
		if x is y:
			return 0

		if (x is _) or (x > y) : 
			return 1
		else:
			return -1

	def toString(self):
		return json.dumps(self.matrix)

	def clone(self):
		return PuzzleMatrix(copy.deepcopy(self.matrix))

	def knownPart(self):
		return {(i, j):self.matrix[i][j] for i in range(self.mHeight) for j in range(self.mWidth) if self.matrix[i][j] != _}

	def dim(self):
		return len(self.matrix), len(self.matrix[0])

class Validator:
	def validate(self, grid, puzzleMatrix):
		directions = grid.allDirection()
		return all([self.validInDirection(direction, puzzleMatrix) for direction in directions])

	def validInDirection(self, direction, puzzleMatrix):
		zones = direction.zones()
		return all(not self.detectDuplication(puzzleMatrix.getNumbersInPos(zone)) for zone in zones)

	def detectDuplication(self, numberList):
		counter = Counter(numberList)
		return not all(counter[number] == 1 for number in counter)

class CandidatesGen:
	def __init__(self, candidatesList):
		self.candidatesList = candidatesList

	def getCandidatesAt(self, grid, pos, puzzleMatrix):
		return self.subList(self.candidatesList, grid.suroundings(pos, puzzleMatrix))

	def subList(self, list1, list2):
		return [number for number in list1 if number not in list2]

class RandomSeqCandidatesDecorator:
	def __init__(self, candidatesGen):
		self.candidatesGen = candidatesGen

	def getCandidatesAt(self, grid, pos, puzzleMatrix):
		candidates = list(self.candidatesGen.getCandidatesAt(grid, pos, puzzleMatrix))
		candidatesCount = len(candidates)
		result = []
		for i in range(0, candidatesCount):
			r = random.randint(0, candidatesCount - i - 1)
			result.append(candidates[r])
			del candidates[r]
		return result		

class Grid:
	nonEmptyNumberIn = lambda self, zone: list(filter(("/").__ne__, zone))

	def __init__(self, matrixHeight, matrixWidth, blockHeight, blockWidth):
		self.gridRow = GridRow(matrixHeight, matrixWidth)
		self.gridColumn = GridColumn(matrixHeight, matrixWidth)
		self.gridBlock = GridBlock(matrixHeight, matrixWidth, blockHeight, blockWidth)

		self.views = [self.gridRow, self.gridColumn, self.gridBlock]

		self.dim = (matrixHeight, matrixWidth)

	def flatten(self, twoDArray):
		return reduce(operator.add, twoDArray, [])

	def suroundings(self, pos, puzzleMatrix):
		poses = self.flatten([view.zoneWithPosIn(pos) for view in self.views])
		return set(puzzleMatrix.getNumbersInPos(poses)) - set(_)

	def allPos(self):
		return self.flatten(self.gridRow.zones())

	def allDirection(self):
		return [self.gridRow, self.gridColumn, self.gridBlock]

class GridDirection:
	def posesInSameZone(self, poses):
		return any([all([pos in zone for pos in poses]) for zone in self.zones()])

	def split(self, poses):
		areas = [{pos for pos in poses if pos in zone} for zone in self.zones()]
		return [area for area in areas if len(area) > 0]

class GridRow(GridDirection):
	def __init__(self, matrixHeight, matrixWidth):
		self.matrixHeight = matrixHeight
		self.matrixWidth = matrixWidth
		pass

	def zones(self):
		return [self.zoneWithPosIn((i, 0)) for i in range(self.matrixHeight)]

	def zoneWithPosIn(self, pos):
		return [(pos[0], x) for x in range(self.matrixWidth)]

class GridColumn(GridDirection):
	def __init__(self, matrixHeight, matrixWidth):
		self.matrixHeight = matrixHeight
		self.matrixWidth = matrixWidth

	def zones(self):
		return [self.zoneWithPosIn((0, j)) for j in range(self.matrixWidth)]

	def zoneWithPosIn(self, pos):
		return [(x, pos[1]) for x in range(self.matrixHeight)]

class GridBlock(GridDirection):
	def __init__(self, matrixHeight, matrixWidth, blockHeight, blockWidth):
		self.blockHeight = blockHeight
		self.blockWidth = blockWidth

		self.nbPerRow = matrixWidth // blockWidth
		bsize = blockWidth * blockHeight
		bnum = matrixHeight * matrixWidth // bsize
		self.blockIndex = [[self.blockIndexToMatrixIndex(i, j) for j in range(bsize)] for i in range(bnum)]
		self.blockIndexMap = [[(i // self.blockHeight * self.nbPerRow + j // self.blockWidth, i % self.blockHeight * self.blockWidth + j % self.blockWidth) for j in range(matrixWidth)] for i in range(matrixHeight)]

	def blockIndexToMatrixIndex(self, bi, bj):
		i = int(bi // self.nbPerRow * self.blockHeight + bj // self.blockWidth)
		j = int(bi % self.nbPerRow * self.blockWidth + bj % self.blockWidth)
		return (i, j)

	def zones(self):
		return self.blockIndex

	def zoneWithPosIn(self, pos):
		(bi, bj) = self.blockIndexMap[pos[0]][pos[1]]
		return self.blockIndex[bi]

class PuzzleFactory:
	def __init__(self, tableSize, blockWidth, blockHeight):
		self.tableSize = tableSize
		self.bw = blockHeight
		self.bh = blockHeight
		self.validator = Validator()
		self.candidatesGen = CandidatesGen(range(1, tableSize+1))
		self.permutator = PuzzleMatrixPermutator(tableSize, tableSize, blockHeight, blockWidth)

	def creatPuzzleByMatrix(self, matrix):
		grid = Grid(self.tableSize, self.tableSize, self.bw, self.bh)
		return Puzzle(PuzzleMatrix(matrix), grid, self.validator, self.candidatesGen)

	def emptyPuzzle(self):
		grid = Grid(self.tableSize, self.tableSize, self.bw, self.bh)
		return Puzzle(PuzzleMatrix(self.emptyMatrix()), grid, self.validator, self.candidatesGen)

	def getRandomPos(self, count):
		d = self.tableSize

		indexs = list(range(d*d))

		tops = [d*d - i - 1 for i in range(count)]
		randNum = [random.randint(0, top) for top in tops]

		result = []
		for num in randNum:
			result = result + [indexs[num]]
			del indexs[num]

		return [(num // d, num % d) for num in result]

	def createPuzzleFromTable(self, table, pos):
		posNumMap = dict(zip(pos, table.getNumbersInPos(pos)))
		matrix = self.emptyMatrix()
		for (i, j) in posNumMap:
			matrix[i][j] = posNumMap[(i, j)]
		return self.creatPuzzleByMatrix(matrix)

	def emptyMatrix(self):
		return  [[_]*self.tableSize for j in range(self.tableSize)]

	def tableBase(self):
		grid = Grid(self.tableSize, self.tableSize, self.bw, self.bh)
		return Puzzle(self.tableBaseMatrix(), grid, self.validator, self.candidatesGen)

	def tableBaseMatrix(self):
		return PuzzleMatrix([[1, 2, 3, 4, 5, 6, 7, 8, 9]] + [[_]*self.tableSize for j in range(self.tableSize - 1)])

	def createPuzzleMatrixByKnownPart(self, knownPart):
		matrix = self.emptyMatrix()
		for (i, j) in knownPart:
			matrix[i][j] = knownPart[(i, j)]
		return PuzzleMatrix(matrix)

	def permPuzzleKnownPart(self, knownPart):
		return self.permutator.permPuzzleKnownPart(knownPart)

	def permPuzzleMatrix(self, puzzleMatrix):
		return self.createPuzzleMatrixByKnownPart(self.permPuzzleKnownPart(puzzleMatrix.knownPart()))


class RandomPuzzleFactory(PuzzleFactory):
	def __init__(self, tableSize, blockWidth, blockHeight):
		super(RandomPuzzleFactory, self).__init__(tableSize, blockWidth, blockHeight)
		self.candidatesGen = RandomSeqCandidatesDecorator(self.candidatesGen)
		pass

class PuzzleMatrixPermutator:
	def __init__(self, tableHeight, tableWidth, blockHeight, blockWidth):
		self.tableHeight = tableHeight
		self.tableWidth = tableWidth
		self.blockHeight = blockHeight
		self.blockWidth = blockWidth
		self.fact = [1]
		self.length = max(tableHeight, tableWidth)
		for i in range(1, self.length):
			self.fact += [self.fact[i - 1] * i]
		pass

	def permGroupsAndPermItemWithinGroup(self, groupPerm, itemPerms):
		perms = zip(groupPerm, itemPerms)
		result = [[p + b * len(itemPerms[0]) for p in perm] for (b, perm) in perms]
		return reduce(operator.add, result)

	def genPerm(self, length, perNum):
		origin = list(range(length))
		result = []
		for index in reversed(range(length)):
			i = perNum // self.fact[index]
			result += [origin[i]]
			del origin[i]
			perNum = perNum % self.fact[index]
		return result

	def randomRowPerm(self):
		perm = self.randPerm(self.tableHeight, self.blockHeight)
		def rowPerm(index):
			return perm[index]
		return rowPerm

	def randomColumnPerm(self):
		perm = self.randPerm(self.tableWidth, self.blockWidth)
		def columnPerm(index):
			return perm[index]
		return columnPerm

	def randomNumberPerm(self):
		perm = self.genPerm(self.length, random.randint(self.length - 1))
		def numPerm(num):
			return perm[num-1] + 1
		return numPerm

	def randPerm(self, totalLen, blockLen):
		numOfBlock = totalLen // blockLen
		blockPerm = self.genPerm(numOfBlock, random.randint(numOfBlock - 1))
		singlePerm = [self.genPerm(blockLen, random.randint(blockLen - 1)) for i in range(numOfBlock)]
		return self.permGroupsAndPermItemWithinGroup(blockPerm, singlePerm)

	def permPuzzleKnownPart(self, puzzleKnownPart):
		row = self.randomRowPerm()
		col = self.randomColumnPerm()
		num = self.randomNumberPerm()
		return {(row(i), col(j)):num(puzzleKnownPart[(i,j)]) for (i,j) in puzzleKnownPart}