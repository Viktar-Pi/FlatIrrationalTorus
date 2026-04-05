cat > scripts/download_data.sh << 'EOF'
#!/usr/bin/env bash
# download_data.sh — Автоматическая загрузка данных Planck PR4
set -euo pipefail

DATA_DIR="${1:-data}"
mkdir -p "$DATA_DIR"

echo "📥 Загрузка данных Planck PR4 в $DATA_DIR/..."

# Карта температуры SMICA (~1.9 GB)
if [[ ! -f "$DATA_DIR/COM_CMB_IQU-smica_2048_R3.00_full.fits" ]]; then
    echo "   🗺️  SMICA map..."
    curl -L -o "$DATA_DIR/COM_CMB_IQU-smica_2048_R3.00_full.fits" \
        "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/maps/component-maps/cmb/COM_CMB_IQU-smica_2048_R3.00_full.fits"
fi

# Общая маска (~45 MB)
if [[ ! -f "$DATA_DIR/COM_Mask_CMB-common-Mask-Pol_2048_R3.00.fits" ]]; then
    echo "   🎭 Common mask..."
    curl -L -o "$DATA_DIR/COM_Mask_CMB-common-Mask-Pol_2048_R3.00.fits" \
        "https://irsa.ipac.caltech.edu/data/Planck/release_3/all-sky-maps/masks/COM_Mask_CMB-common-Mask-Pol_2048_R3.00.fits"
fi

# Спектр мощности (~800 KB)
if [[ ! -f "$DATA_DIR/COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt" ]]; then
    echo "   📈 Power spectrum..."
    curl -L -o "$DATA_DIR/COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt" \
        "https://pla.esac.esa.int/pla-sl/data-a-products/cmb/power-spectra/COM_PowerSpect_CMB-base-plikHM-TTTEEE-lowl-lowE-lensing-minimum-theory_R3.01.txt"
fi

# Генерация хешей
echo "🔐 Генерация контрольных сумм..."
find "$DATA_DIR" -type f \( -name "*.fits" -o -name "*.txt" \) -exec sha256sum {} \; > "$DATA_DIR/checksums.sha256"

echo "✅ Данные загружены. Проверка: sha256sum -c $DATA_DIR/checksums.sha256"
EOF
chmod +x scripts/download_data.sh
