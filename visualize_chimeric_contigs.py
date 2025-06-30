#!/usr/bin/env python3

from generate_interactive_html import load_all_coverage_data, load_config, generate_html, get_contigs_from_fasta
import sys

def identify_chimeric_contigs(min_score=0.6):
    """Identify potentially chimeric contigs using the screening algorithm"""
    print("Screening for chimeric contigs...")
    config = load_config('config.yaml')
    coverage_data = load_all_coverage_data(config['coverage_dir'])
    
    chimeric_contigs = []
    
    for contig_name in coverage_data:
        contig_data = coverage_data[contig_name]
        
        # Get all positions
        all_positions = set()
        for sample in contig_data:
            for point in contig_data[sample]:
                all_positions.add(point['position'])
        
        all_positions = sorted(all_positions)
        contig_length = max(all_positions) if all_positions else 0
        
        if contig_length < 1000:  # Skip very short contigs
            continue
        
        # Divide into 5 segments
        num_segments = 5
        segment_size = contig_length // num_segments
        
        segment_leaders = []
        for seg_idx in range(num_segments):
            seg_start = seg_idx * segment_size
            seg_end = (seg_idx + 1) * segment_size if seg_idx < num_segments - 1 else contig_length
            
            segment_coverage = {}
            for sample in contig_data:
                total_cov = 0
                positions_in_segment = 0
                
                for point in contig_data[sample]:
                    if seg_start <= point['position'] < seg_end:
                        total_cov += point['coverage']
                        positions_in_segment += 1
                
                if positions_in_segment > 0:
                    mean_cov = total_cov / positions_in_segment
                    if mean_cov >= 5:  # Lower threshold for screening
                        segment_coverage[sample] = mean_cov
            
            if segment_coverage:
                leader = max(segment_coverage.items(), key=lambda x: x[1])
                segment_leaders.append(leader[0])
        
        # Score based on number of different leaders
        unique_leaders = len(set(leader for leader in segment_leaders if leader is not None))
        if len(segment_leaders) > 0:
            chimera_score = unique_leaders / len(segment_leaders)
            if chimera_score >= min_score:
                chimeric_contigs.append((contig_name, chimera_score, unique_leaders))
    
    return sorted(chimeric_contigs, key=lambda x: x[1], reverse=True)

def create_chimeric_visualization(min_score=0.6, output_suffix="chimeric"):
    """Create visualization for only the chimeric contigs"""
    
    # Identify chimeric contigs
    chimeric_contigs = identify_chimeric_contigs(min_score)
    
    if not chimeric_contigs:
        print(f"No contigs found with chimera score >= {min_score}")
        return
    
    chimeric_names = [contig[0] for contig in chimeric_contigs]
    
    print(f"Found {len(chimeric_names)} potentially chimeric contigs:")
    for name, score, leaders in chimeric_contigs:
        print(f"  {name}: score={score:.2f} ({leaders} different segment leaders)")
    
    # Load all data
    config = load_config('config.yaml')
    all_coverage_data = load_all_coverage_data(config['coverage_dir'])
    
    # Filter to only chimeric contigs
    filtered_coverage_data = {contig: all_coverage_data[contig] 
                            for contig in chimeric_names 
                            if contig in all_coverage_data}
    
    # Count total samples in filtered data
    all_samples = set()
    for contig_data in filtered_coverage_data.values():
        all_samples.update(contig_data.keys())
    
    print(f"Filtered dataset: {len(filtered_coverage_data)} contigs, {len(all_samples)} samples")
    
    # Generate HTML with custom naming
    output_filename = f"chimeric_contigs_{output_suffix}.html"
    title = f"Potentially Chimeric Contigs (Score ≥ {min_score})"
    dataset_name = f"Chimeric Contigs Analysis - {len(chimeric_names)} contigs, {len(all_samples)} samples"
    
    generate_html(
        contigs=chimeric_names,
        coverage_data=filtered_coverage_data,
        output_path=output_filename,
        title=title,
        dataset_name=dataset_name
    )
    
    print(f"✓ Chimeric contig visualization created: {output_filename}")
    
    # Also create a summary report
    summary_filename = f"chimeric_contigs_summary_{output_suffix}.txt"
    with open(summary_filename, 'w') as f:
        f.write("CHIMERIC CONTIGS ANALYSIS SUMMARY\n")
        f.write("="*50 + "\n\n")
        f.write(f"Analysis parameters:\n")
        f.write(f"  Minimum chimera score: {min_score}\n")
        f.write(f"  Total contigs flagged: {len(chimeric_names)}\n")
        f.write(f"  Total samples involved: {len(all_samples)}\n\n")
        
        f.write("Flagged contigs:\n")
        f.write("-" * 50 + "\n")
        for name, score, leaders in chimeric_contigs:
            f.write(f"{name:<15} Score: {score:.2f}  Leaders: {leaders}\n")
        
        f.write(f"\nVisualization file: {output_filename}\n")
        f.write("Open this HTML file in a web browser to explore the coverage patterns.\n")
    
    print(f"✓ Summary report created: {summary_filename}")

if __name__ == "__main__":
    # Parse command line arguments
    min_score = 0.6  # Default threshold
    output_suffix = "analysis"
    
    if len(sys.argv) > 1:
        try:
            min_score = float(sys.argv[1])
        except ValueError:
            print("Usage: python visualize_chimeric_contigs.py [min_score] [output_suffix]")
            print("Example: python visualize_chimeric_contigs.py 0.8 strict")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        output_suffix = sys.argv[2]
    
    print(f"Creating visualization for contigs with chimera score ≥ {min_score}")
    create_chimeric_visualization(min_score, output_suffix)