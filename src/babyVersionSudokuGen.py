from sudokuTableGen import *
from puzzle import *
from quickSolutionFinder import *
from puzzleGenerator import *

def genSudoku(tableSize, blockSize, initialKnownPartLen):
	tableGen = TableGenerator(tableSize, blockSize)
	factory = PuzzleFactory(tableSize, blockSize, blockSize)
	solutionFinder = QuickSolutionFinder()
	solver = QuickSolver(solutionFinder)
	puzzleGen = QuickPuzzleGenerator(factory, solver)
	digger = HoleDigger(puzzleGen)
	table = tableGen.getTable()
	puzzle = digger.constructPuzzleWithOnlySolution(table, initialKnownPartLen)

	matrix = puzzle.puzzleMatrix
	matrix = factory.permPuzzleMatrix(matrix)
	puzzle = factory.creatPuzzleByMatrix(matrix.matrix)

	return puzzle
	pass
