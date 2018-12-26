import sys

from Encoder.CodeWriter import CodeWriter
from Encoder.Coder import Coder

# Nuskaitom komandines eilutes parametrus
letterLength = 8
unitLength = 2
fileIn = 'test.txt'
fileOut = 'encoded'

if len(sys.argv) > 1:
    letterLength = int(sys.argv[1])
if len(sys.argv) > 2:
    unitLength = int(sys.argv[2])
if len(sys.argv) > 3:
    fileIn = sys.argv[3]
if len(sys.argv) > 4:
    fileOut = sys.argv[4]

sys.setrecursionlimit(10000)
# Nuskaitom norima uzkoduoti faila
f = open(fileIn, 'rb')
allBytes = f.read()

coder = Coder(allBytes, letterLength, unitLength)
encodedData = coder.getEncodedData()
encodingRules = coder.getEncodingRules()
codeWriter = CodeWriter(encodingRules, encodedData)
codeWriter.writeToFile(fileOut)
