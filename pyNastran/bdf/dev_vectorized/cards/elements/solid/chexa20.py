from six.moves import zip
from numpy import zeros, arange, dot, cross, searchsorted, array, asarray
from numpy.linalg import norm

from pyNastran.bdf.fieldWriter import print_card_8
from pyNastran.bdf.bdfInterface.assign_type import (integer, integer_or_blank,
    double_or_blank, integer_double_or_blank, blank)

from pyNastran.bdf.dev_vectorized.cards.elements.solid.chexa8 import quad_area_centroid, volume8
from pyNastran.bdf.dev_vectorized.cards.elements.solid.solid_element import SolidElement

class CHEXA20(SolidElement):
    type = 'CHEXA20'
    nnodes = 20
    def __init__(self, model):
        """
        Defines the CHEXA object.

        :param self: the CHEXA object
        :param model: the BDF object
        """
        SolidElement.__init__(self, model)

    def add(self, card, comment=''):
        i = self.i
        #comment = self._comments[i]
        eid = integer(card, 1, 'element_id')
        #if comment:
            #self._comments[eid] = comment

        #: Element ID
        self.element_id[i] = eid
        #: Property ID
        self.property_id[i] = integer(card, 2, 'property_id')
        #: Node IDs
        nids = array([
            integer(card, 3, 'node_id_1'), integer(card, 4, 'node_id_2'),
            integer(card, 5, 'node_id_3'), integer(card, 6, 'node_id_4'),
            integer(card, 7, 'node_id_5'), integer(card, 8, 'node_id_6'),
            integer(card, 9, 'node_id_7'), integer(card, 10, 'node_id_8'),
            integer_or_blank(card, 11, 'node_id_9', 0),
            integer_or_blank(card, 12, 'node_id_10', 0),
            integer_or_blank(card, 13, 'node_id_11', 0),
            integer_or_blank(card, 14, 'node_id_12', 0),
            integer_or_blank(card, 15, 'node_id_13', 0),
            integer_or_blank(card, 16, 'node_id_14', 0),
            integer_or_blank(card, 17, 'node_id_15', 0),
            integer_or_blank(card, 18, 'node_id_16', 0),
            integer_or_blank(card, 19, 'node_id_17', 0),
            integer_or_blank(card, 20, 'node_id_18', 0),
            integer_or_blank(card, 21, 'node_id_19', 0),
            integer_or_blank(card, 22, 'node_id_20', 0)
        ], dtype='int32')
        self.node_ids[i, :] = nids
        assert len(card) <= 23, 'len(CHEXA20 card) = %i' % len(card)
        self.i += 1

    def build(self):
        if self.n:
            i = self.element_id.argsort()
            self.element_id = self.element_id[i]
            self.property_id = self.property_id[i]
            self.node_ids = self.node_ids[i, :]
            self._cards = []
            self._comments = []
        else:
            self.element_id = array([], dtype='int32')
            self.property_id = array([], dtype='int32')

    def get_mass_matrix(self, i, model, positions, index0s):
        nnodes = 8
        ndof = 3 * nnodes
        pid = self.property_id[i]
        rho = self.model.elements.properties_solid.psolid.get_density_by_property_id(pid)[0]

        n0, n1, n2, n3, n4, n5, n6, n7 = self.node_ids[i, :]
        V = volume8(positions[self.node_ids[i, 0]],
                    positions[self.node_ids[i, 1]],
                    positions[self.node_ids[i, 2]],
                    positions[self.node_ids[i, 3]],

                    positions[self.node_ids[i, 4]],
                    positions[self.node_ids[i, 5]],
                    positions[self.node_ids[i, 6]],
                    positions[self.node_ids[i, 7]],
                    )

        mass = rho * V
        if is_lumped:
            mi = mass / 4.
            nnodes = 4
            M = eye(ndof, dtype='float32')
        else:
            mi = mass / 20.
            M = ones((ndof, ndof), dtype='float32')
            for i in range(nnodes):
                j = i * 3
                M[j:j+3, j:j+3] = 2.
        M *= mi
        dofs, nijv = self.get_dofs_nijv(index0s, n0, n1, n2, n3, n4, n5, n6, n7)
        return M, dofs, nijv

    def get_stiffness_matrix(self, i, model, positions, index0s):
        return K, dofs, nijv

    def get_dofs_nijv(self, index0s, n0, n1, n2, n3, n4, n5, n6, n7):
        i0 = index0s[n0]
        i1 = index0s[n1]
        i2 = index0s[n2]
        i3 = index0s[n3]
        i4 = index0s[n4]
        i5 = index0s[n5]
        i6 = index0s[n6]
        i7 = index0s[n7]
        dofs = array([
            i0, i0+1, i0+2,
            i1, i1+1, i1+2,
            i2, i2+1, i2+2,
            i3, i3+1, i3+2,
            i4, i4+1, i4+2,
            i5, i5+1, i5+2,
            i6, i6+1, i6+2,
            i7, i7+1, i7+2,
        ], 'int32')
        nijv = [
            # translation
            (n0, 1), (n0, 2), (n0, 3),
            (n1, 1), (n1, 2), (n1, 3),
            (n2, 1), (n2, 2), (n2, 3),
            (n3, 1), (n3, 2), (n3, 3),
            (n4, 1), (n4, 2), (n4, 3),
            (n5, 1), (n5, 2), (n5, 3),
            (n6, 1), (n6, 2), (n6, 3),
            (n7, 1), (n7, 2), (n7, 3),
        ]
        return dofs, nijv

    def _verify(self, xref=True):
        eid = self.Eid()
        pid = self.Pid()
        nids = self.nodeIDs()
        assert isinstance(eid, int)
        assert isinstance(pid, int)
        for i,nid in enumerate(nids):
            assert isinstance(nid, int), 'nid%i is not an integer; nid=%s' %(i, nid)
        if xref:
            c = self.centroid()
            v = self.volume()
            assert isinstance(v, float)
            for i in range(3):
                assert isinstance(c[i], float)


    def get_node_indicies(self, i=None):
        if i is None:
            i1 = self.model.grid.get_node_index_by_node_id(self.node_ids[:, 0])
            i2 = self.model.grid.get_node_index_by_node_id(self.node_ids[:, 1])
            i3 = self.model.grid.get_node_index_by_node_id(self.node_ids[:, 2])
            i4 = self.model.grid.get_node_index_by_node_id(self.node_ids[:, 3])
            i5 = self.model.grid.get_node_index_by_node_id(self.node_ids[:, 4])
            i6 = self.model.grid.get_node_index_by_node_id(self.node_ids[:, 5])
            i7 = self.model.grid.get_node_index_by_node_id(self.node_ids[:, 6])
            i8 = self.model.grid.get_node_index_by_node_id(self.node_ids[:, 7])
        else:
            i1 = self.model.grid.get_node_index_by_node_id(self.node_ids[i, 0])
            i2 = self.model.grid.get_node_index_by_node_id(self.node_ids[i, 1])
            i3 = self.model.grid.get_node_index_by_node_id(self.node_ids[i, 2])
            i4 = self.model.grid.get_node_index_by_node_id(self.node_ids[i, 3])
            i5 = self.model.grid.get_node_index_by_node_id(self.node_ids[i, 4])
            i6 = self.model.grid.get_node_index_by_node_id(self.node_ids[i, 5])
            i7 = self.model.grid.get_node_index_by_node_id(self.node_ids[i, 6])
            i8 = self.model.grid.get_node_index_by_node_id(self.node_ids[i, 7])
        return i1, i2, i3, i4, i5, i6, i7, i8

    def _get_node_locations_by_index(self, i, xyz_cid0):
        """
        :param i:        None or an array of node IDs
        :param xyz_cid0: the node positions as a dictionary
        """
        grid = self.model.grid
        get_node_index_by_node_id = self.model.grid.get_node_index_by_node_id
        node_ids = self.node_ids

        msg = ', which is required by %s' % self.type
        i1, i2, i3, i4, i5, i6, i7, i8 = self.get_node_indicies(i)
        n1 = xyz_cid0[i1, :]
        n2 = xyz_cid0[i2, :]
        n3 = xyz_cid0[i3, :]
        n4 = xyz_cid0[i4, :]
        n5 = xyz_cid0[i5, :]
        n6 = xyz_cid0[i6, :]
        n7 = xyz_cid0[i7, :]
        n8 = xyz_cid0[i8, :]
        return n1, n2, n3, n4, n5, n6, n7, n8

    def get_volume_by_element_id(self, element_id=None, xyz_cid0=None, total=False):
        """
        Gets the volume for one or more elements.

        :param element_id: the elements to consider (default=None -> all)
        :param xyz_cid0: the positions of the GRIDs in CID=0 (default=None)
        :param total: should the volume be summed (default=False)

        ..note:: Volume for a CHEXA is the average area of two opposing faces
        times the length between the centroids of those points
        """
        n1, n2, n3, n4, n5, n6, n7, n8 = self._get_node_locations_by_element_id(element_id, xyz_cid0)
        volume = volume8(n1, n2, n3, n4, n5, n6, n7, n8)
        if total:
            volume = abs(volume).sum()
        else:
            volume = abs(volume)
        return volume

    def get_centroid_volume(self, element_id=None, xyz_cid0=None, total=False):
        """
        Gets the centroid and volume for one or more elements.

        :param element_id: the elements to consider (default=None -> all)
        :param xyz_cid0: the positions of the GRIDs in CID=0 (default=None)
        :param total: should the volume be summed; centroid be averaged (default=False)

        ..see:: CHEXA20.get_volume_by_element_id() and CHEXA20.get_centroid_by_element_id() for more information.
        """
        n1, n2, n3, n4, n5, n6, n7, n8 = self._get_node_locations_by_element_id(element_id, xyz_cid0)
        (A1, c1) = quad_area_centroid(n1, n2, n3, n4)
        (A2, c2) = quad_area_centroid(n5, n6, n7, n8)
        centroid = (c1 * A1 + c2 * A2) / (A1 + A2)
        volume = (A1 + A2) / 2. * norm(c1 - c2, axis=1)
        if total:
            centroid = centroid.mean()
            volume = abs(volume).sum()
        else:
            volume = abs(volume)
        assert volume.min() > 0.0, 'volume.min() = %f' % volume.min()
        return centroid, volume

    def get_centroid_by_element_id(self, element_id=None, xyz_cid0=None, total=False):
        """
        Gets the centroid for one or more elements.

        :param element_id: the elements to consider (default=None -> all)
        :param xyz_cid0: the positions of the GRIDs in CID=0 (default=None)
        :param total: should the centroid be averaged (default=False)
        """
        n1, n2, n3, n4, n5, n6, n7, n8 = self._get_node_locations_by_element_id(element_id, xyz_cid0)
        (A1, c1) = quad_area_centroid(n1, n2, n3, n4)
        (A2, c2) = quad_area_centroid(n5, n6, n7, n8)
        centroid = (c1 * A1 + c2 * A2) / (A1 + A2)
        if total:
            centroid = centroid.mean(axis=0)
        return centroid

    def get_face_nodes(self, nid, nid_opposite):
        raise NotImplementedError()
        nids = self.nodeIDs()[:4]
        indx = nids.index(nid_opposite)
        nids.pop(indx)
        return nids

    def write_bdf(self, f, size=8, element_id=None):
        if self.n:
            if element_id is None:
                i = arange(self.n)
            else:
                i = searchsorted(self.element_id, element_id)

            for (eid, pid, n) in zip(self.element_id[i], self.property_id[i], self.node_ids[i]):
                n = [ni if ni != 0 else None for ni in n]
                card = ['CHEXA', eid, pid, n[0], n[1], n[2], n[3], n[4], n[5], n[6], n[7], n[8], n[9],
                        n[10], n[11], n[12], n[13], n[14], n[15], n[16], n[17], n[18], n[19]]
                f.write(print_card_8(card))

