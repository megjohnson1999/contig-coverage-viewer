# Interactive Contig Coverage Visualization - Session Summary

## What We Built

Created an interactive HTML-based heat map viewer for visualizing metagenomic contig coverage across multiple samples/timepoints with professional configuration system and optimized visualization.

### Input Data
- **Assembly**: `01_GEMM_057_contigs_5000bp.fasta` (91 contigs ≥5000bp)
- **Coverage files**: 7 timepoints from single patient (12M_hr, 18M_hr, 24M_hr, 30M_hr, 36M_hr, 48M_hr, 60M_hr)
- **Format**: Compressed BED files (`.per-base.bed.gz`) with per-base coverage data

### Final Product
- **Main tool**: `generate_interactive_html.py` - Configurable Python script
- **Configuration**: `config.yaml` - User-friendly path configuration
- **Output**: `interactive_coverage_viewer.html` - Self-contained HTML with embedded real data
- **Documentation**: Complete README and usage examples
- **Repository**: Published at https://github.com/megjohnson1999/contig-coverage-viewer

## Development Process

### 1. Initial Problem
- Interactive Python scripts (Streamlit, Dash) weren't working as expected
- User wanted browser-based interactive visualization

### 2. Visualization Evolution
We implemented and tested multiple visualization types:
- **Continuous line plots** - Traditional connected lines
- **Discontinuous line plots** - Lines that break at zero coverage (shows true gaps)
- **Stacked area charts** - Shows cumulative coverage contribution
- **Heat map** - Color-coded intensity view

### 3. Final Choice: Heat Map Only
- **Why chosen**: Best for showing which samples cover which regions
- **Advantages**: Scales well, no color confusion, clear gap visualization
- **Perfect for metagenomic data**: Shows true coverage patterns and gaps

### 4. Interface Simplification & Optimization
- Removed unnecessary controls (smoothing, y-axis scale, visualization type selector)
- Fixed legend positioning issues (top cutoff, text overlap)
- Streamlined to essential controls: contig selection only
- Removed obsolete sample color legend from line plot era

## Data Verification

### Confirmed 100% Real Data
- **No synthetic data**: All visualizations use actual experimental data
- **Data sources**: Real FASTA contigs and BED coverage files
- **Sample verification**: Confirmed actual contig names (k127_559, k127_9975, etc.) and coverage values

### Arbitrary Thresholds Identified
1. **BED format check** (`>= 4 columns`) - Standard and necessary
2. **Performance binning** (`~1000 bins max`) - For browser performance with long contigs
3. **Zero coverage visualization** (`> 0` threshold) - Gray for no coverage, colored scale for all other values

## Key Technical Features

### Configuration System
- **YAML configuration file** (`config.yaml`) for easy path setup
- **Command line arguments** to override any setting
- **Optional PyYAML dependency** (graceful fallback to defaults)
- **File validation** and clear error messages
- **Custom titles and dataset names** for branding

### Data Processing
- Reads compressed BED files directly
- Extracts sample names from filenames
- Sorts coverage data by position
- Embeds all data in self-contained HTML

### Visualization
- **D3.js-based heat map** with blues color scale
- **Log scale color mapping** for better dynamic range
- **Intuitive color scheme**: White = no coverage, Dark blue = high coverage
- **Performance binning** for long contigs (~1000 bins max)
- **Interactive tooltips** showing exact coverage values
- **Responsive design** with proper legend positioning

### Performance
- Handles 91 contigs × 7 samples efficiently
- Automatic binning prevents browser performance issues
- Self-contained file (no server required)
- GitHub repository ready for sharing

## Future Considerations

### Scaling to Larger Datasets
Discussed expanding to assemblies from hundreds of patients:
- **Heat maps still preferred** - Avoid color confusion of line plots
- **Potential enhancements needed**:
  - Sample grouping/filtering capabilities
  - Hierarchical viewing (groups → individuals)
  - Better navigation for large sample sets
  - Metadata integration for logical sample organization

### Normalization Decision
**Conclusion: No normalization needed for this use case**
- **Goal**: Evaluate which samples contributed reads to assembly
- **Raw coverage shows**: Actual contribution of each sample to contig assembly
- **Why not normalize**: Want to see true differences in sample contribution
- **Sequencing depth differences**: Informative for assembly evaluation
- **Save normalization for**: Biological abundance questions, not assembly evaluation

## Files Created
- `generate_interactive_html.py` - Main Python tool with configuration support
- `config.yaml` - User-friendly configuration file
- `interactive_coverage_viewer.html` - Demo visualization with real data
- `README.md` - Comprehensive documentation with examples
- `session_summary.md` - This development summary
- `.gitignore` - Protects private data files

## GitHub Repository
**Published at:** https://github.com/megjohnson1999/contig-coverage-viewer

**Repository includes:**
- Complete working tool with configuration system
- Real data demo (28MB HTML file with embedded GEMM_057 data)
- Professional documentation with usage examples
- ASCII art visualization examples in README
- Protection for private data files via .gitignore

## Key Insights
1. **Heat maps are superior** for multi-sample metagenomic coverage visualization
2. **Raw coverage (not normalized)** is appropriate for assembly evaluation
3. **Interactive browser-based tools** can be more practical than Python scripts
4. **Self-contained HTML files** provide excellent portability and sharing
5. **Log scale visualization** is scientifically appropriate for coverage data with large dynamic ranges
6. **Configuration systems** make tools much more user-friendly
7. **Blues color scale** is more intuitive than Viridis for coverage (dark = dense)
8. **GitHub repositories** are excellent for sharing computational biology tools