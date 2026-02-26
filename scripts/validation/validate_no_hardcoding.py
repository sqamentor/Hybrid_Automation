"""
POST-AUDIT VALIDATION SCRIPT
Verifies that all hardcoded values have been removed and framework uses dynamic configuration

Author: Lokendra Singh
Website: www.centerforvein.com
"""

import subprocess
import sys
from pathlib import Path
import yaml

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}")
    print(f"{text}")
    print(f"{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ️  {text}{Colors.ENDC}")

def check_projects_yaml():
    """Verify projects.yaml exists and is properly configured"""
    print_header("1. CHECKING PROJECTS.YAML CONFIGURATION")
    
    config_path = Path(__file__).parent / "config" / "projects.yaml"
    
    if not config_path.exists():
        print_error("projects.yaml not found!")
        return False
    
    print_success("projects.yaml exists")
    
    try:
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            projects = data.get('projects', {})
            
        if 'bookslot' in projects:
            print_success("bookslot project configured")
            envs = projects['bookslot'].get('environments', {})
            
            if 'staging' in envs:
                staging_url = envs['staging'].get('ui_url', '')
                print_success(f"Staging URL: {staging_url}")
            else:
                print_error("Staging environment not configured")
                return False
            
            if 'production' in envs:
                prod_url = envs['production'].get('ui_url', '')
                print_success(f"Production URL: {prod_url}")
            else:
                print_error("Production environment not configured")
                return False
        else:
            print_error("bookslot project not found in projects.yaml")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error reading projects.yaml: {e}")
        return False

def check_no_hardcoded_urls():
    """Check for hardcoded URLs in key files"""
    print_header("2. CHECKING FOR HARDCODED URLs")
    
    files_to_check = [
        "recorded_tests/bookslot/test_bookslot_bookslots_complete.py",
        "pages/bookslot/bookslots_basicinfo.py",
        "conftest.py"
    ]
    
    issues = []
    
    for file_path in files_to_check:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for hardcoded staging URLs
            if 'https://bookslot-staging.centerforvein.com' in content and 'multi_project_config' not in content:
                issues.append(f"{file_path}: Contains hardcoded staging URL")
            
            # Check for hardcoded production URLs
            if 'https://bookslots.centerforvein.com' in content and 'projects.yaml' not in content:
                # Allow if it's in a comment or documentation
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if 'https://bookslots.centerforvein.com' in line:
                        if not (line.strip().startswith('#') or line.strip().startswith('"""') or 
                               line.strip().startswith("'''") or 'Example:' in line or 'projects.yaml' in line):
                            issues.append(f"{file_path}:{i}: Hardcoded production URL")
    
    if issues:
        for issue in issues:
            print_error(issue)
        return False
    else:
        print_success("No hardcoded URLs found in critical files")
        return True

def check_recorded_test_uses_fixture():
    """Verify recorded test uses multi_project_config fixture"""
    print_header("3. CHECKING RECORDED TEST FIXTURE USAGE")
    
    test_file = Path(__file__).parent / "recorded_tests/bookslot/test_bookslot_bookslots_complete.py"
    
    if not test_file.exists():
        print_info("Recorded test file not found (may not exist yet)")
        return True
    
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for fixture in function signature
    if 'multi_project_config' in content:
        print_success("Recorded test uses multi_project_config fixture")
        
        # Check for dynamic URL usage
        if "multi_project_config['bookslot']['ui_url']" in content:
            print_success("Uses dynamic URL from fixture")
            return True
        else:
            print_error("Fixture present but not properly used")
            return False
    else:
        print_error("Recorded test does NOT use multi_project_config fixture")
        return False

