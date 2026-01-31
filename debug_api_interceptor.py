import sys
from unittest.mock import Mock
from framework.api.api_interceptor import APIInterceptor

ui = Mock()
ui.__class__.__name__ = 'PlaywrightEngine'
i = APIInterceptor(ui)

i.captured_requests = [
    {'method': 'GET', 'url': 'https://api.example.com/users'},
    {'method': 'GET', 'url': 'https://api.example.com/orders'},
    {'method': 'GET', 'url': 'https://example.com/page.html'}
]

print(f"Total requests: {len(i.captured_requests)}")
print("Testing filter:")

pattern = '/api/'
print(f"Pattern: '{pattern}'")

for req in i.captured_requests:
    url = req['url']
    contains = pattern in url
    print(f"URL: {url}, Contains '{pattern}': {contains}")

result = i.get_captured_requests(lambda r: pattern in r['url'])
print(f"\nFiltered result: {len(result)}")
print(f"Result: {result}")

result2 = i.get_requests_by_url_pattern('/api/')
print(f"\nget_requests_by_url_pattern result: {len(result2)}")
print(f"Result: {result2}")
