#!/home/sanjayu/shelf/projects/ProbeWeave/.venv/bin/python3
import json
import os
import sys
import glob

def analyze_artifacts(output_dir="output"):
    print("--- ProbeWeave Artifact Analysis ---")
    files = glob.glob(f"{output_dir}/*.json")
    if not files:
        print("No artifacts found to analyze.")
        return

    summary = {
        "total_hosts": len(files),
        "failed_probes": 0,
        "os_distribution": {},
        "lldp_neighbors": 0
    }

    for file_path in files:
        with open(file_path, 'r') as f:
            data = json.load(f)
            results = data.get('results', {})
            
            # Analyze OS
            os_info = results.get('software', {}).get('os', {})
            distro = os_info.get('os_release', {}).get('PRETTY_NAME', 'Unknown')
            summary['os_distribution'][distro] = summary['os_distribution'].get(distro, 0) + 1
            
            # Analyze LLDP
            lldp = results.get('hardware', {}).get('lldp', {})
            if lldp.get('present'):
                summary['lldp_neighbors'] += len(lldp.get('interfaces', {}))
            else:
                summary['failed_probes'] += 1

    print(json.dumps(summary, indent=2))
    
    # Generate a simple Markdown report for Jenkins
    with open("probeweave_report.md", "w") as r:
        r.write("# ProbeWeave Deployment Report

")
        r.write(f"**Total Hosts Crawled:** {summary['total_hosts']}
")
        r.write(f"**LLDP Connections Found:** {summary['lldp_neighbors']}

")
        r.write("### OS Distribution
")
        for distro, count in summary['os_distribution'].items():
            r.write(f"- {distro}: {count}
")
            
    print("Markdown report generated: probeweave_report.md")

if __name__ == "__main__":
    analyze_artifacts()
