#!/usr/bin/env python3

from generate_interactive_html import load_all_coverage_data, load_config, generate_html, get_contigs_from_fasta

def create_filtered_visualization(min_mean_coverage=1.0, max_samples=50):
    """Create visualization for all contigs with sample filtering"""
    
    print("Loading configuration...")
    config = load_config('config.yaml')
    
    print("Loading all coverage data...")
    all_coverage_data = load_all_coverage_data(config['coverage_dir'])
    
    print("Loading contig names...")
    all_contigs = get_contigs_from_fasta(config['fasta_path'])
    
    print(f"Applying filtering (min coverage: {min_mean_coverage}, max samples: {max_samples})...")
    
    # Apply filtering to all contigs
    filtered_coverage_data = {}
    total_samples_before = 0
    total_samples_after = 0
    
    for contig in all_contigs:
        if contig not in all_coverage_data:
            continue
        
        contig_data = all_coverage_data[contig]
        total_samples_before += len(contig_data)
        
        # Calculate mean coverage and filter
        sample_stats = []
        for sample, coverage_points in contig_data.items():
            if coverage_points:
                mean_cov = sum(point['coverage'] for point in coverage_points) / len(coverage_points)
                if mean_cov >= min_mean_coverage:
                    sample_stats.append((sample, mean_cov, coverage_points))
        
        # Keep top N samples by coverage
        sample_stats.sort(key=lambda x: x[1], reverse=True)
        top_samples = sample_stats[:max_samples]
        
        if top_samples:
            filtered_coverage_data[contig] = {sample: coverage_points for sample, _, coverage_points in top_samples}
            total_samples_after += len(top_samples)
            print(f"  {contig}: {len(top_samples)} of {len(contig_data)} samples")
    
    print(f"\nFiltering summary:")
    print(f"  Contigs: {len(filtered_coverage_data)} of {len(all_contigs)}")
    print(f"  Total samples before: {total_samples_before}")
    print(f"  Total samples after: {total_samples_after}")
    print(f"  Data reduction: {(1 - total_samples_after/total_samples_before)*100:.1f}%")
    
    # Count unique samples
    unique_samples = set()
    for contig_data in filtered_coverage_data.values():
        unique_samples.update(contig_data.keys())
    
    print(f"  Unique samples in final dataset: {len(unique_samples)}")
    
    # Generate HTML
    output_file = 'all_contigs_filtered.html'
    title = 'All Contigs - Filtered Dataset'
    dataset_name = f'All {len(filtered_coverage_data)} contigs, top contributors only (max {max_samples} per contig)'
    
    print("\nGenerating HTML visualization...")
    generate_html(all_contigs, filtered_coverage_data, output_file, title, dataset_name)
    
    print(f"✓ Filtered visualization created: {output_file}")
    
    # Estimate file size
    estimated_mb = len(filtered_coverage_data) * max_samples * 0.3 / 1000  # Rough estimate
    print(f"  Estimated file size: ~{estimated_mb:.1f}MB")

if __name__ == "__main__":
    import sys
    
    min_coverage = 1.0
    max_samples = 50
    
    if len(sys.argv) > 1:
        min_coverage = float(sys.argv[1])
    if len(sys.argv) > 2:
        max_samples = int(sys.argv[2])
    
    print(f"Creating filtered visualization of all contigs:")
    print(f"  Minimum mean coverage: {min_coverage}")
    print(f"  Maximum samples per contig: {max_samples}")
    
    create_filtered_visualization(min_coverage, max_samples)