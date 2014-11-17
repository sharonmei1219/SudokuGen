from puzzle import PuzzleFactory
from puzzle import PuzzleMatrix
import json
import sys

def main(inputDir):
	factory = PuzzleFactory(9, 3, 3)
	inputf = open(inputDir, "r")

	for line in inputf:
		matrix = json.loads(line)
		for i in range(10):
			pMatrix = factory.permPuzzleMatrix(PuzzleMatrix(matrix))
			print(pMatrix.toString())
	pass

if __name__ == "__main__":
   main(sys.argv[1])