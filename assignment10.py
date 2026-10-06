import yaml
import numpy as np
import scipy.sparse
import scipy.sparse.linalg
import matplotlib.pyplot as plt

class OneDimReservoir():

    def __init__(self, inputs):
        '''
            Class for solving one-dimensional reservoir problems with
            finite differences.
        '''

        #stores input dictionary as class attribute, either read from a yaml file
        #or directly from a Python dictonary
        if isinstance(inputs, str):
            with open(inputs) as f:
                self.inputs = yaml.safe_load(f)
        else:
            self.inputs = inputs

        #computes delta_x
        self.Nx = self.inputs['numerical']['number of grids']['x']
        self.delta_x = self.inputs['reservoir']['length'] / float(self.Nx)

        #gets delta_t from inputs
        self.delta_t = self.inputs['numerical']['time step']

        #computes eta
        self.compute_eta()

        #calls fill matrix method (must be completely implemented to work)
        self.fill_matrices()

        #applies the initial reservoir pressues to self.p
        self.apply_initial_conditions()

        #create an empty list for storing data if plots are requested
        if 'plots' in self.inputs:
            self.p_plot = []

        return


    def compute_alpha(self):
        '''
            Computes the constant alpha.
        '''

        c_t = self.inputs['fluid']['water']['compressibility']
        mu = self.inputs['fluid']['water']['viscosity']
        phi = self.inputs['reservoir']['porosity']
        k = self.inputs['reservoir']['permeability']

        return k / mu / phi / c_t

    def compute_eta(self):
        '''
            Computes the constant eta
        '''

        alpha = self.compute_alpha()
        factor = self.inputs['conversion factor']
        dx = self.delta_x
        dt = self.delta_t

        self.eta = alpha * dt / dx ** 2 * factor

    def fill_matrices(self):
        """Implement the matrix assembly described in README.md."""
        raise NotImplementedError("Complete fill_matrices")

    def apply_boundary_conditions(self, A, Q):
        '''
            Applies boundary conditions (called by fill_matrices).
        '''

        N = self.Nx

        bc = self.inputs['boundary conditions']
        for side in ('left', 'right'):
            boundary = bc[side]
            if boundary['type'] not in ('prescribed pressure', 'prescribed flux'):
                raise ValueError('unsupported boundary type')
            if boundary['type'] == 'prescribed flux' and boundary['value'] != 0:
                raise ValueError('only zero prescribed flux is supported')

        if bc['left']['type'] == 'prescribed pressure':

            A[0, 0] = 3
            Q[0] = 2 * bc['left']['value']  * self.eta

        elif bc['left']['type'] == 'prescribed flux':

            mu = self.inputs['fluid']['water']['viscosity']
            k = self.inputs['reservoir']['permeability']
            dx = self.delta_x

            A[0, 0] = 1
            Q[0] = bc['left']['value'] * mu / dx / k * self.eta

        if bc['right']['type'] == 'prescribed pressure':

            A[N-1, N-1] = 3
            Q[N-1] = 2 * bc['right']['value'] * self.eta

        elif bc['right']['type'] == 'prescribed flux':

            mu = self.inputs['fluid']['water']['viscosity']
            k = self.inputs['reservoir']['permeability']
            dx = self.delta_x

            A[N-1, N-1] = 1
            Q[N-1] = bc['right']['value'] * mu / dx / k * self.eta

        return


    def apply_initial_conditions(self):
        '''
            Applies initial pressures to self.p
        '''

        N = self.Nx

        self.p = np.ones(N) * self.inputs['initial conditions']['pressure']

        return


    def solve_one_step(self):
        """Implement the time step described in README.md."""
        raise NotImplementedError("Complete solve_one_step")


    def solve(self):
        '''
            Solves until "number of time steps"
        '''

        for i in range(self.inputs['numerical']['number of time steps']):
            self.solve_one_step()

            if 'plots' in self.inputs and i % self.inputs['plots']['frequency'] == 0:
                self.p_plot.append(self.get_solution().copy())

        return

    def plot(self):
        '''
           Crude plotting function.  Plots pressure as a function of grid block #
        '''

        if hasattr(self, 'p_plot'):
            for i in range(len(self.p_plot)):
                plt.plot(self.p_plot[i])

        return

    def get_solution(self):
        '''
            Returns solution vector
        '''
        return self.p.copy()
