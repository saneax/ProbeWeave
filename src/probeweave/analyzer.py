import glob
import json


def analyze(output_dir="output"):
    files = glob.glob(f"{output_dir}/*.json")
    if not files:
        print("No artifacts found.")
        return

    with open("probeweave_report.md", "w") as r:
        r.write("# ProbeWeave Audit Report\n\n")
        for f_path in files:
            with open(f_path, 'r') as f:
                data = json.load(f)
                host = data.get('host')
                os_name = (data.get('results', {})
                           .get('software', {})
                           .get('os', {})
                           .get('hostname', 'Unknown'))
                r.write(f"## {host}\n")
                r.write(f"- OS Hostname: {os_name}\n\n")

if __name__ == "__main__":
    analyze()
