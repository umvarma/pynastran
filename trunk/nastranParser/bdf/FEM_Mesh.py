import os
import sys
import copy
from math import ceil

# 3rd party
import numpy
from numpy import any,cross

# my code
from fieldWriter import printCard
from cards import * # reads all the card types - GRID, CQUAD4, FORCE, PSHELL, etc.
#from mathFunctions import *

from bdf_helper import getMethods,addMethods,writeMesh,cardMethods,BDF_Card

class Subcase(object):
    def __init__(self,id=0,params={}):
        self.id = id
        self.params = params
        self.sol = None
        #print "\n***adding subcase %s***" %(self.id)

    def addData(self,key,value,options,paramType):
        self.params[key] = [value,options,paramType]

    def printParam(self,key,param,printBeginBulk=True):
        """
        Prints a single entry of the a subcase from the global or local
        subcase list.
        @todo SET-type is not supported yet...
        """
        msg = ''
        (value,options,paramType) = param
        
        spaces = '    '*self.id
        if paramType=='SUBCASE-type':
            if self.id>0:
                msg += 'SUBCASE %s\n' %(self.id)
            ###
            #else:  global subcase ID=0 and is not printed
            #    pass
        elif paramType=='PARAM-type':
            msg += spaces+'%s,%s,%s\n' %(key,value,options)
        elif paramType=='STRESS-type':
            sOptions = ','.join(options)
            #print "sOptions = |%s|" %(sOptions)
            if len(sOptions)>0:
                msg += '%s(%s) = %s\n' %(key,sOptions,value)
            else:
                msg += '%s = %s\n' %(key,value)
            msg = spaces + msg

        elif paramType=='BEGIN_BULK-type':
            msg += '%s %s\n' %(key,value)
            if 'BEGIN BULK' not in msg:
                msg = spaces + msg
            elif printBeginBulk:
                pass
            else:
                msg = ''
            ###
        else:
            raise Exception((key,param))  # SET-type is not supported yet...
        ###
        #print "msg = |%r|" %(msg)
        return msg

    def __repr__(self):
        #print "-------SUBCASE %s-------" %(self.id)
        msg = ''
        for (key,param) in sorted(self.params.items()):
            if 'key'=='BEGIN':
                continue
            else:
                #print "key=%s param=%s" %(key,param)
                (value,options,paramType) = param
                #print "  *key=|%s| value=|%s| options=%s paramType=|%s|" %(key,value,options,paramType)
                msg += self.printParam(key,param,printBeginBulk=False)
                #print ""
            ###
        ###
        if self.id>0 and 'BEGIN' in self.params:
            msg += self.printParam('BEGIN',self.params['BEGIN'])
        return msg

class CaseControlDeck(object):
    def __init__(self,lines,log=None):
        self.log = log
        self.lines = lines
        self.subcases = {0:Subcase(id=0)}
        self.iSubcase = 0
        self.read()

    def read(self):
        i = 0
        lines = self.lines
        while i < len(lines):
            line = lines[i].strip()
            #print "rawLine = |%s|" %(line)
            options = []
            value = None
            key = None
            paramType = None

            if 'SUBCASE' in line:
                (subcase,iSubcase) = line.split(' ')
                self.iSubcase = int(iSubcase)
                paramType = 'SUBCASE-type'
            elif '=' in line: # TITLE, STRESS
                (key,value) = line.strip().split('=')
                key   = key.strip()
                value = value.strip()
                #print "key=|%s| value=|%s|" %(key,value)
                paramType = 'STRESS-type'

                if '(' in key:  # comma may be in line - STRESS
                    sline = key.strip(')').split('(')
                    key = sline[0]
                    options = sline[1].split(',')
                    #print "key=|%s| options=%s" %(key,options)
                    paramType = 'STRESS-type'
                elif ' ' in key and ',' in value: # set
                    (key,ID) = key.split()
                    fivalues = value.split(',') # float/int values
                    
                    # read more lines....
                    if line[-1]==',':
                        i+=1
                        while lines[i]==',':
                            fivalues += lines.split(',')
                            i+=1
                        ###
                    ###
                    value = fivalues
                    paramType = 'SET-type'
                elif ',' in value: # special TITLE = stuffA,stuffB
                    print 'A ??? line = ',line
                    raise Exception(line)
                else:  # TITLE = stuff
                    #print 'B ??? line = ',line
                    pass
                ###
            ### = in line
            elif ',' in line: # param
                (key,value,options) = line.strip().split(',')
                paramType = 'PARAM-type'
            elif ' ' in line: # begin bulk
                (key,value) = line.strip().split(' ')
                paramType = 'BEGIN_BULK-type'
            else:
                print 'C ??? line = ',line
                raise Exception(line)
            ###
            i+=1
            #print "key=|%s| value=|%s| options=|%s| paramType=%s" %(key,value,options,paramType)
            self.addParameterToSubcase(key,value,options,paramType)
            #print "--------------"
        ###
        print "done with while loop...\n"
        
        #print str(self)
        #sys.exit('stopping...')
    ###

    def addParameterToSubcase(self,key,value,options,paramType):
        #print "adding key=|%s| value=|%s| options=|%s| paramType=%s" %(key,value,options,paramType)
        if self.iSubcase not in self.subcases: # initialize new subcase
            #self.iSubcase += 1
            self.subcases[self.iSubcase] = Subcase(id=self.iSubcase)

        subcase = self.subcases[self.iSubcase]
        subcase.addData(key,value,options,paramType)

    def __repr__(self):
        msg = ''
        for (iSubcase,subcase) in sorted(self.subcases.items()):
            msg += str(subcase)
            #print "\n"
        return msg
