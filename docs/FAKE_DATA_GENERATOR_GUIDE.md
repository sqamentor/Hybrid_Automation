# Fake Data Generator for Bookslot Testing

## Overview
This utility generates realistic fake data for bookslot testing using the Faker library. It provides flexible data generation with support for JSON and YAML output formats.

## 📁 Files Created

1. **`utils/fake_data_generator.py`** - Main utility module
2. **`examples/fake_data_generator_examples.py`** - Usage examples
3. **`tests/test_bookslot_with_fake_data.py`** - Example test implementation
4. **`conftest.py`** - Updated with pytest fixtures

## 🚀 Quick Start

### 1. Generate Data from Command Line

```bash
# Generate 5 default bookslot records
python utils/fake_data_generator.py
```

Output files will be created in `test_data/bookslot/`:
- `bookslot_data.json`
- `bookslot_data.yaml`

### 2. Use in Python Code

```python
from utils.fake_data_generator import generate_bookslot_payload

# Generate single payload
data = generate_bookslot_payload()
print(data['email'])  # random_user@mailinator.com
```

### 3. Use in Pytest Tests

```python
def test_bookslot(fake_bookslot_data):
    """Test using fixture - auto-generates fresh data"""
    first_name = fake_bookslot_data['first_name']
    email = fake_bookslot_data['email']
    # ... use in your test
```

## 📋 Available Functions

### Core Functions

#### `generate_bookslot_payload()`
Generates a single bookslot payload with all required fields.

```python
from utils.fake_data_generator import generate_bookslot_payload

data = generate_bookslot_payload()
# Returns:
# {
#     "first_name": "John",
#     "last_name": "Doe",
#     "email": "johndoe@mailinator.com",
#     "phone_number": "1234567890",
#     "zip": "20678",
#     "contact_method": "Text",
#     "verification_code": "123456",
#     "zip_distance": "50",
#     "dob": "05/15/1985",
#     "MemberName": "John Doe",
#     "idNumber": "INS-12345",
#     "GroupNumber": "GRP-5678",
#     "PayerName": "Aetna Health"
# }
```

#### `generate_and_save_bookslot_data(count=5, filename_prefix="bookslot_data")`
Generates multiple payloads and saves to JSON/YAML files.

```python
from utils.fake_data_generator import generate_and_save_bookslot_data

# Generate 10 records
data_list = generate_and_save_bookslot_data(count=10)

# Generate with custom filename
data_list = generate_and_save_bookslot_data(
    count=20, 
    filename_prefix="bookslot_qa_data"
)
```

#### `load_bookslot_data(filename="bookslot_data.json")`
Loads previously generated data from file.

```python
from utils.fake_data_generator import load_bookslot_data

# Load default file
data_list = load_bookslot_data()

# Load custom file
data_list = load_bookslot_data("bookslot_custom.json")
```

### Advanced Functions

#### `generate_bookslot_payload_with_options(**kwargs)`
Generates payload with custom configuration options.

```python
from utils.fake_data_generator import generate_bookslot_payload_with_options

# Generate with dynamic ZIP code
data = generate_bookslot_payload_with_options(
    use_dynamic_zip=True,
    state="CA"
)

# Generate with all contact methods enabled
data = generate_bookslot_payload_with_options(
    use_all_contact_methods=True
)
```

## 🧪 Pytest Fixtures

Three fixtures are available in `conftest.py`:

### 1. `fake_bookslot_data`
Function-scoped fixture that generates fresh data for each test.

```python
def test_single_bookslot(fake_bookslot_data):
    email = fake_bookslot_data['email']
    assert '@' in email
```

### 2. `fake_bookslot_batch`
Function-scoped fixture that generates 5 records per test.

```python
def test_multiple_bookslots(fake_bookslot_batch):
    for data in fake_bookslot_batch:
        # Process each record
        submit_bookslot(data)
```

### 3. `bookslot_data_file`
Session-scoped fixture that loads data from file (reused across tests).

```python
def test_with_file_data(bookslot_data_file):
    first_record = bookslot_data_file[0]
    # Use pre-generated data
```

## 📊 Generated Data Structure

### Personal Information
- **first_name**: Random first name (e.g., "John")
- **last_name**: Random last name (e.g., "Doe")
- **email**: Random email with allowed domains (mailinator.com, yopmail.com)
- **phone_number**: Static "1234567890"
- **zip**: Static "20678" (configurable)
- **contact_method**: "Text" (default)
- **verification_code**: Static "123456"
- **zip_distance**: Random from ["25", "50", "75", "100"]
- **dob**: Random DOB between 18-85 years old (format: MM/DD/YYYY)

### Insurance Information
- **MemberName**: Random full name
- **idNumber**: Format "INS-XXXXX" (5-digit random)
- **GroupNumber**: Format "GRP-XXXX" (4-digit random)
- **PayerName**: Random from allowed payers:
  - Aetna Health
  - Blue Cross Blue Shield
  - UnitedHealthcare
  - Cigna
  - Humana

## 💡 Usage Examples

### Example 1: Basic Test

```python
import pytest

def test_bookslot_submission(fake_bookslot_data, page):
    # Navigate to page
    page.goto("https://app.com/bookslot")
    
    # Fill form with fake data
    page.fill("#first_name", fake_bookslot_data["first_name"])
    page.fill("#last_name", fake_bookslot_data["last_name"])
    page.fill("#email", fake_bookslot_data["email"])
    
    # Submit
    page.click("#submit")
    
    # Verify
    assert page.is_visible(".success")
```

