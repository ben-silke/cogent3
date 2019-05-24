#!/usr/bin/env python
"""Tests of the geometry package."""
from numpy import array, take, ones, allclose, isclose, sum, arange, insert, all, mean
from numpy.linalg import norm, inv
from numpy.random import dirichlet, choice
from numpy.testing import assert_allclose
from math import sqrt
from cogent3.util.unit_test import TestCase, main
from cogent3.maths.geometry import center_of_mass_one_array, \
    center_of_mass_two_array, center_of_mass, distance, sphere_points, \
    SimplexTransform, alr, clr, alr_inv, clr_inv, aitchison_distance, \
    multiplicative_replacement, tight_simplex


__author__ = "Sandra Smit"
__copyright__ = "Copyright 2007-2016, The Cogent Project"
__credits__ = ["Sandra Smit", "Rob Knight", "Helmut Simon"]
__license__ = "GPL"
__version__ = "3.0a2"
__maintainer__ = "Sandra Smit"
__email__ = "sandra.smit@colorado.edu"
__status__ = "Production"


class CenterOfMassTests(TestCase):
    """Tests for the center of mass functions"""

    def setUp(self):
        """setUp for all CenterOfMass tests"""
        self.simple = array([[1, 1, 1], [3, 1, 1], [2, 3, 2]])
        self.simple_list = [[1, 1, 1], [3, 1, 1], [2, 3, 2]]
        self.more_weight = array([[1, 1, 3], [3, 1, 3], [2, 3, 50]])
        self.square = array([[1, 1, 25], [3, 1, 25], [3, 3, 25], [1, 3, 25]])
        self.square_odd = array([[1, 1, 25], [3, 1, 4], [3, 3, 25], [1, 3, 4]])
        self.sec_weight = array(
            [[1, 25, 1], [3, 25, 1], [3, 25, 3], [1, 25, 3]])

    def test_center_of_mass_one_array(self):
        """center_of_mass_one_array should behave correctly"""
        com1 = center_of_mass_one_array
        self.assertEqual(com1(self.simple), array([2, 2]))
        self.assertEqual(com1(self.simple_list), array([2, 2]))
        self.assertFloatEqual(com1(self.more_weight), array([2, 2.785714]))
        self.assertEqual(com1(self.square), array([2, 2]))
        self.assertEqual(com1(self.square_odd), array([2, 2]))
        self.assertEqual(com1(self.sec_weight, 1), array([2, 2]))

    def test_CoM_one_array_wrong(self):
        """center_of_mass_one_array should fail on wrong input"""
        com1 = center_of_mass_one_array
        self.assertRaises(TypeError, com1, self.simple,
                          'a')  # weight_idx wrong
        self.assertRaises(IndexError, com1, self.simple,
                          100)  # w_idx out of range
        # shape[1] out of range
        self.assertRaises(IndexError, com1, [1, 2, 3], 2)

    def test_center_of_mass_two_array(self):
        """center_of_mass_two_array should behave correctly"""
        com2 = center_of_mass_two_array
        coor = take(self.square_odd, (0, 1), 1)
        weights = take(self.square_odd, (2,), 1)
        self.assertEqual(com2(coor, weights), array([2, 2]))
        weights = weights.ravel()
        self.assertEqual(com2(coor, weights), array([2, 2]))

    def test_CoM_two_array_wrong(self):
        """center_of_mass_two_array should fail on wrong input"""
        com2 = center_of_mass_two_array
        weights = [1, 2]
        self.assertRaises(TypeError, com2, self.simple,
                          'a')  # weight_idx wrong
        self.assertRaises(ValueError, com2, self.simple,
                          weights)  # not aligned

    def test_center_of_mass(self):
        """center_of_mass should make right choice between functional methods
        """
        com = center_of_mass
        com1 = center_of_mass_one_array
        com2 = center_of_mass_two_array
        self.assertEqual(com(self.simple), com1(self.simple))
        self.assertFloatEqual(com(self.more_weight), com1(self.more_weight))
        self.assertEqual(com(self.sec_weight, 1), com1(self.sec_weight, 1))
        coor = take(self.square_odd, (0, 1), 1)
        weights = take(self.square_odd, (2,), 1)
        self.assertEqual(com(coor, weights), com2(coor, weights))
        weights = weights.ravel()
        self.assertEqual(com(coor, weights), com2(coor, weights))

    def test_distance(self):
        """distance should return Euclidean distance correctly."""
        # for single dimension, should return difference
        a1 = array([3])
        a2 = array([-1])
        self.assertEqual(distance(a1, a2), 4)
        # for two dimensions, should work e.g. for 3, 4, 5 triangle
        a1 = array([0, 0])
        a2 = array([3, 4])
        self.assertEqual(distance(a1, a2), 5)
        # vector should be the same as itself for any dimensions
        a1 = array([1.3, 23, 5.4, 2.6, -1.2])
        self.assertEqual(distance(a1, a1), 0)
        # should match hand-calculated case for an array
        a1 = array([[1, -2], [3, 4]])
        a2 = array([[1, 0], [-1, 2.5]])
        self.assertEqual(distance(a1, a1), 0)
        self.assertEqual(distance(a2, a2), 0)
        self.assertEqual(distance(a1, a2), distance(a2, a1))
        self.assertFloatEqual(distance(a1, a2), sqrt(22.25))

    def test_sphere_points(self):
        """tests sphere points"""
        self.assertEqual(sphere_points(1), array([[1., 0., 0.]]))

