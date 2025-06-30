#!/usr/bin/env python3

import os
import glob
import gzip
import json
import sys
import argparse
from collections import defaultdict

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

def get_contigs_from_fasta(fasta_path):
    """Extract contig names from FASTA file"""
    contigs = []
    with open(fasta_path, 'r') as f:
        for line in f:
            if line.startswith('>'):
                contig_name = line[1:].split()[0]  # Get just the contig name
                contigs.append(contig_name)
    return contigs

def load_all_coverage_data(coverage_dir):
    """Load all coverage data from BED files"""
    files = glob.glob(os.path.join(coverage_dir, "*.per-base.bed.gz"))
    coverage_data = defaultdict(lambda: defaultdict(list))
    
    print(f"Processing {len(files)} coverage files...")
    
    for i, file_path in enumerate(files):
        # Extract sample name from filename (use full filename minus extensions)
        sample_name = os.path.basename(file_path).split(".per-base.bed.gz")[0]
        
        print(f"Processing {sample_name}... ({i+1}/{len(files)})")
        
        with gzip.open(file_path, 'rt') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 4:
                    contig, start, end, coverage = parts[:4]
                    start = int(start)
                    coverage = float(coverage)
                    
                    coverage_data[contig][sample_name].append({
                        'position': start,
                        'coverage': coverage
                    })
    
    # Sort all coverage data by position
    for contig in coverage_data:
        for sample in coverage_data[contig]:
            coverage_data[contig][sample].sort(key=lambda x: x['position'])
    
    return dict(coverage_data)

