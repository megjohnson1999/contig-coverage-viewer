# Coverage Filtering Implementation Summary

## Overview
Implemented sample filtering functionality to display only samples with meaningful coverage for each contig, reducing visual noise and focusing on samples that actually contribute to the assembly.

## Features Added

### 1. Configurable Filtering Thresholds
- **`min_mean_coverage`**: Minimum mean coverage across all positions (default: 1.0)
- **`min_max_coverage`**: Minimum maximum coverage at any position (default: 5.0)

### 2. Configuration Options
- **Config file**: Add thresholds to `config.yaml`
- **Command line**: Override with `--min-mean-coverage` and `--min-max-coverage`
- **Backward compatibility**: Existing scripts continue to work unchanged

### 3. Filtering Results
With the default thresholds (mean ≥ 1.0, max ≥ 5.0):
- **Before filtering**: 405 sample-contig pairs
- **After filtering**: 269 sample-contig pairs  
- **Reduction**: 136 pairs (33.6%) removed

With stricter thresholds (mean ≥ 2.0, max ≥ 10.0):
- **After filtering**: 224 sample-contig pairs
- **Reduction**: 181 pairs (44.7%) removed

## Usage Examples

### Basic Usage (Default Filtering)
```bash
python generate_interactive_html.py
```

### Custom Filtering Thresholds
```bash
# More permissive filtering
python generate_interactive_html.py --min-mean-coverage 0.5 --min-max-coverage 2.0

# Stricter filtering
python generate_interactive_html.py --min-mean-coverage 2.0 --min-max-coverage 10.0
```

### Disable Filtering (Original Behavior)
```bash
python generate_interactive_html.py --min-mean-coverage 0 --min-max-coverage 0
```

## Configuration File
Add to `config.yaml`:
```yaml
# Coverage filtering thresholds
min_mean_coverage: 1.0  # Minimum mean coverage for sample to be included
min_max_coverage: 5.0   # Minimum max coverage for sample to be included
```

## Implementation Details

### Filtering Logic
For each sample-contig pair:
1. Calculate mean coverage across all positions
2. Calculate maximum coverage at any position
3. Include sample only if both thresholds are met

### Backward Compatibility
- Existing scripts importing `load_all_coverage_data()` continue to work
- When no filtering parameters are provided, returns all data (original behavior)
- Optional parameters with sensible defaults

## Generated Files
- `filtered_coverage_viewer.html` - Default filtering (mean≥1.0, max≥5.0)
- `strict_filtered_coverage_viewer.html` - Strict filtering (mean≥2.0, max≥10.0)
- `test_coverage_filtering.py` - Test script to verify filtering behavior

## Benefits
1. **Reduced visual noise**: Only shows samples with meaningful coverage
2. **Better focus**: Highlights samples that actually contribute to assembly
3. **Cleaner visualization**: Fewer empty or low-coverage rows in heatmaps
4. **Configurable**: Adjustable thresholds for different analysis needs
5. **Backward compatible**: Doesn't break existing workflows