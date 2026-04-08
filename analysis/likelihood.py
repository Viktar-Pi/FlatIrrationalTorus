"""
likelihood.py
Planck PR4 temperature power spectrum likelihood approximation.
Uses Gaussian approximation: -2 ln L = Σ [(Dℓ^th - Dℓ^obs)² / σℓ²]
"""

import numpy as np

class PlanckPRLikelihood:
    """
    Approximate likelihood for Planck PR4 TT spectrum (ℓ = 2 to 2000).
    """
    
    def __init__(self, data_file, sigma_fraction=0.15):
        """
        Initialize likelihood with observed data.
        
        Parameters:
        -----------
        data_file : str
            Path to Planck PR4 TT data file (ell, D_ell_obs)
        sigma_fraction : float, optional
            Fractional uncertainty σℓ ≈ 0.15 * Dℓ^obs (default)
        """
        # Load observed data
        data = np.loadtxt(data_file)
        self.ell = data[:, 0].astype(int)
        self.D_obs = data[:, 1]  # Dℓ = ℓ(ℓ+1)Cℓ/(2π)
        self.sigma = sigma_fraction * self.D_obs  # Approximate uncertainty
        
        # Mask for valid multipoles
        self.mask = (self.ell >= 2) & (self.ell <= 2000)
        
    def compute_D_theory(self, Cl_tt, ell_array):
        """
        Convert Cℓ to Dℓ = ℓ(ℓ+1)Cℓ/(2π).
        """
        return ell_array * (ell_array + 1) * Cl_tt / (2 * np.pi)
    
    def log_likelihood(self, D_theory_array):
        """
        Compute log-likelihood for theoretical Dℓ array.
        
        Parameters:
        -----------
        D_theory_array : array-like
            Theoretical Dℓ values matching self.ell
            
        Returns:
        --------
        logL : float
            Log-likelihood value
        """
        # Restrict to valid multipoles
        ell_valid = self.ell[self.mask]
        D_obs_valid = self.D_obs[self.mask]
        sigma_valid = self.sigma[self.mask]
        D_th_valid = np.array(D_theory_array)[self.mask]
        
        # Gaussian log-likelihood
        chi2 = np.sum(((D_th_valid - D_obs_valid) / sigma_valid)**2)
        logL = -0.5 * chi2
        
        return logL
    
    def chi_squared(self, D_theory_array):
        """
        Return χ² value (for model comparison).
        """
        ell_valid = self.ell[self.mask]
        D_obs_valid = self.D_obs[self.mask]
        sigma_valid = self.sigma[self.mask]
        D_th_valid = np.array(D_theory_array)[self.mask]
        
        return np.sum(((D_th_valid - D_obs_valid) / sigma_valid)**2)
