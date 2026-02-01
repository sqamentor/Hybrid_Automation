"""Quick test to verify projects.yaml works."""
import yaml
from pathlib import Path

p = Path('config/projects.yaml')
if p.exists():
    print('✅ projects.yaml exists')
    data = yaml.safe_load(open(p))
    staging_url = data['projects']['bookslot']['environments']['staging']['ui_url']
    production_url = data['projects']['bookslot']['environments']['production']['ui_url']
    print(f'Staging: {staging_url}')
    print(f'Production: {production_url}')
else:
    print('❌ projects.yaml NOT FOUND')
