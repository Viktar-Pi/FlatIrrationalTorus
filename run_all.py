#!/usr/bin/env python3
"""
Main execution script for IT3 topology analysis.
Reproduces all results and figures from the manuscript.
"""

import os
import subprocess

def main():
    print("="*60)
    print("Flat Irrational Torus (IT3) Analysis Pipeline")
    print("="*60)
    
    # Run MCMC analysis
    print("\n[1/4] Running MCMC analysis...")
    subprocess.run(["python", "analysis/mcmc_run.py"], check=True)
    
    # Generate figures
    print("\n[2/4] Generating figures...")
    subprocess.run(["python", "analysis/generate_figures.py"], check=True)
    
    # Validate against DESI
    print("\n[3/4] Validating against DESI 2024 + Pantheon+...")
    subprocess.run(["python", "analysis/desi_validation.py"], check=True)
    
    # Create summary
    print("\n[4/4] Creating results summary...")
    subprocess.run(["python", "verify_results.py"], check=True)
    
    print("\n" + "="*60)
    print("✅ All analysis complete!")
    print("Results saved in figures/ and results/")
    print("="*60)

if __name__ == "__main__":
    main()
