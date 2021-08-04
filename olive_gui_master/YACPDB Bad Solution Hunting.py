import os
import json
import urllib.request

def writeIfInvalidSolution(file,id):
    # load problem with given id
    id = str(id)
    with urllib.request.urlopen('https://www.yacpdb.org/json.php?entry&id='+id) as url:
        
        # gets data about the problem
        data = json.loads(url.read().decode())
        try:
            ash = data.get('ash') + '1'
            print("Problem ID "+id+" exists.")
        except TypeError:
            print("Problem ID "+id+" not found.")
            return
        
        # gets stipulation
        solution = data.get('solution')


        # calls parser
        from p2w.parser import parser
        try:
          solution = parser.parse(data["solution"], debug=0)
          # we're good, solution is now a tree of nodes
          print("Problem ID "+id+" parsable.")
          return
        except Exception as ex:
          # we could not parse it, write id to file
          print("Problem ID "+id+" NOT OK, PLEASE FIX")
          file.write(id+'\n')
          return

f = open("list.txt", "a")
for id in range(140090,140110):
    writeIfInvalidSolution(f,id)
f.close()
        








        
