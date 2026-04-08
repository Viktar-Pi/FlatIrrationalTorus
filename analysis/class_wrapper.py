"""
class_wrapper.py
Wrapper for CLASS Boltzmann code with Flat Irrational Torus (IT3) topology suppression.
Implements F(ℓ) = 1 / (1 + exp[-(ℓ - ℓ_cut)/Δℓ])
"""

import numpy as np
from classy import Class

class IT3Class(Class):
    """
    CLASS wrapper with topological transfer function F(ℓ) for IT3 model.
    """
    
    def __init__(self, Lx_Gpc, delta_ell=3.0, chi_rec_Gpc=14.1):
        """
        Initialize IT3 topology model.
        
        Parameters:
        -----------
        Lx_Gpc : float
            Topology scale Lx in Gpc
        delta_ell : float, optional
            Smoothing width for topological cutoff (default: 3.0)
        chi_rec_Gpc : float, optional
            Comoving distance to last scattering in Gpc (default: 14.1)
        """
        super().__init__()
        self.Lx = Lx_Gpc
        self.delta_ell = delta_ell
        self.chi_rec = chi_rec_Gpc
        
        # Compute ℓ_cut from k_min = 2π/(√3 * Lx)
        self.l_cut = (2 * np.pi / (np.sqrt(3) * self.Lx)) * self.chi_rec
        
    def set_cosmology(self, **kwargs):
        """
        Set cosmological parameters and inject topological modification.
        """
        # Standard ΛCDM parameters
        params = {
            'output': 'tCl',
            'l_max_scalars': 2500,
            'P_k_max_h/Mpc': 1.0,
            **kwargs
        }
        self.set(params)
        self.compute()
        
    def get_Cl_with_topology(self, ell_array):
        """
        Return Cℓ with topological suppression F(ℓ) applied.
        
        Parameters:
        -----------
        ell_array : array-like
            Multipole values
            
        Returns:
        --------
        Cl_suppressed : dict
            Dictionary with suppressed Cl{'tt': ..., 'ee': ..., ...}
        """
        # Get standard CLASS Cl
        Cl_raw = self.raw_cl(ell_array)
        
        # Apply topological transfer function F(ℓ)
        F_ell = 1.0 / (1.0 + np.exp(-(ell_array - self.l_cut) / self.delta_ell))
        
        # Suppress only scalar temperature spectrum (tt)
        Cl_suppressed = Cl_raw.copy()
        if 'tt' in Cl_suppressed:
            Cl_suppressed['tt'] = Cl_raw['tt'] * F_ell**2  # Power spectrum scales as F²
            
        return Cl_suppressed
    
    def close(self):
        """Clean up CLASS instance."""
        super().cleanup()
