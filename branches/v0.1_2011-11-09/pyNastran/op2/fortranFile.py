#import os
#import sys

import struct
from struct import unpack,pack

class FortranFile(object):
    def __init__(self):
        self.endian = '>'
    
    def setEndian(self,endian):
        self.endian = endian

    def readHollerith(self):
        self.skip(4)  # weird hollerith

    def readHeader(self,expected):
        """
        a header is defined as (4,i,4), where i is an integer
        """
        data = self.op2.read(12)
        ints = self.getInts(data)
        print "header ints = %s" %(repr(ints))
        self.n += 12
        assert ints[0]==ints[2]==4,"header ints=(%s, %2s, %s) expected=%s" %(ints[0],ints[1],ints[2],expected)
        return ints[1]

    def readString(self,nData):
        """
        reads nCharacters that are assumed to be a string
        """
        data = self.op2.read(nData)
        string = ''.join(self.getStrings(data))
        self.n += nData
        return string

    #def readString(self,nData):
    #    data = self.op2.read(nData)
    #    self.n += nData
    #    words = self.getStrings(data)
    #    return ''.join(words)

    def readInts(self,nInts):
        """
        reads nIntegers
        """
        nData = 4*nInts
        #print "nData = ",nData
        data = self.op2.read(nData)

        iFormat = 'i'*nInts
        ints = unpack(iFormat,data)
        self.n+=nData
        return ints

    def readDoubles(self,nData):
        """
        reads nDoubles
        """
        data = self.op2.read(nData)
        self.n += nData
        doubles = self.getDoubles(data)
        return doubles

    def readFloats(self,nData):
        """
        reads nFloats
        """
        data = self.op2.read(nData)
        self.n += nData
        floats = self.getFloats(data)
        return floats

    def getStrings(self,data):
        """
        unpacks a data set into a series of characters
        """
        n = len(data)
        sFormat = 's'*n
        strings = unpack(sFormat,data)
        return strings

    def getInts(self,data):
        """
        unpacks a data set into a series of ints
        """
        n = len(data)
        nInts = n/4
        #print "nInts = ",nInts
        iFormat = 'i'*nInts
        ints = unpack(iFormat,data[:nInts*4])
        return ints

    def getLongs(self,data):
        """
        unpacks a data set into a series of longs
        """
        n = len(data)
        nLongs = n/4
        #print "nLongs = ",nLongs
        #a = pack('l',200)
        #print "len(a) = ",len(a)
        
        LFormat = 'l'*nLongs
        longs = unpack(LFormat,data[:nLongs*4])
        return longs

    def getFloats(self,data):
        """
        unpacks a data set into a series of floats
        """
        n = len(data)
        nFloats = n/4
        fFormat = 'f'*nFloats
        ints = unpack(fFormat,data[:nFloats*4])
        return ints

    def getDoubles(self,data):
        """
        unpacks a data set into a series of doubles
        """
        n = len(data)
        nDoubles = n/8
        dFormat = 'd'*nDoubles
        ints = unpack(dFormat,data[:nDoubles*8])
        return ints
    
    def printBlock(self,data):
        """
        prints a data set in int/float/double/string format to
        determine table info.  doesn't move cursor.
        """
        ints    = self.getInts(data)
        #longs   = self.getLongs(data)
        floats  = self.getFloats(data)
        doubles = self.getDoubles(data)
        strings = self.getStrings(data)
        print "ints    = ",ints
        #print "longs   = ",longs
        print "floats  = ",floats
        print "doubles = ",doubles
        print "strings = |%r|" %(''.join(strings))

    def getData(self,n):
        """
        gets a data set of length N
        """
        data = self.op2.read(n)
        self.n+=n
        return data

    def getBlockIntEntry(self,data,n):
        """
        given a data set, grabs the nth word and casts it as an integer
        """
        data2 = data[4*(n-1):4*(n-1)+4]
        return struct.unpack('i',data2)[0]
        
    def printSection(self,nBytes):
        """
        prints data, but doesn't move the cursor
        """
        data = self.op2.read(nBytes)
        self.printBlock(data)
        self.op2.seek(self.n)
    
    def skip(self,n):
        """skips nBits"""
        #print "\n--SKIP--"
        #print "tell = ",self.op2.tell()
        #print "n = ",n
        #print "self.n = ",self.n
        self.n += n
        self.op2.seek(self.n)
        #print "*tell = ",self.op2.tell()
        #print "\n"

    def scan(self,n):
        """same as skip, but actually reads the data instead of using seek"""
        data = self.op2.read(n)
        self.n+=n

    def getTableCode(self,expected=None):
        tableCode = self.readHeader(expected)
        return tableCode

    def getMarker(self,expected=None):
        tableCode = self.readHeader(expected)
        return tableCode
        
    def readMarkers(self,markers):
        """
        reads a set of predefined markers e.g. [-4,1,0]
        and makes sure it is correct
        """
        for marker in markers:
            tableCode = self.readHeader(marker)
            assert marker==tableCode
        ###
        print ""

    def getNMarkers(self,nMarkers,rewind=False):
        """gets the next N markers, verifies they're correct"""
        markers = []
        for iMarker in range(nMarkers):
            tableCode = self.readHeader(None)
            markers.append(tableCode)
        ###
        if rewind:
            self.n -= 12*nMarkers
            self.op2.seek(self.n)
            
        return markers

    def isTableDone(self,expectedMarkers):
        markers = self.getNMarkers(len(expectedMarkers),rewind=True)
        print "getMarkers = ",markers

        if markers==[-1,7]:
            return True
        elif markers==expectedMarkers:
            return False
        else:
            raise RuntimeError('this should never happen...invalid markers...expected=%s markers=%s' %(expectedMarkers,markers))

    def goto(self,n):
        self.op2.seek(n)

    def readBlock(self):
        """
        reads a fortran formatted data block
        nWords  data1 data2 data3 nWords
        """
        data = self.op2.read(4)
        nValues, = unpack('i',data)
        self.n+=4
        data = self.op2.read(nValues)
        self.n+=nValues+4
        self.goto(self.n)
        return data

    def readStringBlock(self):
        """
        reads a fortran formatted block
        assumes that the data is made up of characters only
        """
        data = self.readBlock()
        nLetters = len(data)
        letters = unpack('s'*nLetters,data)
        word = ''.join(letters)
        #print "word = |%s|" %(word)
        return word

    def readIntBlock(self):
        """
        reads a fortran formatted block
        assumes that the data is made up of integers only
        """
        data = self.readBlock()
        nInts = len(data)/4
        print "**nInts = ",nInts
        ints = unpack('i'*nInts,data)
        return ints

    def readFloatBlock(self):
        """
        reads a fortran formatted block
        assumes that the data is made up of floats only
        """
        data = self.readBlock()
        nFloats = len(data)/4
        floats = unpack('f'*nFloats,data)
        return floats

    def readDoubleBlock(self):
        """
        reads a fortran formatted block
        assumes that the data is made up of doubles only
        """
        data = self.readBlock()
        nDoubles = len(data)/8
        doubles = unpack('d'*nDoubles,data)
        return doubles

    def rewind(self,n):
        """
        rewinds the file nBytes
        @warning
            doesnt support a full rewind, only a partial
        """
        self.n -= n
        self.op2.seek(self.n)

    def readTableName(self,rewind=True):
        """
        peeks into a table to check it's name
        """
        n = self.n
        #print ""
        self.readMarkers([0,2])
        word = self.readStringBlock()  # GEOM1
        #print "*word = |%r|" %(word)

        #print "n      = ",n
        #print "self.n = ",self.n
        #print "op2.tell = ",self.op2.tell()
        #print "******"
        if rewind:
            self.n = n
            self.op2.seek(n)
        #print "n      = ",n
        #print "self.n = ",self.n
        #print "op2.tell = ",self.op2.tell()
        return word.strip()

    def skipNextTable(self,bufferSize=10000):
        """
        skips a table
        @todo fix bugs
        """
        word = self.readTableName(rewind=False) # GEOM1
        print "skippingTable |%s|" %(word)

        self.readMarkers([-1,7])
        
        dataPack = (4,1,4,  4,0,4,  4,0,4)  # marks the end of the table
        binaryData = pack('iiiiiiiii',*dataPack)
        #[1,0,0] marks the end of the table
        
        i = 0
        error = 50
        n = self.n
        endIndex = -1
        data = "dummy"
        while endIndex== -1 and len(data)>0:
            data     = self.op2.read(bufferSize+error)
            endIndex = data.find(binaryData)
            
            self.op2.seek(n+i*bufferSize)
            i+=1
        
        print "i = ",i
        assert endIndex>0,'couldnt find the end of the table'
        self.n = self.n+(i-1)*bufferSize + endIndex # 36 so it gets to the end of the table markersNext=[0] or [2]
        
        n = self.n
        self.n += 36  ## @todo sometimes this is needed
        #ints = self.readIntBlock()
        #print "*?*ints = ",ints
        #if len(ints)==0:
        #    pass

        self.op2.seek(self.n)
        "self.op2.tell() = ",self.op2.tell()
        self.printSection(200)
        marker = self.getMarker()
        print "marker = ",marker
        if marker==2:
            isAnotherTable = True
        else:# marker=0
            isAnotherTable = False
        ###
        #print "isAnotherTable = ",isAnotherTable
        self.n -= 24  # subtract off the header [0,2] or [0,0]
        self.op2.seek(self.n)
        return isAnotherTable

    def hasMoreTables(self):
        print self.printSection(120)
        try:
            marker1 = self.getMarker()
            marker2 = self.getMarker()
            marker = [marker1,marker2]
            print "marker = ",marker
            if marker==[0,2]:
                isAnotherTable = True
            else:# marker=0
                isAnotherTable = False
            ###
            #print "isAnotherTable = ",isAnotherTable
            self.n -= 24  # subtract off the header [0,2] or [0,0]
            self.op2.seek(self.n)
        except IndexError:
            isAnotherTable = False
        return isAnotherTable
    