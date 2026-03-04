#!/usr/bin/env python3
"""
Agent Nudge Experiment — Analysis Script
Processes results.csv and generates key metrics + visualizations.

Usage: python analyze.py [--data path/to/results.csv] [--output path/to/figures/]
"""

import argparse
import csv
import os
import json
from collections import defaultdict

# Try importing visualization libraries — graceful fallback if not available
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import numpy as np
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("⚠ matplotlib not installed — text analysis only. Install with: pip install matplotlib numpy")


def wilson_ci(successes, n, z=1.96):
    """Wilson score confidence interval for a proportion."""
    if n == 0:
        return (0, 0)
    p = successes / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2*n)) / denom
    spread = z * ((p*(1-p)/n + z**2/(4*n**2)) ** 0.5) / denom
    return (max(0, center - spread), min(1, center + spread))


def load_data(filepath):
    """Load and validate results CSV."""
    rows = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['correct'] = int(row.get('correct', 0))
            row['nudged'] = int(row.get('nudged', 0))
            rows.append(row)
    return rows


def compute_metrics(data):
    """Compute all key metrics from raw data."""
    agents = sorted(set(r['agent'] for r in data))
    variants = ['control', 'default-selection', 'position-bias', 'social-proof', 'urgency', 'anchoring']
    
    metrics = {
        'by_variant': {},
        'by_agent': {},
        'by_agent_variant': {},
        'summary': {}
    }
    
    # Per-variant metrics (aggregated across agents)
    for v in variants:
        subset = [r for r in data if r['variant'] == v]
        n = len(subset)
        if n == 0:
            continue
        
        correct = sum(r['correct'] for r in subset)
        nudged = sum(r['nudged'] for r in subset)
        aware = sum(1 for r in subset if r.get('mentioned_manipulation', '').lower() == 'yes')
        
        metrics['by_variant'][v] = {
            'n': n,
            'correct_count': correct,
            'correct_rate': correct / n,
            'correct_ci': wilson_ci(correct, n),
            'nudged_count': nudged,
            'nudge_rate': nudged / n,
            'nudge_ci': wilson_ci(nudged, n),
            'awareness_rate': aware / n if v != 'control' else None,
        }
    
    # Per-agent metrics (aggregated across variants)
    for a in agents:
        subset = [r for r in data if r['agent'] == a]
        manip_subset = [r for r in subset if r['variant'] != 'control']
        n = len(subset)
        n_manip = len(manip_subset)
        
        metrics['by_agent'][a] = {
            'n': n,
            'overall_correct_rate': sum(r['correct'] for r in subset) / n if n else 0,
            'manipulation_nudge_rate': sum(r['nudged'] for r in manip_subset) / n_manip if n_manip else 0,
            'control_correct_rate': None,
        }
        
        control_subset = [r for r in subset if r['variant'] == 'control']
        if control_subset:
            metrics['by_agent'][a]['control_correct_rate'] = sum(r['correct'] for r in control_subset) / len(control_subset)
    
    # Per-agent-per-variant (for heatmap)
    for a in agents:
        metrics['by_agent_variant'][a] = {}
        for v in variants:
            subset = [r for r in data if r['agent'] == a and r['variant'] == v]
            n = len(subset)
            if n == 0:
                continue
            nudged = sum(r['nudged'] for r in subset)
            correct = sum(r['correct'] for r in subset)
            metrics['by_agent_variant'][a][v] = {
                'n': n,
                'nudge_rate': nudged / n,
                'correct_rate': correct / n,
            }
    
    # Summary
    all_manip = [r for r in data if r['variant'] != 'control']
    all_control = [r for r in data if r['variant'] == 'control']
    
    metrics['summary'] = {
        'total_runs': len(data),
        'total_agents': len(agents),
        'total_variants': len([v for v in variants if any(r['variant'] == v for r in data)]),
        'overall_control_correct_rate': sum(r['correct'] for r in all_control) / len(all_control) if all_control else 0,
        'overall_manipulation_nudge_rate': sum(r['nudged'] for r in all_manip) / len(all_manip) if all_manip else 0,
        'most_effective_manipulation': None,
        'most_susceptible_agent': None,
        'most_resistant_agent': None,
    }
    
    # Find most effective manipulation
    manip_rates = {v: m['nudge_rate'] for v, m in metrics['by_variant'].items() if v != 'control'}
    if manip_rates:
        metrics['summary']['most_effective_manipulation'] = max(manip_rates, key=manip_rates.get)
    
    # Find most/least susceptible agent
    agent_rates = {a: m['manipulation_nudge_rate'] for a, m in metrics['by_agent'].items()}
    if agent_rates:
        metrics['summary']['most_susceptible_agent'] = max(agent_rates, key=agent_rates.get)
        metrics['summary']['most_resistant_agent'] = min(agent_rates, key=agent_rates.get)
    
    return metrics, agents, variants


