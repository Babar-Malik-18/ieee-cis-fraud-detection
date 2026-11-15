import urllib.request
import json

url = 'https://api.github.com/repos/Babar-Malik-18/ieee-cis-fraud-detection/actions/runs'
req = urllib.request.Request(url, headers={'User-Agent': 'Python-MLOps-Agent'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        print(f"Total workflow runs: {data.get('total_count', 0)}")
        for run in data.get('workflow_runs', [])[:5]:
            name = run.get('name')
            status = run.get('status')
            conclusion = run.get('conclusion')
            html_url = run.get('html_url')
            event = run.get('event')
            print(f"- {name} [{event}]: status={status}, conclusion={conclusion}")
            print(f"  URL: {html_url}")
except Exception as e:
    print("API Query result:", e)
