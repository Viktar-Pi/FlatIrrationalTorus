#!/usr/bin/env python3
"""
convert_chains.py — Convert MCMC chains from .pkl to .npy format
===============================================================
This script converts pickled MCMC chains to NumPy format for easier distribution
and verification. Used for the Flat Irrational Torus topology model.

Usage:
    python convert_chains.py

Input files:
    - samples_it3.pkl (IT3 model chains)
    - samples_lcdm.pkl (ΛCDM model chains)

Output files:
    - data/chains_IT3.npy
    - data/chains_LCDM.npy

Author: Victor Logvinovich
License: MIT
DOI: 10.5281/zenodo.19440498
"""

import pickle
import numpy as np
from pathlib import Path
import sys

DOI = "10.5281/zenodo.19440498"

def main():
    print("=" * 70)
    print("IT3 TOPOLOGY MODEL — CHAIN CONVERSION SCRIPT")
    print(f"DOI: {DOI}")
    print("=" * 70)
    
    Path("data").mkdir(exist_ok=True)
    files = {'samples_it3.pkl': 'data/chains_IT3.npy', 'samples_lcdm.pkl': 'data/chains_LCDM.npy'}
    success_count = 0
    
    for pkl_file, npy_file in files.items():
        pkl_path = Path(pkl_file)
        npy_path = Path(npy_file)
        
        if not pkl_path.exists():
            print(f"❌ File not found: {pkl_path}")
            continue
        
        try:
            print(f"\n📥 Loading {pkl_file}...")
            with open(pkl_path, "rb") as f:
                chains = pickle.load(f)
            if not isinstance(chains, np.ndarray):
                print(f"⚠️  Warning: {pkl_file} is not a NumPy array, converting...")
                chains = np.array(chains)
            np.save(npy_path, chains)
            print(f"✓ Saved {npy_file}")
            print(f"  Shape: {chains.shape[0]} samples × {chains.shape[1]} parameters")
            print(f"  Size: {npy_path.stat().st_size / 1024 / 1024:.2f} MB")
            success_count += 1
        except Exception as e:
            print(f"❌ Error converting {pkl_file}: {e}")
    
    print("\n" + "=" * 70)
    print(f"CONVERSION COMPLETE: {success_count}/{len(files)} files converted")
    print("=" * 70)
    
    if success_count == len(files):
        print("\n✅ All chains successfully converted!")
        print("\n🔍 Next step: Run verification script")
        print("   python verify_results.py")
        return 0
    else:
        print("\n⚠️  Some files were not converted. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())