#    def test_coords_to_symmetry(self):
#        """tests symmetry expansion (TODO)"""
#        pass
#
#    def test_coords_to_crystal(self):
#        """tests crystal expansion (TODO)"""
#        pass

class TestSimplexTransform(TestCase):
    transform = SimplexTransform()

    def test_get_simplex_transform(self):
        """distance between points on standard simplex
        is  conserved under transform."""
        alpha = ones(4)
        y = dirichlet(alpha)
        z = dirichlet(alpha)

        y1 = y @ self.transform
        z1 = z @ self.transform
        assert_allclose(norm(y - z), norm(y1 - z1))

    def test_vertices(self):
        """length of any edge under transform is conserved as sqrt(2)."""
        x = array([1, 0, 0, 0], dtype=float)
        a = x @ self.transform
        x = array([0, 1, 0, 0], dtype=float)
        b = x @ self.transform
        x = array([0, 0, 1, 0], dtype=float)
        c = x @ self.transform
        x = array([0, 0, 0, 1], dtype=float)
        d = x @ self.transform
        assert_allclose(array([norm(a-b), norm(a-c), norm(a-d),
            norm(b-c), norm(b-d), norm(c-d)]), sqrt(2) * ones(6))


class TestAitchison(TestCase):
    def setUp(self):
        x = choice(20, size=10) + 0.1
        self.x = x
        a = arange(1, 7)
        self.a = a
        d = dirichlet(a, size=2)
        self.d = d

    def test_Aitchison_transforms(self):
        """Test that alr_inv of alr is in fact the inverse
        of alr. Ditto for clr_inv and clr. Then test that clr
        transforms into hyperplane x1 + ... + xn=0."""
        length = len(self.x)
        for col in range(-1, length):
            y = alr_inv(self.x, col)
            assert allclose(self.x, alr(y, col)), \
                'Failed alr inverse test for col = ' + str(col) + '.'

        z = dirichlet(self.x)
        y = clr(z)
        assert allclose(z, clr_inv(y)), 'Failed clr inverse test.'
        assert allclose(sum(y), 0), 'Failed clr hyperplane test.'

    def test_Aitchison_distance(self):
        x = self.d[0]
        y = self.d[1]
        assert allclose(aitchison_distance(x, y), \
                           norm(clr(x) - clr(y))), 'Failed distance test.'

    def test_multiplicative_replacement(self):
        x1 = dirichlet(self.a)
        y1 = insert(x1, 3, 0)
        u = multiplicative_replacement(y1)
        assert allclose(y1, u, atol=1e-2), \
            'Multiplicative replacement peturbation is too large.'
        assert isclose(sum(u), 1), \
            'Multiplicative replacement does not yield a composition.'


class TestTightSimplex(TestCase):
    def setUp(self):
        x = dirichlet(100 * ones(4), 5)
        self.x = x
        vertices = tight_simplex(x)
        self.vertices = vertices

    def test_vertices(self):
        """Vertices lie within unit simplex, edges are equal in length and align
        with unit simplex."""
        vertices = self.vertices
        assert_allclose(sum(vertices, axis=1), ones(4), err_msg='Vertices not in unit simplex.')
        l = norm(vertices[0] - vertices[1])
        assert all([allclose(vertices[0] - vertices[2], l * array([1, 0, -1, 0]) / sqrt(2)),
                    allclose(vertices[0] - vertices[3], l * array([1, 0, 0, -1]) / sqrt(2)),
                    allclose(vertices[1] - vertices[2], l * array([0, 1, -1, 0]) / sqrt(2)),
                    allclose(vertices[1] - vertices[3], l * array([0, 1, 0, -1]) / sqrt(2)),
                    allclose(vertices[2] - vertices[3], l * array([0, 0, 1, -1]) / sqrt(2))])

    def test_coordinates(self):
        """Centre of gravity of vertices is the same as centre of gravity of input.
        Barycentric coorinates of all input points relative to vertices returned
        by tight_simplex are positive, i.e. points lie within simplex."""
        x = self.x
        vertices = self.vertices
        assert_allclose(mean(x, axis=0), mean(vertices, axis=0),
                        err_msg='Centre of gravity of vertices and input differ.')
        coords = x @ inv(vertices)
        assert_allclose(sum(coords, axis=1), ones(5), err_msg='Barycentric coords do not total one.')
        if not all(coords > 0.):
            msg = (f'Not all barycentric coordinates are positive: {coords}'
                   f'\n original were {x}')
            raise AssertionError(msg)


if __name__ == '__main__':
    main()