def generate_html(contigs, coverage_data, output_path, title="Interactive Contig Coverage Viewer", dataset_name="Contig Coverage Analysis"):
    """Generate interactive HTML with embedded data"""
    
    # Convert data to JSON strings
    contigs_json = json.dumps(contigs)
    coverage_json = json.dumps(coverage_data)
    num_contigs = len(contigs)
    num_samples = len(set(sample for contig_data in coverage_data.values() for sample in contig_data.keys()))
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }}
        .controls {{
            margin-bottom: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            align-items: center;
        }}
        select {{
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            min-width: 200px;
        }}
        .info {{
            margin: 10px 0;
            padding: 10px;
            background-color: #e9ecef;
            border-radius: 4px;
            font-size: 14px;
        }}
        #chart {{
            margin: 20px 0;
        }}
        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            pointer-events: none;
            font-size: 12px;
            opacity: 0;
            z-index: 1000;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin: 10px 0;
        }}
        .stat-item {{
            background-color: #e9ecef;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="info">
            <strong>Dataset:</strong> {dataset_name} | 
            <strong>Contigs:</strong> {num_contigs} | 
            <strong>Samples:</strong> {num_samples}
        </div>
        
        <div class="controls">
            <div>
                <label for="contigSelect">Select Contig:</label>
                <select id="contigSelect">
                    <option value="">Choose a contig...</option>
                </select>
            </div>
        </div>
        
        <div id="contigInfo" class="info" style="display: none;"></div>
        <div id="stats" class="stats" style="display: none;"></div>
        <div id="chart"></div>
        <div class="tooltip" id="tooltip"></div>
    </div>

    <script>
        // Embedded data
        const contigs = {contigs_json};
        const coverageData = {coverage_json};
        
        const colors = d3.scaleOrdinal(d3.schemeSet3);
        const margin = {{top: 20, right: 100, bottom: 60, left: 80}};
        const width = 1200 - margin.left - margin.right;
        const height = 450 - margin.top - margin.bottom;

        // Initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {{
            populateContigSelect();
            document.getElementById('contigSelect').addEventListener('change', updateChart);
        }});

        function populateContigSelect() {{
            console.log('Populating contig dropdown with', contigs.length, 'contigs');
            const select = document.getElementById('contigSelect');
            
            if (!select) {{
                console.error('Select element with id "contigSelect" not found!');
                return;
            }}
            
            if (!contigs || contigs.length === 0) {{
                console.error('No contigs data available!');
                return;
            }}
            
            contigs.forEach(contig => {{
                const option = document.createElement('option');
                option.value = contig;
                option.textContent = contig;
                select.appendChild(option);
            }});
            
            console.log('Successfully added', contigs.length, 'contig options to dropdown');
        }}

        function smoothData(data, windowSize) {{
            if (windowSize <= 1) return data;
            
            const smoothed = [];
            for (let i = 0; i < data.length; i++) {{
                let sum = 0;
                let count = 0;
                const start = Math.max(0, i - Math.floor(windowSize/2));
                const end = Math.min(data.length - 1, i + Math.floor(windowSize/2));
                
                for (let j = start; j <= end; j++) {{
                    sum += data[j].coverage;
                    count++;
                }}
                
                smoothed.push({{
                    position: data[i].position,
                    coverage: sum / count
                }});
            }}
            return smoothed;
        }}

        function calculateStats(data) {{
            const values = data.map(d => d.coverage);
            const sum = values.reduce((a, b) => a + b, 0);
            const mean = sum / values.length;
            const sorted = [...values].sort((a, b) => a - b);
            const median = sorted[Math.floor(sorted.length / 2)];
            const max = Math.max(...values);
            
            return {{ mean, median, max, length: values.length }};
        }}

        function updateChart() {{
            const selectedContig = document.getElementById('contigSelect').value;
            
            if (!selectedContig || !coverageData[selectedContig]) {{
                document.getElementById('chart').innerHTML = '';
                document.getElementById('contigInfo').style.display = 'none';
                document.getElementById('stats').style.display = 'none';
                document.getElementById('legend').innerHTML = '';
                return;
            }}
            
            const contigData = coverageData[selectedContig];
            const samples = Object.keys(contigData).sort();
            
            // Show contig info
            const maxPosition = Math.max(...samples.map(sample => 
                Math.max(...contigData[sample].map(d => d.position))
            ));
            document.getElementById('contigInfo').innerHTML = 
                `<strong>Contig:</strong> ${{selectedContig}} | <strong>Length:</strong> ${{maxPosition.toLocaleString()}} bp | <strong>Samples:</strong> ${{samples.length}}`;
            document.getElementById('contigInfo').style.display = 'block';
            
            // Calculate and show stats
            const statsDiv = document.getElementById('stats');
            statsDiv.innerHTML = '';
            samples.forEach(sample => {{
                const stats = calculateStats(contigData[sample]);
                const statItem = document.createElement('div');
                statItem.className = 'stat-item';
                statItem.innerHTML = `<strong>${{sample}}</strong><br>
                    Mean: ${{stats.mean.toFixed(2)}} | Median: ${{stats.median.toFixed(2)}} | Max: ${{stats.max.toFixed(2)}}`;
                statsDiv.appendChild(statItem);
            }});
            statsDiv.style.display = 'grid';
            
            // Clear previous chart
            d3.select('#chart').selectAll('*').remove();
            
            // Draw heat map
            drawHeatMap(selectedContig, contigData, samples);
        }}
        
        function getAllPositions(processedSamples) {{
            const allPositions = new Set();
            Object.values(processedSamples).forEach(data => {{
                data.forEach(d => allPositions.add(d.position));
            }});
            return Array.from(allPositions).sort((a, b) => a - b);
        }}
        
        function getCoverageAtPosition(sampleData, position) {{
            const point = sampleData.find(d => d.position === position);
            return point ? point.coverage : 0;
        }}
        
        function drawHeatMap(selectedContig, contigData, samples) {{
            const processedSamples = {{}};
            samples.forEach(sample => {{
                processedSamples[sample] = contigData[sample];  // Use raw data without smoothing
            }});
            
            const allPositions = getAllPositions(processedSamples);
            const binSize = Math.max(1, Math.floor(allPositions.length / 1000)); // Limit to ~1000 bins for performance
            
            // Create binned data
            const binnedPositions = [];
            for (let i = 0; i < allPositions.length; i += binSize) {{
                const binStart = allPositions[i];
                const binEnd = allPositions[Math.min(i + binSize - 1, allPositions.length - 1)];
                const binCenter = (binStart + binEnd) / 2;
                binnedPositions.push({{ start: binStart, end: binEnd, center: binCenter }});
            }}
            
            // Calculate max coverage for color scaling
            const maxCoverage = Math.max(...samples.map(sample => 
                Math.max(...processedSamples[sample].map(d => d.coverage))
            ));
            
            // Use log scale for better coverage visualization
            const minCoverage = Math.max(0.1, d3.min(samples.map(sample => 
                d3.min(processedSamples[sample].filter(d => d.coverage > 0).map(d => d.coverage))
            )));
            
            const colorScale = d3.scaleSequential(d3.interpolateBlues)
                .domain([Math.log10(minCoverage), Math.log10(maxCoverage + 1)]);
            
            // Create SVG with different dimensions for heatmap
            const heatmapHeight = samples.length * 30 + 120; // Extra space for legend
            const svg = d3.select('#chart')
                .append('svg')
                .attr('width', width + margin.left + margin.right)
                .attr('height', heatmapHeight);
            
            const g = svg.append('g')
                .attr('transform', `translate(${{margin.left}},70)`);
            
            const xScale = d3.scaleLinear()
                .domain(d3.extent(allPositions))
                .range([0, width]);
            
            const yScale = d3.scaleBand()
                .domain(samples)
                .range([0, samples.length * 30])
                .padding(0.1);
            
            // Draw heatmap rectangles
            samples.forEach(sample => {{
                binnedPositions.forEach(bin => {{
                    // Calculate average coverage for this bin
                    const relevantPoints = processedSamples[sample].filter(d => 
                        d.position >= bin.start && d.position <= bin.end
                    );
                    const avgCoverage = relevantPoints.length > 0 ? 
                        relevantPoints.reduce((sum, d) => sum + d.coverage, 0) / relevantPoints.length : 0;
                    
                    g.append('rect')
                        .attr('x', xScale(bin.start))
                        .attr('y', yScale(sample))
                        .attr('width', Math.max(1, xScale(bin.end) - xScale(bin.start)))
                        .attr('height', yScale.bandwidth())
                        .attr('fill', avgCoverage > 0 ? colorScale(Math.log10(avgCoverage + 0.1)) : '#f0f0f0')
                        .attr('stroke', 'none');
                }});
            }});
            
            // Add axes
            g.append('g')
                .attr('transform', `translate(0,${{samples.length * 30}})`)
                .call(d3.axisBottom(xScale).tickFormat(d => d.toLocaleString()));
            
            g.append('g')
                .call(d3.axisLeft(yScale));
            
            // Add axis labels
            g.append('text')
                .attr('transform', `translate(${{width/2}},${{samples.length * 30 + 40}})`)
                .style('text-anchor', 'middle')
                .style('font-size', '12px')
                .text('Position (bp)');
            
            g.append('text')
                .attr('transform', 'rotate(-90)')
                .attr('y', -60)
                .attr('x', -(samples.length * 15))
                .style('text-anchor', 'middle')
                .style('font-size', '12px')
                .text('Samples');
            
            // Add color scale legend
            const legendWidth = 180;
            const legendHeight = 10;
            const legend = svg.append('g')
                .attr('transform', `translate(${{width - legendWidth + margin.left - 30}},40)`);
            
            const legendScale = d3.scaleLinear()
                .domain([Math.log10(minCoverage), Math.log10(maxCoverage + 1)])
                .range([0, legendWidth]);
            
            const legendAxis = d3.axisTop(legendScale)
                .ticks(5)
                .tickFormat(d => Math.round(Math.pow(10, d)));
            
            // Create gradient
            const gradient = svg.append('defs')
                .append('linearGradient')
                .attr('id', 'coverage-gradient')
                .attr('x1', '0%').attr('x2', '100%');
            
            const steps = 20;
            for (let i = 0; i <= steps; i++) {{
                const logValue = Math.log10(minCoverage) + (i / steps) * (Math.log10(maxCoverage + 1) - Math.log10(minCoverage));
                gradient.append('stop')
                    .attr('offset', `${{(i / steps) * 100}}%`)
                    .attr('stop-color', colorScale(logValue));
            }}
            
            legend.append('rect')
                .attr('width', legendWidth)
                .attr('height', legendHeight)
                .style('fill', 'url(#coverage-gradient)');
            
            legend.append('g')
                .call(legendAxis);
            
            legend.append('text')
                .attr('x', legendWidth / 2)
                .attr('y', -30)
                .style('text-anchor', 'middle')
                .style('font-size', '10px')
                .text('Coverage (log scale)');
        }}
        

    </script>
