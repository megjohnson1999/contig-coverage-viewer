# Interactive Contig Coverage Visualization - Session Summary

## What We Built

Created an interactive HTML-based heat map viewer for visualizing metagenomic contig coverage across multiple samples/timepoints.

### Input Data
- **Assembly**: `01_GEMM_057_contigs_5000bp.fasta` (91 contigs ≥5000bp)
- **Coverage files**: 7 timepoints from single patient (12M_hr, 18M_hr, 24M_hr, 30M_hr, 36M_hr, 48M_hr, 60M_hr)
- **Format**: Compressed BED files (`.per-base.bed.gz`) with per-base coverage data

### Final Product
- **File**: `interactive_coverage_viewer.html` - Self-contained HTML file with embedded data
- **Visualization**: Heat map showing coverage intensity across contig positions
- **Interface**: Simple dropdown to select contigs, coverage statistics, color legend

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

### 4. Interface Simplification
- Removed unnecessary controls (smoothing, y-axis scale, visualization type selector)
- Fixed y-axis label positioning
- Streamlined to just contig selection

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

### Data Processing
- Reads compressed BED files directly
- Extracts sample names from filenames
- Sorts coverage data by position
- Embeds all data in self-contained HTML

### Visualization
- D3.js-based heat map
- Viridis color scale for coverage intensity
- Binning for performance with long contigs
- Interactive tooltips and legends
- Responsive design

### Performance
- Handles 91 contigs × 7 samples efficiently
- Automatic binning prevents browser performance issues
- Self-contained file (no server required)

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
- `generate_interactive_html.py` - Python script to process data and generate HTML
- `interactive_coverage_viewer.html` - Final interactive visualization
- `session_summary.md` - This summary document

## Key Insights
1. Heat maps are superior for multi-sample metagenomic coverage visualization
2. Raw coverage (not normalized) is appropriate for assembly evaluation
3. Interactive browser-based tools can be more practical than Python scripts
4. Self-contained HTML files provide excellent portability and sharing capabilities
5. Simplicity in interface design often leads to better usability