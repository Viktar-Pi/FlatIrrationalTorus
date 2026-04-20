#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
🎯 IT³ MODULE 38: EXPANDED SNIPER SURVEY (NODE 5 - CETUS/PISCES)
================================================================================
ЦЕЛЬ: Глубокий поиск Узла №5 с учетом орбитальных отклонений (±6 градусов).
Ослаблены фильтры звездности, чтобы пробить пыль и артефакты склейки.
================================================================================
"""

import os
import sys
import time
import math
import logging
import numpy as np
import pandas as pd
import requests
from io import StringIO
from sklearn.cluster import DBSCAN
from concurrent.futures import ProcessPoolExecutor, as_completed
import warnings

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("IT3_Node5_Expanded")

# РАСШИРЕННАЯ ЗОНА ДЛЯ УЗЛА 5 (Учитываем Кеплеровские отклонения по орбите)
TARGET_NODES = {
    'Node_5_Cetus_EXPANDED':  {'ra_min': 23.0,  'ra_max': 41.0,  'dec_min': -5.0, 'dec_max': 13.0}
}

GLOBAL_CONFIG = {
    "TILE_SIZE": 1.5,
    "PM_MIN": 70.0, "PM_MAX": 340.0,
    "SPEED_STEP": 10.0,
    "EPS_DEG": 2.5 / 3600.0,          
    "ZMag_MIN": 17.0, "ZMag_MAX": 23.8,  # Пробиваем глубже
    "MIN_SPAN_DAYS": 1.0,
    "MAX_PARALLAX_SPAN_DAYS": 180.0,     # Расширили окно времени
    "EBV_MAX": 2.0,                   
    "TIMEOUT": 60
}

class ADQLClient:
    @staticmethod
    def fetch_tile(ra1, ra2, dec1, dec2):
        # class_star снижен до 0.6, чтобы ловить объекты, искаженные атмосферой
        query = f"""
            SELECT id, ra, dec, mjd, zmag AS mag
            FROM nsc_dr2.object
            WHERE ra BETWEEN {ra1} AND {ra2}
              AND dec BETWEEN {dec1} AND {dec2}
              AND ndet BETWEEN 2 AND 15
              AND deltamjd < 2.0
              AND zmag BETWEEN {GLOBAL_CONFIG['ZMag_MIN']} AND {GLOBAL_CONFIG['ZMag_MAX']}
              AND class_star > 0.60
              AND flags = 0
              AND ebv < {GLOBAL_CONFIG['EBV_MAX']}
        """
        payload = {"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "query": query.strip()}
        
        try:
            resp = requests.post("https://datalab.noirlab.edu/tap/sync", data=payload, timeout=GLOBAL_CONFIG["TIMEOUT"])
            if "<?xml" in resp.text[:50] or "Error" in resp.text[:50] or len(resp.text) < 10:
                return None
            df = pd.read_csv(StringIO(resp.text))
            if 'ra' not in df.columns: return None
            for col in ['ra', 'dec', 'mjd', 'mag']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            return df.dropna(subset=['ra', 'dec', 'mjd', 'mag'])
        except:
            return None

class KinematicEngine:
    @staticmethod
    def is_real_orbit(track_df):
        track = track_df.sort_values('mjd')
        if len(np.unique(np.floor(track['mjd']))) < 3: return False
        for i in range(len(track) - 1):
            for j in range(i + 1, len(track)):
                dt = track['mjd'].iloc[j] - track['mjd'].iloc[i]
                if 0.1 < dt < 150.0:
                    dx = (track['ra'].iloc[j] - track['ra'].iloc[i]) * 3600.0 * math.cos(math.radians(track['dec'].mean()))
                    dy = (track['dec'].iloc[j] - track['dec'].iloc[i]) * 3600.0
                    if math.sqrt(dx**2 + dy**2) < 0.5: return False
        return True

    @staticmethod
    def scan_tile(df):
        if df is None or len(df) < 5: return []
        candidates = []
        t0_mjd = df['mjd'].mean()
        speeds = np.arange(GLOBAL_CONFIG["PM_MIN"], GLOBAL_CONFIG["PM_MAX"] + GLOBAL_CONFIG["SPEED_STEP"], GLOBAL_CONFIG["SPEED_STEP"])
        target_angles = np.arange(0, 360, 10)
        
        ra_vals, dec_vals, mjd_vals = df['ra'].values, df['dec'].values, df['mjd'].values
        dt_yr = (mjd_vals - t0_mjd) / 365.25
        cos_dec = np.maximum(np.cos(np.radians(dec_vals)), 1e-6)
        
        for speed in speeds:
            for angle in target_angles:
                rad = np.radians(angle)
                ra0 = ra_vals - (speed * np.cos(rad) * dt_yr) / 3600.0 / cos_dec
                dec0 = dec_vals - (speed * np.sin(rad) * dt_yr) / 3600.0
                db = DBSCAN(eps=GLOBAL_CONFIG["EPS_DEG"], min_samples=3).fit(np.column_stack((ra0, dec0)))
                
                for cl in set(db.labels_) - {-1}:
                    idx = np.where(db.labels_ == cl)[0]
                    track_df = df.iloc[idx].copy()
                    time_span = track_df['mjd'].max() - track_df['mjd'].min()
                    
                    if GLOBAL_CONFIG["MIN_SPAN_DAYS"] < time_span < GLOBAL_CONFIG["MAX_PARALLAX_SPAN_DAYS"] and KinematicEngine.is_real_orbit(track_df):
                        mjd_start = track_df['mjd'].min()
                        if not any(abs(c['mjd_start'] - mjd_start) < 0.1 for c in candidates):
                            track_df.loc[:, 'track_id'] = f"{speed:.1f}_{angle}_{mjd_start:.1f}"
                            candidates.append({"mjd_start": mjd_start, "data_chunk": track_df})
        return candidates

class NodeSniper:
    def __init__(self, node_name, bounds):
        self.node_name = node_name
        self.bounds = bounds
        self.csv_path = f"IT3_SNIPER_EXPANDED_{node_name}.csv"
        self.tiles = self._generate_grid()

    def _generate_grid(self):
        tiles, ra = [], self.bounds['ra_min']
        ts = GLOBAL_CONFIG["TILE_SIZE"]
        while ra < self.bounds['ra_max']:
            dec = self.bounds['dec_min']
            while dec < self.bounds['dec_max']:
                tiles.append((ra, ra + ts, dec, dec + ts))
                dec += ts
            ra += ts
        return tiles

    def _worker(self, tile):
        try:
            df = ADQLClient.fetch_tile(*tile)
            cands = KinematicEngine.scan_tile(df)
            if cands:
                logger.info(f"🔥 БИНГО! В зоне {self.node_name} тайл {tile} найдено орбит: {len(cands)}!")
            return cands
        except:
            return None

    def hunt(self):
        logger.info(f"▶️ ПРИЦЕЛИВАНИЕ В {self.node_name} | RA: {self.bounds['ra_min']}–{self.bounds['ra_max']} | Тайлов: {len(self.tiles)}")
        all_candidates = []
        max_workers = max(1, int(os.cpu_count() * 0.75))
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self._worker, t): t for t in self.tiles}
            for i, fut in enumerate(as_completed(futures), 1):
                res = fut.result()
                if res: all_candidates.extend(res)
                if i % 10 == 0:
                    logger.info(f"   ⏳ Сканирование {self.node_name}: {i}/{len(self.tiles)} тайлов")

        if all_candidates:
            final_df = pd.concat([c['data_chunk'] for c in all_candidates], ignore_index=True)
            final_df.to_csv(self.csv_path, index=False)
            logger.info(f"🏆 УСПЕХ! В УЗЛЕ НАЙДЕНЫ КАНДИДАТЫ! Сохранено в {self.csv_path}")
        else:
            logger.info(f"📭 Ничего не найдено даже в расширенной зоне.")
        logger.info("-" * 60)

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.set_start_method("spawn", force=True)
    
    logger.info("="*80)
    logger.info("🎯 IT³ TARGETED SNIPER SURVEY (NODE 5 - CETUS WIDE SEARCH)")
    logger.info("="*80)

    for node_name, bounds in TARGET_NODES.items():
        sniper = NodeSniper(node_name, bounds)
        sniper.hunt()