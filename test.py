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
import nbconvert
import numpy as np

with open("assignment10.ipynb") as f:
    exporter = nbconvert.PythonExporter()
    python_file, _ = exporter.from_file(f)


with open("assignment10.py", "w") as f:
    f.write(python_file)


from assignment10 import *


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
                               np.array([ 1506., 1000.,  1000.,  1000.004]), 
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

if __name__ == '__main__':
        unittest.main()
