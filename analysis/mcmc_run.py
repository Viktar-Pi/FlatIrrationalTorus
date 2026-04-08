 #!/usr/bin/env python3
"""
mcmc_run.py
Bayesian MCMC inference for IT3 topology model using emcee + CLASS.
Reproduces results from Logvinovich (2026), main.pdf
"""

import numpy as np
import emcee
import corner
import matplotlib.pyplot as plt
import os
import sys
from class_wrapper import IT3Class
from likelihood import PlanckPRLikelihood

# Paths
DATA_DIR = "../data/planck_pr4_likelihood"
FIGURES_DIR = "../figures"
RESULTS_DIR = "../results"
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Priors (uniform)
PRIORS = {
    'logA': (1.61, 3.91),      # ln(1e10 As)
    'ns': (0.8, 1.2),          # Spectral index
    'H0': (50, 90),            # km/s/Mpc
    'ombh2': (0.005, 0.1),     # Baryon density
    'omch2': (0.001, 0.99),    # CDM density
    'tau': (0.01, 0.15),       # Reionization optical depth
    'Lx': (28.0, 35.0),        # Topology scale [Gpc]
}

def log_prior(theta):
    """Log-prior: uniform within bounds, -inf outside."""
    names = ['logA', 'ns', 'H0', 'ombh2', 'omch2', 'tau', 'Lx']
    for val, (low, high) in zip(theta, [PRIORS[n] for n in names]):
        if not (low <= val <= high):
            return -np.inf
    return 0.0

def log_likelihood(theta, class_wrapper, likelihood):
    """Log-likelihood: compute theoretical Dℓ and compare to data."""
    logA, ns, H0, ombh2, omch2, tau, Lx = theta
    
    # Update CLASS wrapper with new parameters
    class_wrapper.Lx = Lx
    class_wrapper.set_cosmology(
        A_s=np.exp(logA - 1e10),  # CLASS expects As, not ln(1e10 As)
        n_s=ns,
        H0=H0,
        omega_b=ombh2,
        omega_cdm=omch2,
        tau_reio=tau
    )
    
    # Get suppressed Cl and convert to Dℓ
    ell_array = likelihood.ell[likelihood.mask]
    Cl_tt = class_wrapper.get_Cl_with_topology(ell_array)['tt']
    D_theory = likelihood.compute_D_theory(Cl_tt, ell_array)
    
    return likelihood.log_likelihood(D_theory)

def log_posterior(theta, class_wrapper, likelihood):
    """Log-posterior = log-prior + log-likelihood."""
    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta, class_wrapper, likelihood)

def run_mcmc(n_walkers=32, n_steps=5000, burn_in=1000):
    """
    Run MCMC analysis for IT3 model.
    """
    print(f"[MCMC] Initializing with {n_walkers} walkers, {n_steps} steps...")
    
    # Load data and initialize components
    likelihood = PlanckPRLikelihood(f"{DATA_DIR}/planck_pr4_tt.dat")
    class_wrapper = IT3Class(Lx_Gpc=28.57)  # Initial guess
    
    # Initial positions for walkers (small Gaussian scatter around prior centers)
    ndim = 7
    pos = []
    for _ in range(n_walkers):
        p = [np.random.uniform(low, high) for (low, high) in PRIORS.values()]
        pos.append(p)
    pos = np.array(pos)
    
    # Setup sampler
    sampler = emcee.EnsembleSampler(n_walkers, ndim, log_posterior, 
                                    args=(class_wrapper, likelihood))
    
    # Run MCMC
    print("[MCMC] Running...")
    sampler.run_mcmc(pos, n_steps, progress=True)
    
    # Discard burn-in
    flat_samples = sampler.get_chain(discard=burn_in, flat=True)
    
    # Save chains
    np.save(f"{RESULTS_DIR}/mcmc_chains.npy", flat_samples)
    print(f"[MCMC] Chains saved to {RESULTS_DIR}/mcmc_chains.npy")
    
    return flat_samples, sampler

def generate_corner_plot(samples):
    """Generate corner plot of posterior distributions."""
    labels = [r'$\ln(10^{10}A_s)$', r'$n_s$', r'$H_0$', 
              r'$\Omega_b h^2$', r'$\Omega_c h^2$', r'$\tau$', r'$L_x$ [Gpc]']
    
    fig = corner.corner(samples, labels=labels, 
                        quantiles=[0.16, 0.5, 0.84],
                        show_titles=True, title_fmt=".2f",
                        color='C0', plot_datapoints=False)
    fig.savefig(f"{FIGURES_DIR}/corner_plot.png", dpi=300, bbox_inches='tight')
    print(f"[Plot] Corner plot saved to {FIGURES_DIR}/corner_plot.png")
    plt.close(fig)

def main():
    """Main execution."""
    print("="*60)
    print("IT3 Topology Model — MCMC Analysis")
    print("="*60)
    
    # Run MCMC
    samples, sampler = run_mcmc()
    
    # Generate corner plot
    generate_corner_plot(samples)
    
    # Print marginalized constraints
    param_names = ['logA', 'ns', 'H0', 'ombh2', 'omch2', 'tau', 'Lx']
    print("\n" + "="*60)
    print("MARGINALIZED POSTERIOR CONSTRAINTS (16th/50th/84th percentiles):")
    print("="*60)
    for i, name in enumerate(param_names):
        vals = np.percentile(samples[:, i], [16, 50, 84])
        if name == 'H0':
            print(f"{name:6s} = {vals[1]:.2f} +{vals[2]-vals[1]:.2f}/-{vals[1]-vals[0]:.2f} km/s/Mpc")
        elif name == 'Lx':
            print(f"{name:6s} = {vals[1]:.2f} +{vals[2]-vals[1]:.2f}/-{vals[1]-vals[0]:.2f} Gpc")
        else:
            print(f"{name:6s} = {vals[1]:.3f} +{vals[2]-vals[1]:.3f}/-{vals[1]-vals[0]:.3f}")
    
    print("\n✅ Analysis complete!")
    return samples

if __name__ == "__main__":
    samples = main()
