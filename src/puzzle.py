from collections import Counter
from functools import *
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

	def allCandidates(self):
		return self.candidatesGen.candidatesList

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

	def possibilityMatrix(self):
		pHeight, pWidth = self.puzzleMatrix.dim()
		matrix = [[set()] * pWidth for i in range(pHeight)]
		candidates = self.candidatesGen.candidatesList;
		knownPart = self.knownPart()
		for (i, j) in knownPart:
			matrix[i][j] = {knownPart[(i, j)]}

		unknownPart = self.unknownPart()
		for (i, j) in unknownPart:
			matrix[i][j] = unknownPart[(i, j)]


		return matrix
		pass

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
		pos = [(i, j) for i in range(self.mHeight) for j in range(self.mWidth) if self.matrix[i][j] != _]
		value = [self.matrix[i][j] for (i, j) in pos]
		return dict(zip(pos, value))

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
		result = Counter(numberList)
		return not all(result[number] == 1 for number in result)

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

class Zone:
	def __init__(self, inputId, poses):
		self._id = inputId
		self._poses = poses
	
	def __eq__(self, zone):
		return self._id == zone._id

	def id(self):
		return self._id

	def poses(self):
		return self._poses

	def accept(self, visitor):
		return visitor.visitZone(self._id, self._poses)

class Grid:
	def __init__(self, matrixHeight, matrixWidth, blockHeight, blockWidth):
		self.gridRow = GridRow(matrixHeight, matrixWidth)
		self.gridColumn = GridColumn(matrixHeight, matrixWidth)
		self.gridBlock = GridBlock(matrixHeight, matrixWidth, blockHeight, blockWidth)

		self.views = [self.gridRow, self.gridColumn, self.gridBlock]

		self.dim = (matrixHeight, matrixWidth)

	def flatten(self, twoDArray):
		return reduce(operator.add, twoDArray, ())

	def suroundings(self, pos, puzzleMatrix):
		poses = self.flatten([view.zoneWithPosIn(pos) for view in self.views])
		return set(puzzleMatrix.getNumbersInPos(poses)) - set(_)

	def allPos(self):
		return self.flatten(self.gridRow.zones())

	def allDirection(self):
		return [self.gridRow, self.gridColumn, self.gridBlock]

class GridDirection:
	def posesInSameZone(self, poses):
		return len(set([self.zoneIndex(pos) for pos in poses])) == 1

	def split(self, poses):
		indexes = set([self.zoneIndex(pos) for pos in poses])
		return [set([pos for pos in poses if self.zoneIndex(pos) == index]) for index in indexes]

	def zoneObjs(self): 
		return self._zones;

	def _zoneObj(self, index):
		return self._zones[index]

	def zoneObjWithPosIn(self, pos):
		index = self.zoneIndex(pos)
		return self._zones[index]
		pass

	def zoneWithPosIn(self, pos):
		index = self.zoneIndex(pos)
		return self.zoneOfPoses[index]

	def zones(self):
		return self.zoneOfPoses;


class GridRow(GridDirection):
	def __init__(self, matrixHeight, matrixWidth):
		self.zoneOfPoses = [tuple((i, j) for j in range(matrixWidth)) for i in range(matrixHeight)]
		self._ids = ['GridRow_' + str(i) for i in range(matrixHeight)]
		self._zones = [Zone(zoneId, zonePoses) for (zoneId, zonePoses) in zip(self._ids, self.zoneOfPoses)]

	def zoneIndex(self, pos):
		return pos[0]

class GridColumn(GridDirection):
	def __init__(self, matrixHeight, matrixWidth):
		self._ids = ['GridColumn_' + str(j) for j in range(matrixWidth)]
		self.zoneOfPoses = [tuple((i, j) for i in range(matrixHeight)) for j in range(matrixWidth)]
		self._zones = [Zone(zoneId, zonePoses) for (zoneId, zonePoses) in zip(self._ids, self.zoneOfPoses)]

	def zoneIndex(self, pos):
		return pos[1]

class GridBlock(GridDirection):
	def __init__(self, matrixHeight, matrixWidth, blockHeight, blockWidth):
		nbPerRow = matrixWidth // blockWidth
		bsize = blockWidth * blockHeight
		bnum = matrixHeight * matrixWidth // bsize

		def b2mIndex(bi, bj):
			i = int(bi // nbPerRow * blockHeight + bj // blockWidth)
			j = int(bi % nbPerRow * blockWidth + bj % blockWidth)
			return (i, j)

		def m2bIndex(i, j):
			return (i // blockHeight * nbPerRow + j // blockWidth)

		self.zoneOfPoses = [tuple(b2mIndex(i, j) for j in range(bsize)) for i in range(bnum)]
		self._zoneIndex = [[m2bIndex(i, j) for j in range(matrixWidth)] for i in range(matrixHeight)]
		self._ids = ['GridBlock_' + str(bi) for bi in range(bnum)]
		self._zones = [Zone(zoneId, zonePoses) for (zoneId, zonePoses) in zip(self._ids, self.zoneOfPoses)]

	def zoneIndex(self, pos):
		(i, j) = pos
		return self._zoneIndex[i][j]

class PuzzleFactory:
	def __init__(self, tableSize, blockWidth, blockHeight):
		self.tableSize = tableSize
		self.numberInPuzzle = range(1, tableSize+1);
		self.bw = blockHeight
		self.bh = blockHeight
		self.validator = Validator()
		self.candidatesGen = CandidatesGen(self.numberInPuzzle)
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
		return PuzzleMatrix([list(self.numberInPuzzle)] + [[_]*self.tableSize for j in range(self.tableSize - 1)])

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
		for i in range(1, self.length + 1):
			self.fact += [self.fact[i - 1] * i]
		pass
	
	def permPuzzleKnownPart(self, puzzleKnownPart):
		row = self.randomRowPerm()
		col = self.randomColumnPerm()
		num = self.randomNumberPerm()
		return {(row(i), col(j)): num(puzzleKnownPart[(i,j)]) for (i, j) in puzzleKnownPart}

	def randomRowPerm(self):
		perm = self.randPermOfSubgroupsAndItemsWithinGroup(self.tableHeight, self.blockHeight)
		print('rowPerm')
		print(perm)
		def rowPerm(index):
			return perm[index]
		return rowPerm

	def randomColumnPerm(self):
		perm = self.randPermOfSubgroupsAndItemsWithinGroup(self.tableWidth, self.blockWidth)
		print('columnPerm')
		print(perm)
		def columnPerm(index):
			return perm[index]
		return columnPerm

	def randomNumberPerm(self):
		perm = self.genPerm(self.length, random.randint(0, self.fact[self.length] - 1))
		print('numberPerm')
		print(perm)
		def numPerm(num):
			return perm[num-1] + 1
		return numPerm		

	def joinSubGroupPermAndItemPermWithinSubGroup(self, groupPerm, itemPerms):
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

	def randPermOfSubgroupsAndItemsWithinGroup(self, totalLen, blockLen):
		numOfBlock = totalLen // blockLen
		subGroupPermutation = self.genPerm(numOfBlock, random.randint(0, numOfBlock - 1))
		itemPermutationWithinSubGroup = [self.genPerm(blockLen, random.randint(0, blockLen - 1)) for i in range(numOfBlock)]
		return self.joinSubGroupPermAndItemPermWithinSubGroup(subGroupPermutation, itemPermutationWithinSubGroup)