### Example 2: Data-Driven Testing

```python
@pytest.mark.parametrize("test_data", [
    generate_bookslot_payload() for _ in range(5)
])
def test_multiple_scenarios(test_data, page):
    # Each iteration uses different fake data
    submit_bookslot(test_data)
    verify_submission()
```

### Example 3: Batch Generation

```python
def test_bulk_bookslots(fake_bookslot_batch):
    results = []
    
    for idx, data in enumerate(fake_bookslot_batch):
        result = submit_bookslot(data)
        results.append(result)
        print(f"Processed {idx+1}: {data['email']}")
    
    assert all(results), "Some bookslots failed"
```

### Example 4: Custom Data Generation

```python
from utils.fake_data_generator import generate_and_save_bookslot_data

# Generate test data for specific scenario
generate_and_save_bookslot_data(
    count=50,
    filename_prefix="bookslot_stress_test"
)

# Load and use in test
data = load_bookslot_data("bookslot_stress_test.json")
```

## 🎯 Best Practices

1. **Use Fixtures for Individual Tests**
   ```python
   def test_something(fake_bookslot_data):
       # Automatically gets fresh data
   ```

2. **Generate Batch Data for Performance Tests**
   ```python
   # Pre-generate data
   python utils/fake_data_generator.py
   
   # Load in tests
   def test_perf(bookslot_data_file):
       # Reuses pre-generated data
   ```

3. **Validate Generated Data**
   ```python
   def test_data_validation(fake_bookslot_data):
       assert fake_bookslot_data["phone_number"] == "1234567890"
       assert "@mailinator.com" in fake_bookslot_data["email"] or \
              "@yopmail.com" in fake_bookslot_data["email"]
   ```

4. **Custom Scenarios**
   ```python
   # For specific test scenarios
   from utils.fake_data_generator import generate_bookslot_payload_with_options
   
   def test_dynamic_location():
       data = generate_bookslot_payload_with_options(
           use_dynamic_zip=True,
           state="TX"
       )
   ```

## 🔧 Configuration

### Modify Default Values

Edit `utils/fake_data_generator.py`:

```python
# Change static phone
STATIC_PHONE = "9999999999"

# Change default ZIP
STATIC_ZIP = "12345"

# Add more payers
PAYER_LIST = [
    "Aetna Health",
    "Blue Cross Blue Shield",
    # ... add more
]

# Change email domains
ALLOWED_EMAIL_DOMAINS = ["temp-mail.com", "guerrillamail.com"]
```

## 📂 Output Files

Generated files are saved to `test_data/bookslot/`:

```
test_data/bookslot/
├── bookslot_data.json          # Default JSON output
├── bookslot_data.yaml          # Default YAML output
├── bookslot_custom.json        # Custom generated files
└── bookslot_custom.yaml
```

## 🧩 Integration with Existing Tests

### Option 1: Direct Import

```python
from utils.fake_data_generator import generate_bookslot_payload

def test_existing_flow():
    data = generate_bookslot_payload()
    # Use with existing test logic
```

### Option 2: Use Fixtures

```python
# Just add fixture parameter
def test_existing_flow(fake_bookslot_data):
    # fake_bookslot_data is automatically available
    # No changes to test logic needed
```

### Option 3: Batch Processing

```python
from utils.fake_data_generator import load_bookslot_data

def test_bulk_processing():
    data_list = load_bookslot_data()
    for data in data_list:
        process_bookslot(data)
```

## ✅ Running Tests

```bash
# Run example tests
pytest tests/test_bookslot_with_fake_data.py -v

# Run with markers
pytest tests/test_bookslot_with_fake_data.py -v -m bookslot

# Run specific test
pytest tests/test_bookslot_with_fake_data.py::TestBookslotWithFakeData::test_single_bookslot_with_fake_data -v

# Generate HTML report
pytest tests/test_bookslot_with_fake_data.py --html=reports/fake_data_tests.html
```

## 📚 Additional Resources

- **Examples**: See `examples/fake_data_generator_examples.py`
- **Test Suite**: See `tests/test_bookslot_with_fake_data.py`
- **Faker Documentation**: https://faker.readthedocs.io/

## 🐛 Troubleshooting

### Issue: Faker not installed
```bash
pip install Faker>=21.0.0
# or
pip install -r requirements.txt
```

### Issue: File not found when loading data
```python
# Generate data first
from utils.fake_data_generator import generate_and_save_bookslot_data
generate_and_save_bookslot_data(count=5)

# Then load
data = load_bookslot_data()
```

### Issue: Custom output directory
```python
# Modify OUTPUT_DIR in fake_data_generator.py
OUTPUT_DIR = PROJECT_ROOT / "custom" / "path"
```

## 🎉 Summary

The fake data generator is now fully integrated into your bookslot testing framework:

✅ Utility module created in `utils/fake_data_generator.py`  
✅ Pytest fixtures added to `conftest.py`  
✅ Example tests created in `tests/test_bookslot_with_fake_data.py`  
✅ Usage examples provided in `examples/fake_data_generator_examples.py`  
✅ Supports JSON and YAML output formats  
✅ Flexible and customizable  
✅ Easy integration with existing tests  

Start using it immediately in your tests!
