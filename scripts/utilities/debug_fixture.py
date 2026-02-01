"""Debug script to test the fixture loading"""
from pathlib import Path
import yaml

def test_fixture_logic(env):
    """Simulate the exact fixture logic"""
    print(f"\n{'='*80}")
    print(f"TESTING FIXTURE WITH ENV: {env}")
    print(f"{'='*80}\n")
    
    # Load projects.yaml
    config_path = Path(__file__).parent / "config" / "projects.yaml"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            projects_data = yaml.safe_load(f)
            projects_config = projects_data.get('projects', {})
        print(f"✅ Loaded projects.yaml")
    else:
        projects_config = {}
        print(f"❌ projects.yaml not found")
    
    # Build result
    result = {}
    for project_name in ['bookslot', 'patientintake', 'callcenter']:
        if project_name in projects_config:
            project = projects_config[project_name]
            env_config = project.get('environments', {}).get(env, {})
            if env_config:
                result[project_name] = env_config
                print(f"  [{project_name}] {env} URL: {env_config.get('ui_url')}")
    
    # Check fallback
    if not result:
        print(f"\n⚠️  WARNING: No config found, using fallback!")
        print(f"  Fallback env: {env}")
        
        fallback_structure = {
            'bookslot': {
                'staging': {
                    'ui_url': 'https://bookslot-staging.centerforvein.com',
                    'api_url': 'https://api-bookslot-staging.centerforvein.com'
                },
                'production': {
                    'ui_url': 'https://bookslots.centerforvein.com',
                    'api_url': 'https://api-bookslot.centerforvein.com'
                }
            }.get(env, {})
        }
        
        print(f"\n  Fallback returns: {fallback_structure}")
        result = fallback_structure
    
    print(f"\n{'='*80}")
    print(f"FINAL RESULT:")
    print(f"{'='*80}")
    print(f"  bookslot URL: {result.get('bookslot', {}).get('ui_url', 'NOT FOUND')}")
    
    return result

# Test with production
print("\n\nTEST 1: Production Environment")
result_prod = test_fixture_logic('production')
print(f"\nResult structure: {result_prod}")

print("\n\nTEST 2: Staging Environment")
result_staging = test_fixture_logic('staging')
print(f"\nResult structure: {result_staging}")
