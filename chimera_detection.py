#!/usr/bin/env python3

from generate_interactive_html import load_all_coverage_data, load_config
import csv

def analyze_coverage_distribution(contig_name, min_coverage=10):
    """Analyze coverage distribution along a specific contig to detect potential chimerism"""
    
    print(f"Analyzing coverage distribution for {contig_name}...")
    config = load_config('config.yaml')
    coverage_data = load_all_coverage_data(config['coverage_dir'])
    
    if contig_name not in coverage_data:
        print(f"Error: Contig '{contig_name}' not found!")
        available = list(coverage_data.keys())[:10]
        print(f"Available contigs (first 10): {available}")
        return
    
    contig_data = coverage_data[contig_name]
    
    # Get all positions across all samples
    all_positions = set()
    for sample in contig_data:
        for point in contig_data[sample]:
            all_positions.add(point['position'])
    
    all_positions = sorted(all_positions)
    contig_length = max(all_positions) if all_positions else 0
    
    print(f"Contig length: {contig_length:,} bp")
    print(f"Total coverage positions: {len(all_positions):,}")
    
    # Divide contig into segments for analysis
    num_segments = min(10, len(all_positions) // 100)  # Max 10 segments, min 100 positions per segment
    if num_segments < 3:
        num_segments = 3
    
    segment_size = contig_length // num_segments
    
    print(f"\nAnalyzing {num_segments} segments of ~{segment_size:,} bp each:")
    print("="*80)
    
    # Find top contributors for each segment
    for seg_idx in range(num_segments):
        seg_start = seg_idx * segment_size
        seg_end = (seg_idx + 1) * segment_size if seg_idx < num_segments - 1 else contig_length
        
        # Get coverage for each sample in this segment
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
                if mean_cov >= min_coverage:
                    segment_coverage[sample] = mean_cov
        
        # Sort by coverage
        top_samples = sorted(segment_coverage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        print(f"Segment {seg_idx + 1}: {seg_start:,}-{seg_end:,} bp")
        if top_samples:
            for sample, cov in top_samples:
                # Shorten sample name for display
                short_name = sample.split('_')[-3:]  # Take last 3 parts
                short_name = '_'.join(short_name)
                print(f"  {short_name:<30} {cov:>8.1f}")
        else:
            print("  (No samples with significant coverage)")
        print()
    
    # Summary analysis
    print("CHIMERISM ASSESSMENT:")
    print("="*50)
    
    # Check if different samples dominate different segments
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
                if mean_cov >= min_coverage:
                    segment_coverage[sample] = mean_cov
        
        if segment_coverage:
            leader = max(segment_coverage.items(), key=lambda x: x[1])
            segment_leaders.append(leader[0])
        else:
            segment_leaders.append(None)
    
    # Count unique leaders
    unique_leaders = set(leader for leader in segment_leaders if leader is not None)
    
    print(f"Number of different 'dominant' samples across segments: {len(unique_leaders)}")
    
    if len(unique_leaders) <= 2:
        print("✓ LIKELY GENUINE: Same sample(s) dominate most segments")
    elif len(unique_leaders) <= 4:
        print("⚠ POSSIBLY CHIMERIC: Multiple different samples dominate different segments")
    else:
        print("⚠ LIKELY CHIMERIC: Many different samples dominate different segments")
    
    print(f"Segment leaders: {segment_leaders}")

def quick_chimera_scan():
    """Quick scan of all contigs to flag potential chimeras"""
    print("Quick chimera screening of all contigs...")
    config = load_config('config.yaml')
    coverage_data = load_all_coverage_data(config['coverage_dir'])
    
    chimera_scores = []
    
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
            chimera_scores.append((contig_name, chimera_score, unique_leaders, len(segment_leaders)))
    
    # Sort by chimera score (highest first)
    chimera_scores.sort(key=lambda x: x[1], reverse=True)
    
    print("\nCHIMERA SCREENING RESULTS:")
    print("="*60)
    print("Contig                Score  Leaders/Segments  Assessment")
    print("-"*60)
    
    for contig, score, leaders, segments in chimera_scores:
        if score >= 0.8:
            assessment = "LIKELY CHIMERIC"
        elif score >= 0.6:
            assessment = "POSSIBLY CHIMERIC"
        else:
            assessment = "Likely genuine"
        
        print(f"{contig:<20} {score:>6.2f}  {leaders:>2}/{segments:<2}          {assessment}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Analyze specific contig
        contig_name = sys.argv[1]
        analyze_coverage_distribution(contig_name)
    else:
        # Run quick screening
        quick_chimera_scan()
        print("\nTo analyze a specific contig in detail:")
        print("python chimera_detection.py contig_21")