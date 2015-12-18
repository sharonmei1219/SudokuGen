from puzzle import PuzzleFactory
from puzzle import PuzzleMatrix
import json
import sys

def main(inputDir):
	factory = PuzzleFactory(5, 1, 1)
	print(inputDir)
	inputf = open(inputDir, "r")
	
	for line in inputf:
		matrix = json.loads(line)
		for i in range(30):
			pMatrix = factory.permPuzzleMatrix(PuzzleMatrix(matrix))
			print(pMatrix.toString())
			print(prettyPrint(pMatrix.matrix))
	pass

def prettyPrint(matrix):
	result = ""
	for row in matrix:
		result += printRow(row) + "\n"
	return result
	pass

def printRow(row):
	result = ""
	for cell in row:
		if cell is not '/':
			result += str(cell)
		result += "\t"
	return result
	pass

if __name__ == "__main__":
   main(sys.argv[1])