import urllib.request
import json

run_id = "43755223949"
url = f"https://api.github.com/repos/Babar-Malik-18/ieee-cis-fraud-detection/actions/runs/{run_id}/jobs"
req = urllib.request.Request(url, headers={'User-Agent': 'Python-MLOps-Agent'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        for job in data.get('jobs', []):
            print(f"Job: {job.get('name')}, Status: {job.get('status')}, Conclusion: {job.get('conclusion')}")
            for step in job.get('steps', []):
                if step.get('conclusion') == 'failure':
                    print(f"  FAILED STEP: {step.get('name')}")
except Exception as e:
    print("Error:", e)
