import pdb

from puzzle import PuzzleFactory
from puzzle import _
from solutionCollector import *
from quickSolutionFinder import *

factory = PuzzleFactory(2, 1, 1)
table = factory.creatPuzzleByMatrix([[2, 1],[1, 2]])
lastSolution = factory.creatPuzzleByMatrix([[1, 2], [2, 1]])
puzzle = factory.creatPuzzleByMatrix([[_, _],[_, _]])
collector = SolutionCollectorWithMemory(table, lastSolution)
solver = QuickSolutionFinder()
pdb.set_trace()
solver.solve(puzzle, collector)
result = collector.result()
self.assertEquals(2, result.solutionCount())