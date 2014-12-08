from pysimplesoap.server import SoapDispatcher, SOAPHandler
from http.server import BaseHTTPRequestHandler, HTTPServer

def sudokuHelp(puzzle):
    print(puzzle)
    return 'hello, I am human solver'

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