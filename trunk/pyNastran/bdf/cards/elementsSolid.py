from numpy import dot, cross
from elements import Element

class SolidElement(Element):
    def __init__(self,card):
        Element.__init__(self,card)
        self.eid = card.field(1)
        self.pid = card.field(2)

    def crossReference(self,mesh):
        self.nodes = mesh.Nodes(self.nodes)
        self.pid   = mesh.Property(self.pid)

class CHEXA8(SolidElement):
    """
    CHEXA EID PID G1 G2 G3 G4 G5 G6
    G7 G8
    """
    type = 'CHEXA'
    def __init__(self,card):
        SolidElement.__init__(self,card)
        #print "hexa = ",card
        nids = card.fields(3,11)
        #print "nids = ",nids
        self.prepareNodeIDs(nids)
        assert len(self.nodes)==8

class CHEXA20(CHEXA8):
    """
    CHEXA EID PID G1 G2 G3 G4 G5 G6
    G7 G8 G9 G10 G11 G12 G13 G14
    G15 G16 G17 G18 G19 G20
    """
    type = 'CHEXA'
    def __init__(self,card):
        SolidElement.__init__(self,card)

        nids = card.fields(3,23)
        self.prepareNodeIDs(nids,allowEmptyNodes=True)
        msg = 'len(nids)=%s nids=%s' %(len(nids),nids)
        assert len(self.nodes)<=20,msg

class CPENTA6(SolidElement):
    """
    CPENTA EID PID G1 G2 G3 G4 G5 G6
    """
    type = 'CPENTA'
    def __init__(self,card):
        SolidElement.__init__(self,card)

        nids = card.fields(3,9)
        self.prepareNodeIDs(nids)
        assert len(self.nodes)==6

class CPENTA15(CPENTA6):
    """
    CPENTA EID PID G1 G2 G3 G4 G5 G6
    G7 G8 G9 G10 G11 G12 G13 G14
    G15
    """
    type = 'CPENTA'
    def __init__(self,card):
        SolidElement.__init__(self,card)

        nids = card.fields(3,18)
        self.prepareNodeIDs(nids,allowEmptyNodes=True)
        assert len(self.nodes)<=15

class CTETRA4(SolidElement):
    """
    CTETRA EID PID G1 G2 G3 G4
    """
    type = 'CTETRA'
    def __init__(self,card):
        SolidElement.__init__(self,card)
        nids = card.fields(3,7)
        self.prepareNodeIDs(nids)
        assert len(self.nodes)==4

    def volume(self):
        """
        V = (a-d) * ((b-d) x (c-d))/6   where x is cross and * is dot
        """
        (n1,n2,n3,n4) = self.nodePositions()
        V = dot((n1-n4),cross(n2-n4,n3-n4))/6.
        return V

class CTETRA10(CTETRA4):
    """
    CTETRA EID PID G1 G2 G3 G4 G5 G6
    G7 G8 G9 G10
    CTETRA   1       1       239     229     516     99      335     103
             265     334     101     102
    """
    type = 'CTETRA'
    def __init__(self,card):
        SolidElement.__init__(self,card)
        nids = card.fields(3,13)
        self.prepareNodeIDs(nids,allowEmptyNodes=True)
        assert len(self.nodes)<=10