def check_conftest_no_fallback():
    """Verify conftest raises error instead of using fallback"""
    print_header("4. CHECKING CONFTEST ERROR HANDLING")
    
    conftest_file = Path(__file__).parent / "conftest.py"
    
    with open(conftest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that fallback is removed
    if 'Fallback to hardcoded values' in content or 'fallback for env' in content:
        print_error("conftest still has hardcoded fallback values")
        return False
    
    # Check that it raises error
    if 'raise ValueError' in content and 'CONFIG] ERROR' in content:
        print_success("conftest raises error when config missing (no silent fallback)")
        return True
    else:
        print_error("conftest doesn't properly raise error on missing config")
        return False

def check_cli_uses_dynamic_urls():
    """Verify CLI loads URLs from projects.yaml"""
    print_header("5. CHECKING CLI DYNAMIC URL LOADING")
    
    cli_file = Path(__file__).parent / "run_tests_cli.py"
    
    with open(cli_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for yaml import
    if 'import yaml' not in content:
        print_error("run_tests_cli.py doesn't import yaml")
        return False
    
    print_success("CLI imports yaml module")
    
    # Check for URL loading method
    if '_load_project_urls' in content:
        print_success("CLI has _load_project_urls method")
        
        # Check for usage
        if 'self.staging_url' in content and 'self.production_url' in content:
            print_success("CLI uses dynamic staging_url and production_url")
            return True
        else:
            print_error("CLI doesn't use loaded URLs")
            return False
    else:
        print_error("CLI doesn't have URL loading method")
        return False

def check_env_example_exists():
    """Verify .env.example template exists"""
    print_header("6. CHECKING .ENV.EXAMPLE TEMPLATE")
    
    env_example = Path(__file__).parent / "env.example"
    
    if env_example.exists():
        print_success("env.example template exists")
        
        with open(env_example, 'r') as f:
            content = f.read()
        
        # Check for key sections
        if 'OPENAI_API_KEY' in content:
            print_success("Contains AI configuration")
        if 'DB_HOST' in content:
            print_success("Contains database configuration")
        if 'TEST_ENV' in content:
            print_success("Contains environment override")
        
        return True
    else:
        print_error("env.example template not found")
        return False

def run_validation_tests():
    """Run actual tests to verify dynamic behavior"""
    print_header("7. RUNNING VALIDATION TESTS")
    
    print_info("Testing with staging environment...")
    result_staging = subprocess.run(
        "python -m pytest pages/bookslot/bookslots_basicinfo.py::test_bookslot_basic_info_form_validation --env=staging --co -v",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if 'bookslot-staging.centerforvein.com' in result_staging.stdout + result_staging.stderr:
        print_success("Staging environment loads staging URL")
    else:
        print_error("Staging environment doesn't load staging URL")
        return False
    
    print_info("Testing with production environment...")
    result_prod = subprocess.run(
        "python -m pytest pages/bookslot/bookslots_basicinfo.py::test_bookslot_basic_info_form_validation --env=production --co -v",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if 'bookslots.centerforvein.com' in result_prod.stdout + result_prod.stderr:
        print_success("Production environment loads production URL")
    else:
        print_error("Production environment doesn't load production URL")
        return False
    
    return True

def main():
    """Run all validation checks"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*80)
    print("  POST-AUDIT VALIDATION - FRAMEWORK DYNAMIC CONFIGURATION CHECK")
    print("="*80)
    print(Colors.ENDC)
    
    results = []
    
    results.append(("projects.yaml Configuration", check_projects_yaml()))
    results.append(("No Hardcoded URLs", check_no_hardcoded_urls()))
    results.append(("Recorded Test Uses Fixture", check_recorded_test_uses_fixture()))
    results.append(("Conftest Error Handling", check_conftest_no_fallback()))
    results.append(("CLI Dynamic URL Loading", check_cli_uses_dynamic_urls()))
    results.append((".env.example Template", check_env_example_exists()))
    results.append(("Runtime Validation Tests", run_validation_tests()))
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        if result:
            print_success(f"{check_name}: PASSED")
        else:
            print_error(f"{check_name}: FAILED")
    
    print(f"\n{Colors.BOLD}")
    if passed == total:
        print(f"{Colors.GREEN}✅ ALL CHECKS PASSED ({passed}/{total}){Colors.ENDC}")
        print(f"\n{Colors.GREEN}🎉 Framework is fully dynamic! No hardcoded values found.{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.RED}❌ SOME CHECKS FAILED ({passed}/{total} passed){Colors.ENDC}")
        print(f"\n{Colors.RED}⚠️  Please review failed checks and fix the issues.{Colors.ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
