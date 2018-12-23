from heapq import heappush, heappop

from bitarray import bitarray

from Model.EncodedData import EncodedData
from Model.EncodingRules import EncodingRules
from Model.Node import Node


class Coder:
    def __init__(self, word, letterLength, unitLength):
        self.word = bitarray()
        self.word.frombytes(word)
        print(len(self.word))
        # print(self.word)
        self.letterLength = letterLength
        self.unitLength = unitLength
        self.lettersDictionary = {}
        # Bitai kurie nebeiejo i raide. Pvz:. jei k = 4 ir turim žodį: 010110, tai 0101 bus viena raidė, o galune 10 nebesudarys raides
        self.suffixBits = bitarray()
        self.suffixBits, self.word = self.__getSuffixBits()
        if len(self.word) < 1:
            raise Exception('Ivesties failas negali buti mazesnis nei koduojamo zodzio ilgis')
            
        #self.lettersDictionary = self.__getLettersDictionary()
        self.dictionaryOfDictionaries = self.__getEncodedLettersForDictionaryOfDictionaries()

    def __getEncodedLettersForDictionaryOfDictionaries(self):
        dictionaryOfDictionaries = self.__getDictionaryOfDictionaries()
        for key in dictionaryOfDictionaries:
            uniqueSymbolsWithFreqs = dictionaryOfDictionaries[key]
            dictionaryOfDictionaries[key] = self.__getLettersDictionary(uniqueSymbolsWithFreqs)
        return dictionaryOfDictionaries
    def __getDictionaryOfDictionaries(self):
        uniqueLettersUnits = self.__getUniqueLetterUnitsInWordWithoutFreqs(self.word)
        dictionaryOfDictionaries = self.__createDictionaryOfDictionaries(uniqueLettersUnits)
        bitsToTake = self.letterLength * self.unitLength
        i = 0
        while i < len(self.word) - bitsToTake:
            lettersUnit = self.word[i:i+bitsToTake]
            letterDictionary = dictionaryOfDictionaries[lettersUnit.to01()]
            nextLettersUnit = self.word[i+bitsToTake:i+2*bitsToTake]
            if nextLettersUnit.to01() in letterDictionary:
                letterDictionary[nextLettersUnit.to01()] += 1
            else:
                letterDictionary[nextLettersUnit.to01()] = 1
            i += bitsToTake
        for element in dictionaryOfDictionaries.items():
            listItems = self.__getListItem(element[1])
            dictionaryOfDictionaries[element[0]] = listItems
        dictionaryOfDictionaries = self.__deleteEmptyValues(dictionaryOfDictionaries)
        return dictionaryOfDictionaries
    def __deleteEmptyValues(self, dictionaryOfDictionaries):
        keyToDelete = None
        for key in dictionaryOfDictionaries.items():
            if not key[1]:
                keyToDelete = key[0]
        if keyToDelete is not None:
            del dictionaryOfDictionaries[keyToDelete]
        return dictionaryOfDictionaries
    def __getListItem(self, dict):
        list = []
        for key, value in dict.items():
            list.append([key, value])
        return list
    def __createDictionaryOfDictionaries(self, uniqueLettersUnits):
        dict = {}
        for lettersUnit in uniqueLettersUnits:
            dict[lettersUnit] = {}
        return dict
        
    def __getUniqueLetterUnitsInWordWithoutFreqs(self, word):
        i = 0
        length = len(word)
        dict = {}
        letterUnitBitsSize = self.letterLength * self.unitLength
        while i < length:
            letter = word[i:i+letterUnitBitsSize]
            if letter.to01() in dict:
                dict[letter.to01()] += 1
            else:
                dict[letter.to01()] = 1
            i += letterUnitBitsSize
        dictList = []
        for key, value in dict.items():
            dictList.append(key)
        return dictList
        
    def __getSuffixBits(self):
        suffixBitsLength = len(self.word) % self.letterLength
        if suffixBitsLength == 0:
            return bitarray(), self.word
        # print(suffixBitsLength)
        suffixBits = self.word[len(self.word) - suffixBitsLength:len(self.word)]
        return suffixBits, self.word[:len(self.word) - suffixBitsLength]

    def getEncodingRules(self):
        rootsDictionary = {}
        treeBitsDict = {}
        lettersDict = {}
        for item in self.dictionaryOfDictionaries.items():
            dict = item[0]
            innerDict = self.dictionaryOfDictionaries[dict]
            listOfItems = []
            for elem in innerDict.items():
                listOfItems.append(elem)
            #print(listOfItems)
            rootsDictionary[item[0]] = self.__createTree(listOfItems)
            #print(self.__getEncodingDecodingRules(rootsDictionary[item[0]]))
            treeBits = self.__getEncodingDecodingRules(rootsDictionary[item[0]])
            #self.dictionaryOfDictionaries[item[0]] = treeBits

            treeBitsDict[item[0]] = treeBits
            #print(treeBits)
        encodingRules = EncodingRules(treeBitsDict, self.letterLength, self.unitLength, len(self.dictionaryOfDictionaries))
        return encodingRules

    # pvz jei yra 11110a0b11....., tai treeBits - bitukai; symbols - a,b
    def __separateTreeBitsAndLetters(self, treeStr):
        bits = []
        letters = []
        for element in treeStr:
            if isinstance(element, bool):
                bits.append(element)
            else:
                letters.append(element)
        return bitarray(bits), letters

    # Gaunam taisykles. Pvz:. 1110a110b... -> a dekoduojama i 0001, b i
    def __getEncodingDecodingRules(self, node):
        str = bitarray()
        if node.getLetter() == '':
            str.append(True)
        else:
            str.append(False)
            #print(node.getLetter())
            str.extend(node.getLetter())
        if node.leftChild is not None:
            str.extend(self.__getEncodingDecodingRules(node.leftChild))
        if node.rightChild is not None:
            str.extend(self.__getEncodingDecodingRules(node.rightChild))
        return str

    def __createTree(self, uniqueLetters):
        rootNode = Node('')
        #uniqueCharsRepresentedInBits = self.__getUniqueLettersInWord()
        for letter in uniqueLetters:
            # letter butu [raide, daznis]
            rootNode = self.__updateTree(rootNode, letter[1], letter[0])
        return rootNode

    def __updateTree(self, node, encodedLetter, letter):
        #encodedLetter = letter#self.lettersDictionary[letter]
        currentNode = node
        for i in range(0, len(encodedLetter)):
            bit = encodedLetter[i]
            if bit == 0:
                if currentNode.leftChild is None:
                    currentNode.leftChild = Node('')
                currentNode = currentNode.leftChild
            elif bit == 1:
                if currentNode.rightChild is None:
                    currentNode.rightChild = Node('')
                currentNode = currentNode.rightChild
        currentNode.setLetter(letter)
        return node

    def getEncodedData(self):
        encodedWord = bitarray()
        encodedWord.append(False)
        bitsToRead = self.letterLength * self.unitLength
        currentUnit = self.word[0:bitsToRead]
        currentDictionary = self.dictionaryOfDictionaries[currentUnit.to01()]
        i = bitsToRead
        while i < len(self.word):
            currentUnit = self.word[i:i+bitsToRead]
            encodedUnit = currentDictionary[currentUnit.to01()]
            encodedWord.extend(encodedUnit)
            if i + bitsToRead < len(self.word):
                currentDictionary = self.dictionaryOfDictionaries[currentUnit.to01()]
            i += bitsToRead
        return EncodedData(encodedWord, self.suffixBits)

    def __getEncodedLetter(self, letter):
        return self.lettersDictionary[letter]

    # Gaunam žodyna koki simboli i koki uzkoduoti. Tai diction[a] - gaunam kaip uzkoduotas a
    def __getLettersDictionary(self, uniqueSymbolsWithFreqs):
        #uniqueSymbols = self.__getUniqueLettersInWord()
        # print(uniqueSymbols)
        symbolsList = self.__splitListOfSymbolsToListOfSymbolsList(uniqueSymbolsWithFreqs)
        if len(symbolsList) == 1:
            diction = self.__createDictionaryForSymbols(symbolsList, "0", {})
        else:
            diction = self.__createDictionaryForSymbols(symbolsList, "", {})
        # print("dict dydis")
        # print(len(diction))
        return diction

    # Jei turim lista [a,b,c,d], tai verciam i [[a],[b],[c],[d]]
    def __splitListOfSymbolsToListOfSymbolsList(self, uniqueSymbols):
        list = []
        for element in uniqueSymbols:
            newList = [element]
            list.append(newList)
        return list

    # gaunam dictionary raidems
    def __createDictionaryForSymbols(self, symbolsList, currentSeq, diction):
        if len(symbolsList) == 1:
            diction[((symbolsList[0])[0])[0]] = bitarray(currentSeq)
            # print(len(currentSeq))
            # print("key: %s, value: %s" % (((symbolsList[0])[0])[0], currentSeq))
            return diction
        minHeap = self.__createHeap(symbolsList)
        # print("recLimit %d" % (sys.getrecursionlimit()))
        while len(minHeap) != 2:
            # 2 mažiausius bucketus apjungiam i viena bucketa. Jei turim [[a],[b],[c],[d]] verciam i [[a], [b], [c,d]]
            minHeap = self.__merge2LeastBucketsIntoOne(minHeap)
            # symbolsList = self.__merge2LeastBucketsIntoOne(symbolsList)
        # Po loopo gaunam lista kuriame yra du itemai, pvz [[a, c, h, ...], [b, d, e, ...]]
        # symbolsList = self.__sortDescending(symbolsList)
        leftList = self.__splitListOfSymbolsToListOfSymbolsList(heappop(minHeap)[1])
        currentSeq = currentSeq + "0"
        diction = self.__createDictionaryForSymbols(leftList, currentSeq, diction)
        currentSeq = currentSeq[:len(currentSeq) - 1]
        rightList = self.__splitListOfSymbolsToListOfSymbolsList(heappop(minHeap)[1])
        currentSeq = currentSeq + "1"
        diction = self.__createDictionaryForSymbols(rightList, currentSeq, diction)

        return diction

    def __createHeap(self, symbolsList):
        heap = []
        for item in symbolsList:
            value = self.__calculateTotalValueOfBucket(item)
            heappush(heap, (value, item))
        return heap

    def __merge2LeastBucketsIntoOne(self, minHeap):
        least = heappop(minHeap)
        secLeast = heappop(minHeap)
        newItem = []
        newItem.extend(secLeast[1])
        newItem.extend(least[1])
        newItemValue = secLeast[0] + least[0]
        heappush(minHeap, (newItemValue, newItem))
        return minHeap

    def __calculateTotalValueOfBucket(self, bucket):
        totalValue = 0
        for item in bucket:
            totalValue = totalValue + item[1]
        return totalValue

    # Gaunam lista unikaliu raidziu ir ju daznius [['00001', 1534], [...], ...]
    def __getUniqueLettersInWord(self):
        i = 0
        length = len(self.word)
        dict = {}
        while i < length:
            letter = self.word[i:i + self.letterLength]
            if letter.to01() in dict:
                dict[letter.to01()] += 1
            else:
                dict[letter.to01()] = 1
            i += len(letter)
        dictList = []
        for key, value in dict.items():
            dictList.append([key, value])
        return dictList