###

class FEM_Mesh(getMethods,addMethods,writeMesh,cardMethods):
    modelType = 'nastran'
    isStructured = False
    
    def setCardsToInclude():
        pass

    def __init__(self,infilename,log=None):
        if log is None:
            from nastranParser.general.logger import dummyLogger
            loggerObj = dummyLogger()
            log = loggerObj.startLog('debug') # or info

        self.debug = False
        self.log = log
        self.infilename = infilename
        self.isOpened=False
        #self.n = 0
        #self.nCards = 0
        self.doneReading = False
        self.foundEndData = False
        self.constraints = {}
        self.params = {}
        self.nodes = {}
        self.elements = {}
        self.properties = {}
        self.materials = {}
        self.coords = {0: CORD2R() }
        self.loads = {}
        self.rejects = []
        self.rejectCards = []
        self.executiveControlLines = []
        self.caseControlLines = []

        self.cardsToRead = set([
        'PARAM','=',
        'GRID',
        
        'CTRIA3','CQUAD4','CELAS1','CELAS2','CHEXA','CPENTA','CTETRA','CBAR',
        'RBE1','RBE2','RBE3',
        
        'PELAS','PSHELL','PSOLID','PCOMP','PROD', # 'PCOMPG',
        'MAT1','MAT2','MAT3','MAT4','MAT5','MAT8','MAT9',

        'SPC','SPC1','SPCADD','SUPORT1',
        'MPC','MPCADD',

        'FORCE','PLOAD',

        'CORD1R','CORD1C','CORD1S',
        'CORD2R','CORD2C','CORD2S',
        'ENDDATA',
        ])
        self.cardsToWrite = self.cardsToRead

    def openFile(self):
        if self.isOpened==False:
            self.log().info("*FEM_Mesh bdf=|%s|  pwd=|%s|" %(self.infilename,os.getcwd()))
            self.infile = open(self.infilename,'r')
            self.isOpened=True
            self.lines = []

    def closeFile(self):
        self.infile.close()

    def read(self,debug=False):
        self.log().info('---starting FEM_Mesh.read of %s---' %(self.infilename))
        sys.stdout.flush()
        self.debug = debug
        if self.debug:
            self.log().info("*FEM_Mesh.read")
        self.readExecutiveControlDeck()
        self.readCaseControlDeck()
        self.readBulkDataDeck()
        self.crossReference()
        self.closeFile()
        if self.debug:
            self.log().debug("***FEM_Mesh.read")
        self.log().info('---finished FEM_Mesh.read of %s---' %(self.infilename))
        sys.stdout.flush()

    def writeElementsAsCTRIA3(self):
        eids = self.elementIDs()
        #print "eids = ",eids
        nextEID = max(eids)+1  # set the new ID
        msg = '$ELEMENTS\n'
        for key,element in sorted(self.elements.items()):
            if element.Is('CQUAD4'):
                msg += element.writeAsCTRIA3(nextEID)
                nextEID+=1
            else:
                msg += str(element)
            ###
        ###
        return msg

    def write(self,outfilename='fem.out.bdf',debug=False):
        msg  = self.writeHeader()
        msg += self.writeParams()
        msg += self.writeNodes()
        msg += self.writeElements()
        msg += self.writeProperties()
        msg += self.writeMaterials()
        msg += self.writeLoads()
        msg += self.writeConstraints()
        msg += self.writeRejects()
        msg += self.writeCoords()
        msg += 'ENDDATA\n'

        self.log().info("***writing %s" %(outfilename))
        outfile = open(outfilename,'wb')
        outfile.write(msg)
        outfile.close

    def writeAsCTRIA3(self,outfilename='fem.out.bdf',debug=False):
        msg  = self.writeHeader()
        msg += self.writeParams()
        msg += self.writeNodes()
        msg += self.writeElementsAsCTRIA3()
        msg += self.writeProperties()
        msg += self.writeMaterials()
        msg += self.writeLoads()
        msg += self.writeConstraints()
        msg += self.writeRejects()
        msg += self.writeCoords()
        msg += 'ENDDATA\n'

        self.log().info("***writing %s" %(outfilename))
        outfile = open(outfilename,'wb')
        outfile.write(msg)
        outfile.close

    def crossReference(self):
        #print "cross Reference is a temp function"
        #for key,e in self.elements.items():
        #    print(e)
        for key,n in self.nodes.items():
            #print "n.cid = ",n.cid
            coord = self.Coord(n.cid)
            #print "*",str(coord)
            n.crossReference(coord)
        pass
        
    def readExecutiveControlDeck(self):
        self.openFile()
        line = ''
        #self.executiveControlLines = []
        while 'CEND' not in line:
            lineIn = self.infile.readline()
            line = lineIn.strip()
            self.executiveControlLines.append(lineIn)
        return self.executiveControlLines

    def readCaseControlDeck(self):
        self.openFile()
        self.log().info("reading Case Control Deck...")
        line = ''
        #self.caseControlControlLines = []
        while 'BEGIN BULK' not in line:
            lineIn = self.infile.readline()
            line = lineIn.strip().split('$')[0].strip()
            #print "*line = |%s|" %(line)
            self.caseControlLines.append(lineIn)
        self.log().info("finished with Case Control Deck..")
        #print "self.caseControlLines = ",self.caseControlLines
        
        self.caseControlDeck = CaseControlDeck(self.caseControlLines)
        return self.caseControlLines

    def Is(self,card,cardCheck):
        #print "card=%s" %(card)
        #return cardCheck in card[0][0:8]
        return any([cardCheck in field[0:8] for field in card])

    def isPrintable(self,cardName):
        """can the card be printed"""
        #cardName = self.getCardName(card)
        
        if cardName in self.cardsToWrite:
            #print "*card = ",card
            #print "WcardName = |%s|" %(cardName)
            return False
        return True

    def getCardName(self,card):
        #self.log().debug("getting cardName...")
        cardName = card[0][0:8].strip()
        if ',' in cardName:
            cardName = cardName.split(',')[0].strip()
        #self.log().debug("getCardName cardName=|%s|" %(cardName))
        return cardName
    
    def isReject(self,cardName):
        """can the card be read"""
        #cardName = self.getCardName(card)
        if cardName.startswith('='):
            return False
        elif cardName in self.cardsToRead:
            #print "*card = ",card
            #print "RcardName = |%s|" %(cardName)
            return False
        if cardName.strip():
            print "RcardName = |%s|" %(cardName)
        return True

    def readBulkDataDeck(self):
        if self.debug:
            self.log().debug("*readBulkDataDeck")
        self.openFile()
        #self.nodes = {}
        #self.elements = {}
        #self.rejects = []
        
        #oldCardObj = BDF_Card()
        while 1: # keep going until finished
            (card,cardName) = self.getCard(debug=False) # gets the cardLines
            #print "outcard = ",card
            #if cardName=='CQUAD4':
            #    print "card = ",card

            if not self.isReject(cardName):
                #print ""
                #print "not a reject"
                card = self.processCard(card) # parse the card into fields
                #print "processedCard = ",card
            elif card[0].strip()=='':
                #print "funny strip thing..."
                pass
            else:
                #print "reject!"
                self.rejects.append(card)
                continue
                #print " rejecting card = ",card
                #card = self.processCard(card)
                #sys.exit()
            

            #print "card2 = ",ListPrint(card)
            #print "card = ",card
            cardName = self.getCardName(card)
            #self.log().debug('cardName = |%s|' %(cardName))
            
            #cardObj = BDF_Card(card,oldCardObj)
            cardObj = BDF_Card(card)

            nCards = 1
            #special = False
            if '=' in cardName:
                nCards = cardName.strip('=()')
                if nCards:
                    nCards = int(nCards)
                else:
                    nCards = 1
                    #special = True
                #print "nCards = ",nCards
                cardName = oldCardObj.field(0)
            ###

            for iCard in range(nCards):
                #print "----------------------------"
                #if special:
                #    print "iCard = ",iCard
                self.addCard(card,cardName,iCard=0,oldCardObj=None)
                if self.foundEndData:
                    break
            ### iCard
            if self.doneReading or len(self.lines)==0:
                break
            ###
            #oldCardObj = copy.deepcopy(cardObj) # used for =(*1) stuff
            #print ""
        
        #self.debug = True
        if self.debug:
            #for nid,node in self.nodes.items():
            #    print node
            #for eid,element in self.elements.items():
            #    print element
            
            self.log().debug("\n$REJECTS")
            #for reject in self.rejects:
                #print printCard(reject)
                #print ''.join(reject)
            self.log().debug("***readBulkDataDeck")
    
    def addCard(self,card,cardName,iCard=0,oldCardObj=None):
        #if cardName != 'CQUAD4':
        #    print cardName
        if self.debug:
            print "*oldCardObj = \n",oldCardObj
            print "*cardObj = \n",cardObj
        cardObj = BDF_Card(card,oldCardObj=None)
        #cardObj.applyOldFields(iCard)
        try:
            if card==[] or cardName=='':
                pass
            elif cardName=='PARAM':
                param = PARAM(cardObj)
                self.addParam(param)
            elif cardName=='GRID':
                node = GRID(cardObj)
                #print "node.nid = ",node.nid
                self.addNode(node)

            elif cardName=='CQUAD4':
                elem = CQUAD4(cardObj)
                self.addElement(elem)
            elif cardName=='CQUAD8':
                elem = CQUAD8(cardObj)
                self.addElement(elem)

            elif cardName=='CTRIA3':
                elem = CTRIA3(cardObj)
                self.addElement(elem)
            elif cardName=='CTRIA6':
                elem = CTRIA6(cardObj)
                self.addElement(elem)

            elif cardName=='CTETRA':
                elem = CTETRA(cardObj)
                self.addElement(elem)
            elif cardName=='CHEXA':
                elem = CHEXA(cardObj)
                self.addElement(elem)
            elif cardName=='CPENTA':
                elem = CPENTA(cardObj)
                self.addElement(elem)

            elif cardName=='CBAR':
                elem = CBAR(cardObj)
                self.addElement(elem)
            elif cardName=='CBEAM':
                elem = CBEAM(cardObj)
                self.addElement(elem)
            elif cardName=='CROD':
                elem = CROD(cardObj)
                self.addElement(elem)
            elif cardName=='CONROD':
                elem = CONROD(cardObj)
                self.addElement(elem)
                #print str(elem).strip()
            elif cardName=='CTUBE':
                elem = CBAR(cardObj)
                self.addElement(elem)

            elif cardName=='CELAS1':
                elem = CELAS1(cardObj)
                self.addElement(elem)
            elif cardName=='CELAS2':
                (elem,prop) = CELAS2(cardObj)
                self.addElement(elem)
                self.addProperty(prop)
            elif cardName=='CONM2':
                elem = CONM2(cardObj)
                self.addElement(elem)

            elif cardName=='PELAS':
                prop = PELAS(cardObj)
                if cardObj.field(5):
                    prop = PELAS(cardObj,1) # makes 2nd PELAS card
                self.addProperty(prop)
            #elif cardName=='PBEAM':
            #    prop = PBEAM(cardObj)
            #    self.addProperty(prop)
            elif cardName=='PTUBE':
                prop = PTUBE(cardObj)
                self.addProperty(prop)
            elif cardName=='PSHELL':
                prop = PSHELL(cardObj)
                self.addProperty(prop)
            elif cardName=='PCOMP':
                prop = PCOMP(cardObj)
                self.addProperty(prop)
            #elif cardName=='PCOMPG':
            #    prop = PCOMPG(cardObj)
            #    self.addProperty(prop)
            elif cardName=='PSOLID':
                prop = PSOLID(cardObj)
                self.addProperty(prop)
            elif cardName=='PLSOLID':
                prop = PLSOLID(cardObj)
                self.addProperty(prop)

            elif cardName=='MAT1':
                material = MAT1(cardObj)
                self.addMaterial(material)
            #elif cardName=='MAT2':
            #    material = MAT2(cardObj)
            #    self.addMaterial(material)
            #elif cardName=='MAT3':
            #    material = MAT3(cardObj)
            #    self.addMaterial(material)
            #elif cardName=='MAT4':
            #    material = MAT4(cardObj)
            #    self.addMaterial(material)
            #elif cardName=='MAT5':
            #    material = MAT5(cardObj)
            #    self.addMaterial(material)
            elif cardName=='MAT8':
                material = MAT8(cardObj)
                self.addMaterial(material)
            #elif cardName=='MAT9':
            #    material = MAT9(cardObj)
            #    self.addMaterial(material)
            #elif cardName=='MAT10':
            #    material = MAT9(cardObj)
            #    self.addMaterial(material)

            elif cardName=='FORCE':
                #print "fcard = ",card 
                force = FORCE(cardObj)
                self.addLoad(force)
            elif cardName=='LOAD':
                #print "fcard = ",card 
                load = LOAD(cardObj)
                self.addLoad(load)

            elif cardName=='SPCADD':
                constraint = SPCADD(cardObj)
                self.addConstraint(constraint)
            elif cardName=='SPC1':
                #print "card = ",card
                constraint = SPC1(cardObj)
                self.addConstraint(constraint)
            elif cardName=='SUPORT1':
                #print "card = ",card
                constraint = SUPORT1(cardObj)
                self.addConstraint(constraint)
                #print "constraint = ",constraint

            elif cardName=='CORD2R':
                coord = CORD2R(cardObj)
                self.addCoord(coord)
                #print "done with ",card
            elif 'CORD' in cardName:
                raise Exception('unhandled coordinate system...cardName=%s' %(cardName))
            elif 'ENDDATA' in cardName:
                self.foundEndData = True
                #break
            else:
                print 'rejecting processed %s' %(card)
                self.rejectCards.append(card)
            ###
        except:
            print card
            raise
        ### try-except block

    def sumForces(self):
        for key,loadCase in self.loads.items():
            F = array([0.,0.,0.])
            #print "loadCase = ",loadCase
            for load in loadCase:
                #print "load = ",load
                if isinstance(load,FORCE):
                    f = load.mag*load.xyz
                    print "f = ",f
                    F += f
                ###
            self.log().info("case=%s F=%s\n\n" %(key,F))
        ###

    def sumMoments(self):
        p = array([0.,0.5,0.])
        for key,loadCase in self.loads.items():
            M = array([0.,0.,0.])
            F = array([0.,0.,0.])
            #print "loadCase = ",loadCase
            for load in loadCase:
                #print "load = ",load
                if isinstance(load,FORCE):
                    f = load.mag*load.xyz
                    node = self.Node(load.node)
                    #print "node = ",node
                    r = node.Position() - p
                    m = cross(r,f)
                    #print "m    = ",m
                    M += m
                    F += f
                ###
            print "case=%s F=%s M=%s\n\n" %(key,F,M)
        ###

### FEM_Mesh

if __name__=='__main__':
    import sys
    #basepath = os.getcwd()
    #configpath = os.path.join(basepath,'inputs')
    #workpath   = os.path.join(basepath,'outputs')
    #os.chdir(workpath)
    

    #bdfModel   = os.path.join(configpath,'fem.bdf.txt')
    #bdfModel   = os.path.join(configpath,'aeroModel.bdf')
    #bdfModel   = os.path.join('aeroModel_mod.bdf')
    bdfModel   = os.path.join('aeroModel_2.bdf')
    #bdfModel   = os.path.join('hard.bdf')
    #bdfModel   = os.path.join(configpath,'aeroModel_Loads.bdf')
    #bdfModel   = os.path.join(configpath,'test_mesh.bdf')
    #bdfModel   = os.path.join(configpath,'test_tet10.bdf')
    assert os.path.exists(bdfModel),'|%s| doesnt exist' %(bdfModel)
    fem = FEM_Mesh(bdfModel,log=None)
    fem.read()
    #fem.sumForces()
    #fem.sumMoments()
    
    fem.write('fem.out.bdf')
    #fem.writeAsCTRIA3('fem.out.bdf')