def print_report(metrics, agents, variants):
    """Print text-based analysis report."""
    s = metrics['summary']
    
    print("=" * 70)
    print("AGENT NUDGE EXPERIMENT — RESULTS")
    print("=" * 70)
    print(f"\nTotal runs: {s['total_runs']} across {s['total_agents']} agents and {s['total_variants']} variants")
    print(f"Control correct rate: {s['overall_control_correct_rate']:.0%}")
    print(f"Overall manipulation nudge rate: {s['overall_manipulation_nudge_rate']:.0%}")
    
    if s['most_effective_manipulation']:
        rate = metrics['by_variant'][s['most_effective_manipulation']]['nudge_rate']
        print(f"Most effective manipulation: {s['most_effective_manipulation']} ({rate:.0%} nudge rate)")
    
    if s['most_susceptible_agent']:
        rate = metrics['by_agent'][s['most_susceptible_agent']]['manipulation_nudge_rate']
        print(f"Most susceptible agent: {s['most_susceptible_agent']} ({rate:.0%} nudge rate)")
    
    if s['most_resistant_agent']:
        rate = metrics['by_agent'][s['most_resistant_agent']]['manipulation_nudge_rate']
        print(f"Most resistant agent: {s['most_resistant_agent']} ({rate:.0%} nudge rate)")
    
    # Per-variant table
    print("\n" + "-" * 70)
    print("MANIPULATION SUCCESS RATES BY VARIANT")
    print("-" * 70)
    print(f"{'Variant':<22} {'N':>4} {'Correct':>10} {'Nudged':>10} {'Nudge 95% CI':>16} {'Aware':>8}")
    print("-" * 70)
    
    for v in variants:
        m = metrics['by_variant'].get(v)
        if not m:
            continue
        ci_str = f"[{m['nudge_ci'][0]:.0%}-{m['nudge_ci'][1]:.0%}]"
        aware_str = f"{m['awareness_rate']:.0%}" if m['awareness_rate'] is not None else "n/a"
        print(f"{v:<22} {m['n']:>4} {m['correct_rate']:>9.0%} {m['nudge_rate']:>9.0%} {ci_str:>16} {aware_str:>8}")
    
    # Per-agent table
    print("\n" + "-" * 70)
    print("AGENT SUSCEPTIBILITY (across all manipulation variants)")
    print("-" * 70)
    print(f"{'Agent':<16} {'N':>4} {'Control Correct':>16} {'Manip Nudge Rate':>18}")
    print("-" * 70)
    
    for a in agents:
        m = metrics['by_agent'].get(a)
        if not m:
            continue
        ctrl = f"{m['control_correct_rate']:.0%}" if m['control_correct_rate'] is not None else "n/a"
        print(f"{a:<16} {m['n']:>4} {ctrl:>16} {m['manipulation_nudge_rate']:>17.0%}")
    
    # Heatmap as text
    print("\n" + "-" * 70)
    print("NUDGE RATE HEATMAP (agent × variant)")
    print("-" * 70)
    header = f"{'':>16}" + "".join(f"{v[:12]:>14}" for v in variants)
    print(header)
    for a in agents:
        row = f"{a:>16}"
        for v in variants:
            cell = metrics['by_agent_variant'].get(a, {}).get(v)
            if cell:
                row += f"{cell['nudge_rate']:>13.0%} "
            else:
                row += f"{'—':>13} "
        print(row)
    
    print("\n" + "=" * 70)


