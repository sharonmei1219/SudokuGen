import unittest
from babyVersionSudokuGen import genSudoku
from puzzle import *
from sudokuTableGen import *

class TestBabyVersionSudokuGen(unittest.TestCase):
	def test5Times5SodukuGen(self):
		sudoku = genSudoku(5, 1, 10)
		knownPart = sudoku.knownPart().values()
		self.assertTrue(set(knownPart) <= set([1, 2, 3, 4, 5]))
		self.assertTrue(len(sudoku.unknownPart()) < 25)
		self.assertEqual(25, len(sudoku.unknownPart()) + len(knownPart))
		# self.assertEqual('sharon', sudoku.toString())
		pass

	def testPerm5Times5Table(self):
		for i in range(5):
			factory = PuzzleFactory(9, 1, 1)
			tableGen = TableGenerator(9, 1)
			table = tableGen.getTable()
			table = factory.permPuzzleMatrix(table.puzzleMatrix)
			print(table.toString())
		self.assertEqual('sharon', table.toString())

		pass