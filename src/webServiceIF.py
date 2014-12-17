from pysimplesoap.server import SoapDispatcher, SOAPHandler
from http.server import BaseHTTPRequestHandler, HTTPServer

from humanSolver import *
from puzzle import *
from puzzle import _
import json

factory = PuzzleFactory(9, 3, 3)

def sudokuHelp(puzzle):
    print(puzzle)
    humanSolver = HumanSolver(Grid(9, 9, 3, 3))
    encoder = HintMessage()
    
    matrix = json.loads(puzzle)
    puzzleObj = factory.creatPuzzleByMatrix(matrix)
    hint = humanSolver.hint(puzzleObj)
    msg = encoder.getMsg(hint)
    print(msg)
    return json.dumps(msg)

dispatcher = SoapDispatcher(
    'my_dispatcher',
    location = "http://localhost:8008/",
    action = 'http://localhost:8008/', # SOAPAction
    namespace = "http://example.com/sample.wsdl", prefix="ns0",
    trace = True,
    ns = True)

# register the user function
dispatcher.register_function('SudokuHelp', sudokuHelp,
    returns={'hint': str}, 
    args={'puzzle': str})

print("Starting server...")
httpd = HTTPServer(("", 8008), SOAPHandler)
httpd.dispatcher = dispatcher
httpd.serve_forever()