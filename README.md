# Interactive Contig Coverage Viewer

An interactive browser-based tool for visualizing metagenomic contig coverage across multiple samples using heat maps.

## Overview

This tool helps evaluate metagenomic assemblies by showing which samples contributed reads to each contig. It displays per-base coverage data as an interactive heat map where each row represents a sample and colors indicate coverage intensity.

## Features

- **Interactive heat map visualization** - Clear view of coverage patterns across contig positions
- **Sample comparison** - See which samples cover which regions
- **Coverage statistics** - Mean, median, and maximum coverage per sample
- **Self-contained HTML output** - No server required, works in any modern browser
- **Performance optimized** - Handles large contigs efficiently with automatic binning

## Quick Start

1. **Prepare your data**:
   - FASTA file with contigs
   - Per-base coverage files (`.bed` or `.bed.gz` format)

2. **Generate the viewer**:
   ```bash
   python generate_interactive_html.py
   ```

3. **Open the visualization**:
   - Open `interactive_coverage_viewer.html` in your web browser
   - Select a contig from the dropdown to view its coverage

## Input Data Format

### Required Files

- **Assembly FASTA**: `01_GEMM_057_contigs_5000bp.fasta`
  - Standard FASTA format with contig sequences
  - Contig names extracted from headers

- **Coverage Directory**: `coverage_5000bp/`
  - Per-base coverage files in BED format
  - Files can be compressed (`.bed.gz`) or uncompressed (`.bed`)
  - Sample names extracted from filenames

### BED File Format
```
contig_name    start    end    coverage
k127_559       0        25     1.0
k127_559       25       119    2.0
k127_559       119      162    3.0
```

## Usage

### Basic Usage
```bash
# Default settings (modify paths in script if needed)
python generate_interactive_html.py
```

### Customizing File Paths
Edit the configuration section in `generate_interactive_html.py`:
```python
# Configuration
fasta_path = "your_assembly.fasta"
coverage_dir = "your_coverage_directory"
output_path = "your_output.html"
```

## Output

### Interactive HTML File
- **Self-contained**: All data embedded, no external dependencies except D3.js CDN
- **Portable**: Can be shared via email, stored on any web server, or opened locally
- **Interactive features**:
  - Contig selection dropdown
  - Hover tooltips showing exact coverage values
  - Coverage statistics display
  - Color legend for intensity scale

### Visualization Details
- **Heat map layout**: Samples as rows, genomic positions as columns
- **Color scale**: Viridis colormap (purple = low, yellow = high coverage)
- **Zero coverage**: Gray color to distinguish from low coverage
- **Performance**: Automatic binning for contigs with >1000 coverage positions

## Use Cases

### Assembly Evaluation
- **Primary goal**: Determine which samples contributed reads to each contig
- **Sample contribution**: Identify dominant vs. minor contributors
- **Coverage gaps**: Visualize regions with no sequencing coverage
- **Quality assessment**: Evaluate assembly support across samples

### Multi-sample Analysis
- Compare coverage patterns between different samples/timepoints
- Identify sample-specific contigs
- Assess assembly completeness across sample sets

## Technical Details

### Dependencies
- **Python packages**: `os`, `glob`, `gzip`, `json`, `collections` (all standard library)
- **Visualization**: D3.js (loaded from CDN)
- **Browser**: Any modern web browser with JavaScript enabled

### Performance Considerations
- **Binning**: Contigs with >1000 positions are automatically binned for browser performance
- **Memory**: All data embedded in HTML file (consider file size for very large datasets)
- **Browser limits**: Very large datasets (hundreds of samples × long contigs) may require chunking

### Data Processing
1. **Contig extraction**: Reads FASTA headers to get contig names
2. **Coverage loading**: Parses all BED files in coverage directory
3. **Sample naming**: Extracts sample names from filenames
4. **Data embedding**: Converts all data to JSON and embeds in HTML template

## Normalization

**This tool uses raw coverage values (no normalization)**

- **Rationale**: For assembly evaluation, raw coverage shows actual sample contribution
- **Alternative**: For biological abundance analysis, consider normalizing by sequencing depth
- **Implementation**: Normalization can be added to the data processing step if needed

## Limitations

- **File size**: Large datasets create large HTML files
- **Browser memory**: Very large datasets may require browser with sufficient RAM
- **Static output**: Generated HTML is snapshot of data (not live-updating)

## Troubleshooting

### Common Issues

**No data displays when selecting contigs**
- Check that coverage files are in correct BED format
- Verify file paths in configuration section
- Ensure contig names match between FASTA and BED files

**Browser performance issues**
- Try with smaller datasets first
- Check browser console for JavaScript errors
- Consider using binning for very long contigs

**Empty coverage files**
- Verify BED files contain data for selected contigs
- Check file compression (script handles .gz automatically)

### File Path Issues
- Use absolute paths if relative paths cause problems
- Ensure coverage directory contains `.bed` or `.bed.gz` files
- Check that FASTA file is readable

## Example Dataset

The included example processes:
- **Assembly**: 91 contigs ≥5000bp from GEMM_057 sample
- **Samples**: 7 timepoints (12M_hr through 60M_hr)
- **Coverage**: Per-base coverage from metagenomic read mapping

## Contributing

To extend functionality:
1. **Add normalization**: Modify data loading to include depth normalization
2. **Enhance filtering**: Add sample filtering capabilities
3. **Improve UI**: Add search, sorting, or grouping features
4. **Scale performance**: Implement virtual scrolling for very large datasets

## License

This tool is provided as-is for research purposes.