#!/usr/bin/env python3

from generate_interactive_html import load_all_coverage_data, load_config
import csv

def analyze_sample_contributions():
    """Analyze which samples contribute to each contig"""
    
    print("Loading configuration...")
    config = load_config('config.yaml')
    
    print("Loading coverage data...")
    coverage_data = load_all_coverage_data(config['coverage_dir'])
    
    print("Analyzing sample contributions...")
    
    # Create summary: which samples contribute to each contig
    results = []
    for contig in coverage_data:
        contributing_samples = []
        for sample in coverage_data[contig]:
            # Check if sample has meaningful coverage (>0 for significant portion)
            coverages = [d['coverage'] for d in coverage_data[contig][sample]]
            if any(c > 0 for c in coverages):
                mean_cov = sum(coverages) / len(coverages)
                max_cov = max(coverages)
                # Only include if mean coverage > 0.1 (filter out very low coverage)
                if mean_cov > 0.1:
                    contributing_samples.append((sample, mean_cov, max_cov))
        
        # Sort by mean coverage (highest first)
        contributing_samples.sort(key=lambda x: x[1], reverse=True)
        
        results.append({
            'contig': contig,
            'num_contributing_samples': len(contributing_samples),
            'contributing_samples': contributing_samples
        })
    
    # Sort by number of contributing samples (most broadly supported first)
    results.sort(key=lambda x: x['num_contributing_samples'], reverse=True)
    
    print(f"\n{'='*60}")
    print("SAMPLE CONTRIBUTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total contigs analyzed: {len(results)}")
    print(f"Total samples in dataset: {len(set(sample for result in results for sample, _, _ in result['contributing_samples']))}")
    print(f"{'='*60}\n")
    
    # Print summary
    for result in results:
        print(f"{result['contig']}: {result['num_contributing_samples']} samples contribute")
        
        # Show top contributing samples
        top_samples = result['contributing_samples'][:5]
        for sample, mean_cov, max_cov in top_samples:
            print(f"  - {sample}: mean={mean_cov:.1f}, max={max_cov:.1f}")
        
        if len(result['contributing_samples']) > 5:
            remaining = len(result['contributing_samples']) - 5
            print(f"  ... and {remaining} more samples")
        
        print()
    
    # Save detailed results to CSV
    csv_filename = 'sample_contributions_detailed.csv'
    print(f"Saving detailed results to {csv_filename}...")
    
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Contig', 'Sample', 'Mean_Coverage', 'Max_Coverage', 'Rank'])
        
        for result in results:
            for rank, (sample, mean_cov, max_cov) in enumerate(result['contributing_samples'], 1):
                writer.writerow([result['contig'], sample, f"{mean_cov:.2f}", f"{max_cov:.2f}", rank])
    
    print(f"✓ Analysis complete! Detailed results saved to {csv_filename}")

if __name__ == "__main__":
    analyze_sample_contributions()