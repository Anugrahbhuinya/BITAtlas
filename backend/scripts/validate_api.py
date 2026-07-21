import urllib.request
import urllib.error
import json
import sys

BASE_URL = "http://localhost:8001"

ENDPOINTS = [
    # (Path, Method, Payload, Expect_CORS)
    ("/health", "GET", None, True),
    ("/system/status", "GET", None, True),
    ("/config", "GET", None, True),
    ("/openapi.json", "GET", None, True),
    ("/docs", "GET", None, False),
    ("/api/auth/login", "OPTIONS", None, True),
    ("/api/auth/login", "POST", {"email": "test@example.com", "password": "wrongpassword"}, True),
    ("/api/admin/login", "OPTIONS", None, True),
    ("/api/admin/login", "POST", {"username": "admin", "password": "wrongpassword"}, True),
    ("/chat", "OPTIONS", None, True),
    ("/api/admin/documents", "OPTIONS", None, True),
    ("/api/admin/websites", "OPTIONS", None, True),
]

def run_test(path, method, payload=None, expect_cors=True):
    url = f"{BASE_URL}{path}"
    headers = {
        "Origin": "http://localhost:5180"
    }
    
    if method == "OPTIONS":
        headers["Access-Control-Request-Method"] = "POST"
        headers["Access-Control-Request-Headers"] = "Content-Type"
        
    data = None
    if payload:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    status_code = None
    resp_headers = {}
    error_msg = None
    
    try:
        with urllib.request.urlopen(req, timeout=3.0) as response:
            status_code = response.status
            resp_headers = dict(response.info())
    except urllib.error.HTTPError as e:
        status_code = e.code
        resp_headers = dict(e.headers)
        try:
            error_msg = e.read().decode("utf-8")
        except Exception:
            pass
    except Exception as e:
        status_code = "ERR"
        error_msg = str(e)
        
    # Check CORS Headers
    cors_ok = False
    allow_origin = resp_headers.get("access-control-allow-origin") or resp_headers.get("Access-Control-Allow-Origin")
    allow_credentials = resp_headers.get("access-control-allow-credentials") or resp_headers.get("Access-Control-Allow-Credentials")
    
    if allow_origin == "http://localhost:5180" and allow_credentials == "true":
        cors_ok = True
    elif not expect_cors:
        cors_ok = True # not expected
        
    return {
        "url": url,
        "method": method,
        "status_code": status_code,
        "cors_ok": cors_ok,
        "allow_origin": allow_origin,
        "error_msg": error_msg
    }

def main():
    print("\n" + "="*80)
    print("                 BITATLAS - API VALIDATION SUITE")
    print("="*80)
    print(f"Targeting: {BASE_URL}\n")
    
    success = True
    results = []
    
    for path, method, payload, expect_cors in ENDPOINTS:
        res = run_test(path, method, payload, expect_cors)
        results.append(res)
        
        status_str = f"HTTP {res['status_code']}"
        cors_str = "CORS PASS" if res['cors_ok'] else "CORS FAIL"
        
        indicator = "[PASS]"
        if res['status_code'] == "ERR" or (expect_cors and not res['cors_ok']):
            indicator = "[FAIL]"
            success = False
            
        print(f"  {indicator} {method:<8} {path:<30} {status_str:<10} {cors_str:<12} Origin: {res['allow_origin']}")
        if res['error_msg'] and "wrongpassword" not in res['error_msg'] and "Incorrect" not in res['error_msg']:
            print(f"      Details: {res['error_msg'][:150]}")
            
    print("\n" + "="*80)
    if success:
        print(" SUCCESS: All API validation assertions passed!")
        print("="*80 + "\n")
        sys.exit(0)
    else:
        print(" FAILURE: Some API validation checks failed.")
        print("="*80 + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
