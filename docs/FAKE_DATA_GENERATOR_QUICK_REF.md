# 🎲 Fake Data Generator - Quick Reference Card

## 🚀 One-Line Commands

```bash
# Generate data
python utils/fake_data_generator.py

# Run examples
python examples/fake_data_generator_examples.py

# Run tests
python -m pytest tests/test_bookslot_with_fake_data.py -v
```

---

## 📝 Import Statements

```python
# Basic import
from utils.fake_data_generator import generate_bookslot_payload

# Full imports
from utils.fake_data_generator import (
    generate_bookslot_payload,              # Single payload
    generate_and_save_bookslot_data,        # Batch + save
    load_bookslot_data,                     # Load from file
    generate_bookslot_payload_with_options  # Custom options
)
```

---

## 🎯 Usage Cheat Sheet

### Single Payload
```python
data = generate_bookslot_payload()
# → {'first_name': 'John', 'email': 'john@mailinator.com', ...}
```

### Batch Generation
```python
data_list = generate_and_save_bookslot_data(count=10)
# → Saves to test_data/bookslot/bookslot_data.json/yaml
```

### Load from File
```python
data_list = load_bookslot_data("bookslot_data.json")
# → Returns list of payloads
```

### Custom Options
```python
data = generate_bookslot_payload_with_options(
    use_dynamic_zip=True,
    state="CA"
)
```

---

## 🧪 Pytest Fixtures

### Fixture 1: Single Payload
```python
def test_single(fake_bookslot_data):
    email = fake_bookslot_data['email']
```

### Fixture 2: Batch (5 records)
```python
def test_batch(fake_bookslot_batch):
    for data in fake_bookslot_batch:
        # Use data
```

### Fixture 3: From File
```python
def test_file(bookslot_data_file):
    data = bookslot_data_file[0]
```

---

## 📊 Data Structure

```python
{
    # Personal Info
    "first_name": str,           # Random
    "last_name": str,            # Random
    "email": str,                # Random@{mailinator|yopmail}.com
    "phone_number": "1234567890", # Static
    "zip": "20678",              # Static (configurable)
    "contact_method": "Text",    # Static (configurable)
    "verification_code": "123456", # Static
    "zip_distance": str,         # Random: 25/50/75/100
    "dob": "MM/DD/YYYY",         # Random (age 18-85)
    
    # Insurance Info
    "MemberName": str,           # Random
    "idNumber": "INS-XXXXX",     # Random 5-digit
    "GroupNumber": "GRP-XXXX",   # Random 4-digit
    "PayerName": str             # Random from list
}
```

---

## 🎨 Common Patterns

### Pattern 1: Inline in Test
```python
def test_something():
    data = generate_bookslot_payload()
    # Use immediately
```

### Pattern 2: With Fixture
```python
def test_something(fake_bookslot_data):
    # Data automatically provided
```

### Pattern 3: Parametrized
```python
@pytest.mark.parametrize("data", [
    generate_bookslot_payload() for _ in range(5)
])
def test_multi(data):
    # Each iteration gets different data
```

### Pattern 4: Pre-generated
```python
# Step 1: Generate once
generate_and_save_bookslot_data(count=100)

# Step 2: Use in tests
def test_with_data(bookslot_data_file):
    for data in bookslot_data_file:
        # Use pre-generated
```

---

## 🔧 Configuration Quick Edit

**File:** `utils/fake_data_generator.py`

```python
# Line ~35: Change phone
STATIC_PHONE = "9999999999"

# Line ~37: Change ZIP
STATIC_ZIP = "12345"

# Line ~40: Change contact methods
CONTACT_METHODS = ["Text", "Email", "Call"]

# Line ~31: Change payers
PAYER_LIST = [
    "Aetna Health",
    "Blue Cross Blue Shield",
    # Add more...
]

# Line ~38: Change email domains
ALLOWED_EMAIL_DOMAINS = ["mailinator.com", "yopmail.com"]
```

---

## 📍 File Locations

```
utils/fake_data_generator.py          → Main utility
examples/fake_data_generator_examples.py  → Usage examples
tests/test_bookslot_with_fake_data.py     → Test examples
docs/FAKE_DATA_GENERATOR_GUIDE.md         → Full documentation
docs/FAKE_DATA_GENERATOR_SUMMARY.md       → Implementation summary
conftest.py                                → Fixtures (updated)

test_data/bookslot/
├── bookslot_data.json                → Generated data
└── bookslot_data.yaml                → Generated data
```

---

## 🐛 Troubleshooting

### Issue: Import Error
```python
# Add to top of file
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Issue: File Not Found
```python
# Generate first
generate_and_save_bookslot_data()
# Then load
data = load_bookslot_data()
```

### Issue: Missing Faker
```bash
pip install Faker>=21.0.0
# or
pip install -r requirements.txt
```

---

## ✅ Validation Tests

```bash
# Run all validation tests
python -m pytest tests/test_bookslot_with_fake_data.py::TestBookslotDataValidation -v

# Tests verify:
✓ Email domains (mailinator/yopmail)
✓ Insurance payer from allowed list
✓ Static fields (phone/zip/verification)
✓ Insurance ID format (INS-XXXXX)
✓ Group number format (GRP-XXXX)
✓ DOB format (MM/DD/YYYY)
✓ ZIP distance (25/50/75/100)
```

---

## 🎁 Bonus Features

### Feature 1: Custom Filename
```python
generate_and_save_bookslot_data(
    count=10,
    filename_prefix="my_custom_data"
)
# → my_custom_data.json/yaml
```

### Feature 2: Dynamic ZIP
```python
data = generate_bookslot_payload_with_options(
    use_dynamic_zip=True,
    state="MD"
)
# → Random Maryland ZIP code
```

### Feature 3: All Contact Methods
```python
data = generate_bookslot_payload_with_options(
    use_all_contact_methods=True
)
# → Text/Email/Call (random)
```

---

## 📱 Copy-Paste Templates

### Template 1: Basic Test
```python
def test_bookslot(fake_bookslot_data, page):
    page.goto("https://app.com/bookslot")
    page.fill("#first_name", fake_bookslot_data["first_name"])
    page.fill("#email", fake_bookslot_data["email"])
    page.click("#submit")
    assert page.is_visible(".success")
```

### Template 2: Batch Test
```python
def test_multiple(fake_bookslot_batch):
    for data in fake_bookslot_batch:
        result = submit_bookslot(data)
        assert result.success
```

### Template 3: Custom Generation
```python
from utils.fake_data_generator import generate_and_save_bookslot_data

# In test setup or conftest
@pytest.fixture(scope="session", autouse=True)
def setup_test_data():
    generate_and_save_bookslot_data(count=100)
```

---

## 🎯 Best Practices

✅ Use fixtures for individual tests  
✅ Pre-generate for performance tests  
✅ Validate generated data in tests  
✅ Keep static fields consistent  
✅ Document custom configurations  
✅ Use meaningful filenames for batches  

---

**Quick Help:**  
📖 Full Guide: `docs/FAKE_DATA_GENERATOR_GUIDE.md`  
💡 Examples: `examples/fake_data_generator_examples.py`  
🧪 Tests: `tests/test_bookslot_with_fake_data.py`

---

**Status:** ✅ Ready to Use  
**Version:** 1.0.0