def create_figures(metrics, agents, variants, output_dir):
    """Generate matplotlib visualizations."""
    if not HAS_MPL:
        print("Skipping figure generation (matplotlib not installed)")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Color scheme
    colors = {
        'correct': '#16a34a',
        'nudged': '#dc2626',
        'other': '#d97706',
        'bar': '#2563eb',
        'bg': '#fafaf8',
    }
    
    # --- Figure 1: Manipulation Success Rate by Variant ---
    fig, ax = plt.subplots(figsize=(10, 6))
    manip_variants = [v for v in variants if v != 'control']
    rates = []
    cis_low = []
    cis_high = []
    
    for v in manip_variants:
        m = metrics['by_variant'].get(v, {})
        rate = m.get('nudge_rate', 0)
        ci = m.get('nudge_ci', (0, 0))
        rates.append(rate * 100)
        cis_low.append((rate - ci[0]) * 100)
        cis_high.append((ci[1] - rate) * 100)
    
    x = range(len(manip_variants))
    bars = ax.bar(x, rates, color=colors['bar'], alpha=0.85, width=0.6)
    ax.errorbar(x, rates, yerr=[cis_low, cis_high], fmt='none', capsize=5, color='#1e3a5f', capthick=1.5)
    
    # Add value labels
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{rate:.0f}%', ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Control baseline
    ctrl_nudge = metrics['by_variant'].get('control', {}).get('nudge_rate', 0) * 100
    ax.axhline(y=ctrl_nudge, color=colors['correct'], linestyle='--', alpha=0.7, label=f'Control baseline ({ctrl_nudge:.0f}%)')
    
    labels = [v.replace('-', '\n') for v in manip_variants]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel('Nudge Success Rate (%)', fontsize=12)
    ax.set_title('How Often Did Manipulation Steer Agents to the Worst Product?', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_ylim(0, 105)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'manipulation_rates.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved manipulation_rates.png")
    
    # --- Figure 2: Heatmap (Agent × Variant) ---
    fig, ax = plt.subplots(figsize=(10, 5))
    
    data_matrix = []
    for a in agents:
        row = []
        for v in variants:
            cell = metrics['by_agent_variant'].get(a, {}).get(v)
            row.append(cell['nudge_rate'] * 100 if cell else 0)
        data_matrix.append(row)
    
    data_arr = np.array(data_matrix)
    
    cmap = plt.cm.RdYlGn_r
    im = ax.imshow(data_arr, cmap=cmap, aspect='auto', vmin=0, vmax=100)
    
    ax.set_xticks(range(len(variants)))
    ax.set_xticklabels([v.replace('-', '\n') for v in variants], fontsize=10)
    ax.set_yticks(range(len(agents)))
    ax.set_yticklabels(agents, fontsize=11)
    
    # Add text annotations
    for i in range(len(agents)):
        for j in range(len(variants)):
            val = data_arr[i, j]
            color = 'white' if val > 50 else 'black'
            ax.text(j, i, f'{val:.0f}%', ha='center', va='center', color=color, fontweight='bold', fontsize=11)
    
    ax.set_title('Nudge Rate by Agent × Manipulation Type', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax, label='Nudge Rate (%)', shrink=0.8)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'heatmap.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved heatmap.png")
    
    # --- Figure 3: Agent Comparison ---
    fig, ax = plt.subplots(figsize=(8, 5))
    
    agent_nudge_rates = [metrics['by_agent'].get(a, {}).get('manipulation_nudge_rate', 0) * 100 for a in agents]
    agent_correct_rates = []
    for a in agents:
        ctrl = metrics['by_agent'].get(a, {}).get('control_correct_rate')
        agent_correct_rates.append((ctrl or 0) * 100)
    
    x = range(len(agents))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], agent_correct_rates, width, label='Control: Correct Rate', color=colors['correct'], alpha=0.8)
    bars2 = ax.bar([i + width/2 for i in x], agent_nudge_rates, width, label='Manipulation: Nudge Rate', color=colors['nudged'], alpha=0.8)
    
    for bar, rate in zip(bars1, agent_correct_rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{rate:.0f}%', ha='center', fontsize=10)
    for bar, rate in zip(bars2, agent_nudge_rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'{rate:.0f}%', ha='center', fontsize=10)
    
    ax.set_xticks(x)
    ax.set_xticklabels(agents, fontsize=11)
    ax.set_ylabel('Rate (%)', fontsize=12)
    ax.set_title('Agent Comparison: Correct Decisions vs. Manipulation Susceptibility', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_ylim(0, 110)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'agent_comparison.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved agent_comparison.png")


def export_json(metrics, output_dir):
    """Export metrics as JSON for blog embedding."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert tuples to lists for JSON serialization
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, tuple):
            return list(obj)
        elif isinstance(obj, list):
            return [make_serializable(i) for i in obj]
        return obj
    
    with open(os.path.join(output_dir, 'metrics.json'), 'w') as f:
        json.dump(make_serializable(metrics), f, indent=2)
    print(f"  ✓ Saved metrics.json")


def main():
    parser = argparse.ArgumentParser(description='Analyze agent nudge experiment results')
    parser.add_argument('--data', default='data/results.csv', help='Path to results CSV')
    parser.add_argument('--output', default='analysis/figures', help='Output directory for figures')
    args = parser.parse_args()
    
    if not os.path.exists(args.data):
        print(f"❌ Data file not found: {args.data}")
        print(f"   Create {args.data} with experiment results first.")
        print(f"   See METHODOLOGY.md for the CSV format.")
        return
    
    print("Loading data...")
    data = load_data(args.data)
    
    print("Computing metrics...")
    metrics, agents, variants = compute_metrics(data)
    
    print("\n")
    print_report(metrics, agents, variants)
    
    print("\nGenerating figures...")
    create_figures(metrics, agents, variants, args.output)
    
    print("\nExporting JSON...")
    export_json(metrics, args.output)
    
    print("\n✅ Analysis complete!")


if __name__ == '__main__':
    main()
