#!/usr/bin/env python3
"""
Tension Field Solver for IT³ Framework
Numerical solution of the modified Poisson equation
"""

import numpy as np
from typing import Tuple, Callable
import matplotlib.pyplot as plt
from scipy import ndimage

class TensionFieldSolver:
    """
    Solves the modified Poisson equation:
    ∇²Φ_eff = 4πG(ρ_baryon + ρ_T)
    
    where ρ_T = (1/2)μ|∇T|² + V(T)
    """
    
    def __init__(self, grid_size: int = 128, box_size: float = 10.0):
        """
        Initialize solver
        
        Args:
            grid_size: Number of grid points in each dimension
            box_size: Physical size of the computational domain
        """
        self.grid_size = grid_size
        self.box_size = box_size
        self.dx = box_size / grid_size
        
        # Physical constants (in appropriate units)
        self.G = 1.0  # Gravitational constant
        self.mu = 1.0  # Lattice stiffness parameter
        self.lambda_param = 1.0  # Self-interaction strength
        self.v = 1.0  # Vacuum expectation value
        
    def tension_potential(self, T: np.ndarray) -> np.ndarray:
        """
        Compute the tension field potential V(T)
        
        V(T) = (λ/4)(T² - v²)²
        
        Args:
            T: Tension field configuration
            
        Returns:
            Potential energy density
        """
        return (self.lambda_param / 4.0) * (T**2 - self.v**2)**2
    
    def tension_energy_density(self, T: np.ndarray) -> np.ndarray:
        """
        Compute the tension field energy density ρ_T
        
        ρ_T = (1/2)μ|∇T|² + V(T)
        
        Args:
            T: Tension field configuration
            
        Returns:
            Energy density
        """
        # Compute gradient
        grad_T = np.gradient(T, self.dx)
        grad_mag_sq = sum(g**2 for g in grad_T)
        
        # Kinetic term
        kinetic = 0.5 * self.mu * grad_mag_sq
        
        # Potential term
        potential = self.tension_potential(T)
        
        return kinetic + potential
    
    def laplacian(self, phi: np.ndarray) -> np.ndarray:
        """
        Compute Laplacian using finite differences
        
        Args:
            phi: Scalar field
            
        Returns:
            ∇²phi
        """
        return ndimage.laplace(phi) / self.dx**2
    
    def solve_poisson_iterative(self, rho: np.ndarray, 
                                 max_iter: int = 10000,
                                 tol: float = 1e-6) -> np.ndarray:
        """
        Solve Poisson equation ∇²Φ = 4πGρ using Jacobi iteration
        
        Args:
            rho: Source density
            max_iter: Maximum number of iterations
            tol: Convergence tolerance
            
        Returns:
            Gravitational potential Φ
        """
        # Initialize potential
        phi = np.zeros_like(rho)
        
        # Source term
        source = 4 * np.pi * self.G * rho
        
        # Jacobi iteration
        for iteration in range(max_iter):
            phi_old = phi.copy()
            
            # Update using 7-point stencil (3D)
            for i in range(1, self.grid_size-1):
                for j in range(1, self.grid_size-1):
                    for k in range(1, self.grid_size-1):
                        phi[i,j,k] = (
                            phi_old[i+1,j,k] + phi_old[i-1,j,k] +
                            phi_old[i,j+1,k] + phi_old[i,j-1,k] +
                            phi_old[i,j,k+1] + phi_old[i,j,k-1] -
                            self.dx**2 * source[i,j,k]
                        ) / 6.0
            
            # Check convergence
            diff = np.max(np.abs(phi - phi_old))
            if diff < tol:
                print(f"Converged after {iteration} iterations (tol={diff:.2e})")
                break
            
            if iteration % 1000 == 0:
                print(f"Iteration {iteration}: max diff = {diff:.2e}")
        
        return phi
    
    def solve_modified_poisson(self, rho_baryon: np.ndarray,
                                T_field: np.ndarray,
                                max_iter: int = 10000) -> dict:
        """
        Solve the modified Poisson equation with tension field
        
        ∇²Φ_eff = 4πG(ρ_baryon + ρ_T)
        
        Args:
            rho_baryon: Baryonic matter density
            T_field: Tension field configuration
            max_iter: Maximum iterations for Poisson solver
            
        Returns:
            Dictionary with solution and diagnostics
        """
        # Compute tension field energy density
        rho_T = self.tension_energy_density(T_field)
        
        # Total effective density
        rho_total = rho_baryon + rho_T
        
        # Solve Poisson equation
        print("Solving modified Poisson equation...")
        phi_eff = self.solve_poisson_iterative(rho_total, max_iter=max_iter)
        
        # Compute effective gravitational acceleration
        grad_phi = np.gradient(phi_eff, self.dx)
        g_magnitude = np.sqrt(sum(g**2 for g in grad_phi))
        
        return {
            'phi_eff': phi_eff,
            'rho_baryon': rho_baryon,
            'rho_T': rho_T,
            'rho_total': rho_total,
            'g_magnitude': g_magnitude,
            'tension_field': T_field
        }
    
    def create_galaxy_model(self, 
                           center: Tuple[int, int, int] = None,
                           mass: float = 1.0,
                           scale_radius: float = 5.0) -> np.ndarray:
        """
        Create a simple galaxy density model
        
        Args:
            center: Center of the galaxy in grid coordinates
            mass: Total mass
            scale_radius: Scale radius of the density profile
            
        Returns:
            Density distribution
        """
        if center is None:
            center = (self.grid_size // 2,) * 3
        
        # Create coordinate grids
        x = np.arange(self.grid_size) - center[0]
        y = np.arange(self.grid_size) - center[1]
        z = np.arange(self.grid_size) - center[2]
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        
        # Compute radius
        R = np.sqrt(X**2 + Y**2 + Z**2) * self.dx
        
        # Plummer-like density profile
        rho = (3 * mass / (4 * np.pi * scale_radius**3)) * \
              (1 + (R/scale_radius)**2)**(-2.5)
        
        return rho
    
    def create_tension_field_vacuum(self) -> np.ndarray:
        """
        Create tension field in vacuum configuration (T = v)
        
        Returns:
            Uniform tension field
        """
        return np.ones((self.grid_size, self.grid_size, self.grid_size)) * self.v


def main():
    """Main function to demonstrate tension field solver"""
    print("=" * 70)
    print("IT³ Framework - Tension Field Solver")
    print("Modified Poisson Equation: ∇²Φ_eff = 4πG(ρ_baryon + ρ_T)")
    print("=" * 70)
    
    # Initialize solver
    solver = TensionFieldSolver(grid_size=64, box_size=10.0)
    
    # Create galaxy model
    print("\n1. Creating galaxy model...")
    rho_baryon = solver.create_galaxy_model(
        center=(32, 32, 32),
        mass=100.0,
        scale_radius=3.0
    )
    print(f"   Total baryonic mass: {np.sum(rho_baryon):.2f}")
    
    # Create tension field (vacuum configuration)
    print("\n2. Creating tension field (vacuum configuration T=v)...")
    T_field = solver.create_tension_field_vacuum()
    print(f"   Vacuum expectation value: v = {solver.v}")
    
    # Compute tension energy density
    rho_T = solver.tension_energy_density(T_field)
    print(f"   Tension energy density: ρ_T = {np.mean(rho_T):.6f}")
    
    # Solve modified Poisson equation
    print("\n3. Solving modified Poisson equation...")
    solution = solver.solve_modified_poisson(rho_baryon, T_field, max_iter=5000)
    
    # Print diagnostics
    print("\n4. Solution Diagnostics:")
    print("-" * 70)
    print(f"   Max potential: Φ_max = {np.max(solution['phi_eff']):.6f}")
    print(f"   Min potential: Φ_min = {np.min(solution['phi_eff']):.6f}")
    print(f"   Max g-field: g_max = {np.max(solution['g_magnitude']):.6f}")
    
    # Save results
    print("\n5. Saving results...")
    np.savez('tension_field_solution.npz', **solution)
    print("   Results saved to 'tension_field_solution.npz'")
    
    print("=" * 70)


if __name__ == "__main__":
    main()