</body>
</html>"""
    
    with open(output_path, 'w') as f:
        f.write(html_content)

def load_config(config_path="config.yaml"):
    """Load configuration from YAML file or return defaults"""
    default_config = {
        'fasta_path': "01_GEMM_057_contigs_5000bp.fasta",
        'coverage_dir': "coverage_5000bp",
        'output_path': "interactive_coverage_viewer.html",
        'title': "Interactive Contig Coverage Viewer",
        'dataset_name': "Contig Coverage Analysis"
    }
    
    if os.path.exists(config_path) and YAML_AVAILABLE:
        print(f"Loading configuration from {config_path}")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        # Merge with defaults
        for key in default_config:
            if key not in config:
                config[key] = default_config[key]
        return config
    elif os.path.exists(config_path) and not YAML_AVAILABLE:
        print(f"Warning: {config_path} found but PyYAML not installed. Using default configuration.")
        print("Install PyYAML with: pip install pyyaml")
        return default_config
    else:
        print(f"No config file found at {config_path}, using default configuration")
        return default_config

def main():
    parser = argparse.ArgumentParser(description='Generate interactive contig coverage visualization')
    parser.add_argument('--config', '-c', default='config.yaml', 
                       help='Path to configuration file (default: config.yaml)')
    parser.add_argument('--fasta', help='Path to assembly FASTA file (overrides config)')
    parser.add_argument('--coverage-dir', help='Directory with coverage BED files (overrides config)')
    parser.add_argument('--output', '-o', help='Output HTML file path (overrides config)')
    parser.add_argument('--title', help='Title for the visualization (overrides config)')
    parser.add_argument('--dataset-name', help='Dataset name for display (overrides config)')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.fasta:
        config['fasta_path'] = args.fasta
    if args.coverage_dir:
        config['coverage_dir'] = args.coverage_dir
    if args.output:
        config['output_path'] = args.output
    if args.title:
        config['title'] = args.title
    if args.dataset_name:
        config['dataset_name'] = args.dataset_name
    
    # Validate input files exist
    if not os.path.exists(config['fasta_path']):
        print(f"Error: FASTA file not found: {config['fasta_path']}")
        sys.exit(1)
    
    if not os.path.exists(config['coverage_dir']):
        print(f"Error: Coverage directory not found: {config['coverage_dir']}")
        sys.exit(1)
    
    print(f"Configuration:")
    print(f"  FASTA file: {config['fasta_path']}")
    print(f"  Coverage directory: {config['coverage_dir']}")
    print(f"  Output file: {config['output_path']}")
    print(f"  Title: {config['title']}")
    print(f"  Dataset: {config['dataset_name']}")
    print()
    
    print("Loading contig names from FASTA...")
    contigs = get_contigs_from_fasta(config['fasta_path'])
    print(f"Found {len(contigs)} contigs")
    
    print("Loading coverage data...")
    coverage_data = load_all_coverage_data(config['coverage_dir'])
    print(f"Loaded coverage data for {len(coverage_data)} contigs")
    
    print("Generating interactive HTML...")
    generate_html(contigs, coverage_data, config['output_path'], 
                 config['title'], config['dataset_name'])
    
    print(f"✓ Interactive HTML generated: {config['output_path']}")
    print(f"Open {config['output_path']} in your web browser to view the interactive coverage plots!")

if __name__ == "__main__":
    main()