#!/usr/bin/env python

# Copyright 2018-2020 John T. Foster
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
import numpy as np
from assignment10 import OneDimReservoir


class TestSolution(unittest.TestCase):

    def setUp(self):

        self.inputs = {
            'conversion factor': 6.33e-3,
            'fluid': {
                'water': {
                    'compressibility': 1e-6, #psi^{-1}
                    'viscosity': 1, #cp
                },
            },
            'reservoir': {
                'permeability': 50, #mD
                'porosity': 0.2,
                'length': 10000, #ft
            },
            'initial conditions': {
                'pressure': 1000 #psi
            },
            'boundary conditions': {
                'left': {
                    'type': 'prescribed pressure',
                    'value': 2000 #psi
                },
                'right': {
                    'type': 'prescribed flux',
                    'value': 0 #ft^3/day
                }
            },
            'numerical': {
                'solver': 'implicit',
                'number of grids': {
                 'x': 4},
                'time step': 1, #day
                'number of time steps' : 3
            },
            'plots': {
                'frequency': 1
            }
        }

        return

    def test_eta(self):

        problem = OneDimReservoir(self.inputs)

        np.testing.assert_allclose(problem.eta, 0.2532, atol=1e-3)

        return

    def test_implicit_solve_one_step(self):

        implicit = OneDimReservoir(self.inputs)
        implicit.solve_one_step()
        np.testing.assert_allclose(implicit.get_solution(),
                                   np.array([1295.1463, 1051.1036, 1008.8921, 1001.7998]),
                                   atol=0.5)
        return

    def test_explicit_solve_one_step(self):

        self.inputs['numerical']['solver'] = 'explicit'

        explicit = OneDimReservoir(self.inputs)

        explicit.solve_one_step()

        np.testing.assert_allclose(explicit.get_solution(),
                               np.array([ 1506., 1000.,  1000.,  1000.0]),
                               atol=0.5)
        return

    def test_implicit_solve(self):

        implicit = OneDimReservoir(self.inputs)
        implicit.solve()
        np.testing.assert_allclose(implicit.get_solution(),
                                   np.array([1582.9, 1184.8, 1051.5, 1015.9]),
                                   atol=0.5)
        return

    def test_explicit_solve(self):

        self.inputs['numerical']['solver'] = 'explicit'

        explicit = OneDimReservoir(self.inputs)

        explicit.solve()

        np.testing.assert_allclose(explicit.get_solution(),
                               np.array([1689.8, 1222.3, 1032.4, 1000.0]),
                               atol=0.5)
        return

class TestMatrixContract(unittest.TestCase):
    setUp = TestSolution.setUp
    def test_matrix_and_boundary_vector(self):
        from scipy.sparse import issparse
        model = OneDimReservoir(self.inputs)
        self.assertTrue(issparse(model.A))
        self.assertTrue(issparse(model.I))
        np.testing.assert_allclose(model.A.toarray(), [[3,-1,0,0],[-1,2,-1,0],[0,-1,2,-1],[0,0,-1,1]])
        np.testing.assert_allclose(model.pB, [2*model.eta*2000,0,0,0])

    def test_closed_uniform_pressure(self):
        self.inputs['boundary conditions']['left'] = {'type':'prescribed flux','value':0}
        for solver in ('explicit', 'implicit'):
            self.inputs['numerical']['solver'] = solver
            model = OneDimReservoir(self.inputs)
            model.solve()
            np.testing.assert_allclose(model.get_solution(), 1000, atol=1e-8)

    def test_right_pressure_uses_right_value(self):
        self.inputs['boundary conditions']['right'] = {'type':'prescribed pressure','value':1500}
        model = OneDimReservoir(self.inputs)
        np.testing.assert_allclose(model.pB, [2*model.eta*2000,0,0,2*model.eta*1500])


if __name__ == '__main__':
        unittest.main()
