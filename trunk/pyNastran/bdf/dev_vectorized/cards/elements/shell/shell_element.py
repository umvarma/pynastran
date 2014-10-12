import cStringIO
from numpy import zeros, searchsorted, where

class ShellElement(object):
    def __init__(self, model):
        self.model = model
        self.n = 0
        self._cards = []
        self._comments = []

    def __getitem__(self, element_ids):
        """
        Allows for slicing:
         - elements[1:10]
         - elements[4]
         - elements[1:10:2]
         - elements[[1,2,5]]
         - elements[array([1,2,5])]
        """
        i = searchsorted(self.element_id, element_ids)
        return self.slice_by_index(i)

    def __repr__(self):
        f = cStringIO.StringIO()
        f.write('<C%s object> n=%s\n' % (self.type, self.n))
        self.write_bdf(f)
        return f.getvalue()

    def add(self, card, comment):
        self._cards.append(card)
        self._comments.append(comment)

    def get_mass(self, element_ids=None, total=False, node_ids=None, xyz_cid0=None):
        """
        Gets the mass of the CQUAD4s on a total or per element basis.

        :param self: the CQUAD4 object
        :param element_ids: the elements to consider (default=None -> all)
        :param total: should the mass be summed (default=False)

        :param xyz_cid0: the GRIDs as an (N, 3) NDARRAY in CORD2R=0 (or None)

        ..note:: If node_ids is None, the positions of all the GRID cards
                 must be calculated
        """
        mass, _area, _normal = self._mass_area_normal(element_ids=element_ids,
            xyz_cid0=xyz_cid0,
            calculate_mass=True, calculate_area=False,
            calculate_normal=False)

        if total:
            return mass.sum()
        else:
            #print('mass.shape = %s' % mass.shape)
            return mass

    def get_normal(self, element_ids=None, xyz_cid0=None):
        """
        Gets the normals of the CQUAD4s on per element basis.

        :param self: the CQUAD4 object
        :param element_ids: the elements to consider (default=None -> all)

        :param xyz_cid0: the GRIDs as an (N, 3) NDARRAY in CORD2R=0 (or None)

        ..note:: If node_ids is None, the positions of all the GRID cards
                 must be calculated
        """
        _mass, area, normal = self._mass_area_normal(element_ids=element_ids,
            xyz_cid0=xyz_cid0,
            calculate_mass=False, calculate_area=False,
            calculate_normal=True)
        return normal

    def get_area(self, element_ids=None, total=False, xyz_cid0=None):
        """
        Gets the area of the CQUAD4s on a total or per element basis.

        :param self: the CQUAD4 object
        :param element_ids: the elements to consider (default=None -> all)
        :param total: should the area be summed (default=False)

        :param node_ids:   the GRIDs as an (N, )  NDARRAY (or None)
        :param grids_cid0: the GRIDs as an (N, 3) NDARRAY in CORD2R=0 (or None)

        ..note:: If node_ids is None, the positions of all the GRID cards
                 must be calculated
        """
        _mass, area, _normal = self._mass_area_normal(element_ids=element_ids,
            xyz_cid0=xyz_cid0,
            calculate_mass=False, calculate_area=True,
            calculate_normal=False)
        if total:
            return area.sum()
        else:
            return area

    def get_thickness(self, element_ids=None):
        if element_ids is None:
            element_ids = self.element_id
            property_id = self.property_id
            i = None
        else:
            i = searchsorted(self.element_id, element_ids)
            property_id = self.property_id[i]
        #print 'element_ids =', element_ids
        #print 'property_ids =', property_id
        t = self.model.properties_shell.get_thickness(property_id)
        return t

    def get_nonstructural_mass(self, element_ids=None):
        if element_ids is None:
            element_ids = self.element_id
            property_id = self.property_id
            i = None
        else:
            i = searchsorted(self.element_id, element_ids)
            property_id = self.property_id[i]
        nsm = self.model.properties_shell.get_nonstructural_mass(property_id)
        return nsm

    def get_density(self, element_ids=None):
        if element_ids is None:
            element_ids = self.element_id
            property_id = self.property_id
            i = None
        else:
            i = searchsorted(self.element_id, element_ids)
            property_id = self.property_id[i]
        #print('density - element_ids = %s' % element_ids)
        density = self.model.properties_shell.get_density(property_id)
        #print('density_out = %s' % density)
        return density

