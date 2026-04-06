# Archival Materials — Flat Irrational Torus Model

This folder contains metadata and manifests for long-term preservation of the project.

## 📄 Files

| File | Purpose |
|------|---------|
| `zenodo_metadata.json` | Structured metadata for Zenodo upload |
| `archive_manifest.txt` | Human-readable inventory of archived contents |
| `checksums.sha256` | SHA256 hashes for integrity verification (generated on upload) |

## 🗃 Archival Strategy

### Dual Preservation
1. **GitHub Repository**: Active development, issue tracking, community contributions
2. **Zenodo Archive**: Immutable snapshot with permanent DOI for citation

### Versioning
- Each Zenodo release corresponds to a Git tag (e.g., `v1.1.0`)
- Manuscript revisions trigger new archival versions
- DOI resolves to the latest version; previous versions remain accessible

### FAIR Principles
- **Findable**: DOI, keywords, ORCID, cross-references
- **Accessible**: Open access, no login required, standard formats
- **Interoperable**: JSON metadata, plain text manifests, open licenses
- **Reusable**: Clear licenses (MIT for code, CC-BY-4.0 for text), detailed documentation

## 🔍 Verification

After downloading from Zenodo, verify integrity:
```bash
sha256sum -c checksums.sha256
