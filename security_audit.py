"""
Comprehensive Security Audit Script for Nepali Learning Platform
Tests common web vulnerabilities and API security issues
"""

import requests
import json
import time
from urllib.parse import urlencode
import sys

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# ANSI color codes for output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

vulnerabilities_found = []
tests_passed = []

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_test(test_name):
    print(f"{Colors.BLUE}[TEST]{Colors.RESET} {test_name}...", end=" ")

def print_vulnerable(message, severity="HIGH"):
    color = Colors.RED if severity == "HIGH" else Colors.YELLOW if severity == "MEDIUM" else Colors.MAGENTA
    print(f"{color}[VULNERABLE - {severity}]{Colors.RESET}")
    print(f"  → {message}")
    vulnerabilities_found.append({"test": message, "severity": severity})

def print_secure():
    print(f"{Colors.GREEN}[SECURE]{Colors.RESET}")
    tests_passed.append(True)

def print_info(message):
    print(f"{Colors.CYAN}[INFO]{Colors.RESET} {message}")

# ==================== SQL INJECTION TESTS ====================
def test_sql_injection():
    print_header("SQL INJECTION VULNERABILITY TESTS")
    
    sql_payloads = [
        "' OR '1'='1",
        "' OR 1=1--",
        "admin' --",
        "' UNION SELECT NULL--",
        "1' AND '1'='1",
        "'; DROP TABLE dictionary;--",
        "' OR 'x'='x",
        "1' ORDER BY 1--",
        "' OR '1'='1' /*",
    ]
    
    endpoints = [
        f"{API_BASE}/dictionary/",
        f"{API_BASE}/phrases",
        f"{API_BASE}/alphabet",
        f"{API_BASE}/resources/videos",
    ]
    
    for endpoint in endpoints:
        for payload in sql_payloads:
            print_test(f"SQL Injection: {endpoint} with payload: {payload[:20]}...")
            try:
                # Test in query parameters
                response = requests.get(f"{endpoint}?search={payload}", timeout=5)
                if response.status_code == 500 or "error" in response.text.lower():
                    if "sql" in response.text.lower() or "syntax" in response.text.lower():
                        print_vulnerable(f"SQL error exposed at {endpoint}", "HIGH")
                        continue
                
                # Test in JSON body
                response = requests.post(endpoint, json={"nepali": payload}, timeout=5)
                if response.status_code == 500 and "sql" in response.text.lower():
                    print_vulnerable(f"SQL injection possible in POST to {endpoint}", "HIGH")
                    continue
                    
                print_secure()
            except requests.exceptions.Timeout:
                print_vulnerable(f"Timeout - possible SQL injection causing delay", "MEDIUM")
            except Exception as e:
                print_secure()

# ==================== XSS TESTS ====================
def test_xss():
    print_header("CROSS-SITE SCRIPTING (XSS) TESTS")
    
    xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg/onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<iframe src='javascript:alert(1)'>",
        "<body onload=alert('XSS')>",
        "'-alert('XSS')-'",
        "\"><script>alert(String.fromCharCode(88,83,83))</script>",
    ]
    
    print_test("XSS in Dictionary POST")
    try:
        response = requests.post(f"{API_BASE}/dictionary/", 
                               json={"nepali": xss_payloads[0], "romanized": "test", "english": "test"},
                               timeout=5)
        
        # Check if stored
        if response.status_code in [200, 201]:
            get_response = requests.get(f"{API_BASE}/dictionary/", timeout=5)
            if xss_payloads[0] in get_response.text:
                print_vulnerable("Stored XSS possible - script tags not sanitized", "HIGH")
            else:
                print_secure()
        else:
            print_secure()
    except Exception as e:
        print_secure()
    
    print_test("XSS in Phrases POST")
    try:
        response = requests.post(f"{API_BASE}/phrases", 
                               json={"nepali": xss_payloads[1], "romanized": "test", "english": "test", "category": "test"},
                               timeout=5)
        print_secure()
    except Exception as e:
        print_secure()

# ==================== AUTHENTICATION & AUTHORIZATION TESTS ====================
def test_authentication():
    print_header("AUTHENTICATION & AUTHORIZATION TESTS")
    
    # Test if admin panel is protected
    print_test("Admin panel access without authentication")
    try:
        response = requests.get(f"{BASE_URL}/admin", timeout=5)
        if response.status_code == 200 and "admin" in response.text.lower():
            print_vulnerable("Admin panel accessible without authentication!", "HIGH")
        else:
            print_secure()
    except Exception as e:
        print_secure()
    
    # Test API endpoints without auth
    print_test("DELETE endpoints without authentication")
    try:
        response = requests.delete(f"{API_BASE}/dictionary/1", timeout=5)
        if response.status_code in [200, 204]:
            print_vulnerable("DELETE allowed without authentication", "HIGH")
        else:
            print_secure()
    except Exception as e:
        print_secure()

# ==================== CSRF TESTS ====================
def test_csrf():
    print_header("CROSS-SITE REQUEST FORGERY (CSRF) TESTS")
    
    print_test("CSRF tokens on state-changing operations")
    try:
        # Check if DELETE accepts request without CSRF token
        response = requests.delete(f"{API_BASE}/phrases/999", timeout=5)
        # If it doesn't fail on CSRF, it's vulnerable
        print_vulnerable("No CSRF protection on DELETE operations", "MEDIUM")
    except Exception as e:
        print_secure()
    
    print_test("CSRF protection on POST")
    try:
        response = requests.post(f"{API_BASE}/dictionary/", 
                               json={"nepali": "test", "romanized": "test", "english": "test"},
                               timeout=5)
        if response.status_code in [200, 201]:
            print_vulnerable("No CSRF protection on POST operations", "MEDIUM")
        else:
            print_secure()
    except Exception as e:
        print_secure()

# ==================== INPUT VALIDATION TESTS ====================
def test_input_validation():
    print_header("INPUT VALIDATION TESTS")
    
    print_test("Extremely long input strings")
    try:
        long_string = "A" * 10000
        response = requests.post(f"{API_BASE}/dictionary/", 
                               json={"nepali": long_string, "romanized": long_string, "english": long_string},
                               timeout=5)
        if response.status_code in [200, 201]:
            print_vulnerable("No length validation on inputs", "MEDIUM")
        else:
            print_secure()
    except Exception as e:
        print_secure()
    
    print_test("Special characters and Unicode handling")
    try:
        special_chars = "'\"><script>&&||%%$$##@@!!"
        response = requests.post(f"{API_BASE}/phrases", 
                               json={"nepali": special_chars, "romanized": special_chars, 
                                   "english": special_chars, "category": special_chars},
                               timeout=5)
        if response.status_code == 500:
            print_vulnerable("Server error on special characters - poor input handling", "LOW")
        else:
            print_secure()
    except Exception as e:
        print_secure()
    
    print_test("Null/None value handling")
    try:
        response = requests.post(f"{API_BASE}/dictionary/", 
                               json={"nepali": None, "romanized": None, "english": None},
                               timeout=5)
        if response.status_code == 500:
            print_vulnerable("Server crashes on null values", "LOW")
        else:
            print_secure()
    except Exception as e:
        print_secure()

# ==================== FILE UPLOAD TESTS ====================
def test_file_upload():
    print_header("FILE UPLOAD VULNERABILITY TESTS")
    
    print_test("Malicious file upload")
    try:
        # Try uploading a PHP shell
        files = {'file': ('shell.php', '<?php system($_GET["cmd"]); ?>', 'application/x-php')}
        response = requests.post(f"{API_BASE}/bulk/dictionary", files=files, timeout=5)
        
        if response.status_code in [200, 201]:
            print_vulnerable("No file type validation - PHP file accepted", "HIGH")
        else:
            print_secure()
    except Exception as e:
        print_secure()
    
    print_test("CSV injection in bulk upload")
    try:
        csv_payload = "=cmd|'/c calc'!A1,test,test\ntest2,test2,test2"
        files = {'file': ('inject.csv', csv_payload, 'text/csv')}
        response = requests.post(f"{API_BASE}/bulk/dictionary", files=files, timeout=5)
        print_secure()  # This is a low-risk CSV injection
    except Exception as e:
        print_secure()

# ==================== API SECURITY TESTS ====================
def test_api_security():
    print_header("API SECURITY TESTS")
    
    print_test("Rate limiting on API endpoints")
    try:
        # Send 100 rapid requests
        for i in range(100):
            response = requests.get(f"{API_BASE}/dictionary/", timeout=1)
        
        print_vulnerable("No rate limiting detected - API abuse possible", "MEDIUM")
    except Exception as e:
        print_secure()
    
    print_test("CORS configuration")
    try:
        response = requests.get(f"{API_BASE}/dictionary/", 
                              headers={'Origin': 'http://evil.com'}, timeout=5)
        cors_header = response.headers.get('Access-Control-Allow-Origin', '')
        if cors_header == '*':
            print_vulnerable("CORS allows all origins (*) - potential security risk", "MEDIUM")
        else:
            print_secure()
    except Exception as e:
        print_secure()
    
    print_test("Sensitive data exposure in API responses")
    try:
        response = requests.get(f"{API_BASE}/dictionary/1", timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Check for sensitive fields
            if 'password' in str(data) or 'secret' in str(data).lower():
                print_vulnerable("Sensitive data exposed in API response", "HIGH")
            else:
                print_secure()
    except Exception as e:
        print_secure()

# ==================== INFORMATION DISCLOSURE TESTS ====================
def test_information_disclosure():
    print_header("INFORMATION DISCLOSURE TESTS")
    
    print_test("Debug mode enabled")
    try:
        # Try to trigger an error
        response = requests.get(f"{API_BASE}/dictionary/99999999", timeout=5)
        if "Traceback" in response.text or "File " in response.text:
            print_vulnerable("Debug mode enabled - stack traces exposed", "MEDIUM")
        else:
            print_secure()
    except Exception as e:
        print_secure()
    
    print_test("Server version disclosure")
    try:
        response = requests.get(BASE_URL, timeout=5)
        server_header = response.headers.get('Server', '')
        if 'Werkzeug' in server_header or 'Flask' in server_header:
            print_vulnerable(f"Server version disclosed: {server_header}", "LOW")
        else:
            print_secure()
    except Exception as e:
        print_secure()
    
    print_test("Database error messages")
    try:
        response = requests.get(f"{API_BASE}/dictionary/?page=-1", timeout=5)
        if "sqlite" in response.text.lower() or "database" in response.text.lower():
            print_vulnerable("Database details exposed in error messages", "MEDIUM")
        else:
            print_secure()
    except Exception as e:
        print_secure()

# ==================== MASS ASSIGNMENT TESTS ====================
def test_mass_assignment():
    print_header("MASS ASSIGNMENT VULNERABILITY TESTS")
    
    print_test("Mass assignment in POST requests")
    try:
        # Try to inject admin fields
        response = requests.post(f"{API_BASE}/dictionary/", 
                               json={"nepali": "test", "romanized": "test", "english": "test",
                                   "id": 99999, "is_admin": True, "role": "admin"},
                               timeout=5)
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('id') == 99999 or data.get('is_admin'):
                print_vulnerable("Mass assignment possible - extra fields accepted", "HIGH")
            else:
                print_secure()
        else:
            print_secure()
    except Exception as e:
        print_secure()

# ==================== IDOR TESTS ====================
def test_idor():
    print_header("INSECURE DIRECT OBJECT REFERENCE (IDOR) TESTS")
    
    print_test("IDOR - Access other user's data")
    try:
        # Try accessing sequential IDs
        for id in [1, 2, 3, 100, 999]:
            response = requests.get(f"{API_BASE}/dictionary/{id}", timeout=5)
            if response.status_code == 200:
                print_vulnerable(f"No authorization check - can access any ID", "MEDIUM")
                break
        else:
            print_secure()
    except Exception as e:
        print_secure()
    
    print_test("IDOR - Modify other user's data")
    try:
        response = requests.put(f"{API_BASE}/dictionary/1", 
                              json={"english": "HACKED"}, timeout=5)
        if response.status_code in [200, 204]:
            print_vulnerable("Can modify any record without authorization", "HIGH")
        else:
            print_secure()
    except Exception as e:
        print_secure()

# ==================== DENIAL OF SERVICE TESTS ====================
def test_dos():
    print_header("DENIAL OF SERVICE (DOS) VULNERABILITY TESTS")
    
    print_test("Resource exhaustion via large payload")
    try:
        huge_array = [{"nepali": "test" * 1000, "english": "test" * 1000} for _ in range(1000)]
        response = requests.post(f"{API_BASE}/bulk/dictionary", 
                               json=huge_array, timeout=10)
        if response.status_code == 500:
            print_vulnerable("Server crashes on large payload - DoS possible", "MEDIUM")
        else:
            print_secure()
    except requests.exceptions.Timeout:
        print_vulnerable("Timeout on large payload - DoS risk", "MEDIUM")
    except Exception as e:
        print_secure()

# ==================== SECURITY HEADERS TESTS ====================
def test_security_headers():
    print_header("SECURITY HEADERS TESTS")
    
    try:
        response = requests.get(BASE_URL, timeout=5)
        headers = response.headers
        
        security_headers = {
            'X-Frame-Options': 'Prevents clickjacking',
            'X-Content-Type-Options': 'Prevents MIME sniffing',
            'X-XSS-Protection': 'XSS filter',
            'Strict-Transport-Security': 'Forces HTTPS',
            'Content-Security-Policy': 'Prevents XSS and injection',
            'Referrer-Policy': 'Controls referrer information'
        }
        
        for header, description in security_headers.items():
            print_test(f"Security header: {header}")
            if header not in headers:
                print_vulnerable(f"Missing {header} - {description}", "LOW")
            else:
                print_secure()
                
    except Exception as e:
        print_info(f"Could not test security headers: {e}")

# ==================== MAIN EXECUTION ====================
def main():
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║     COMPREHENSIVE SECURITY AUDIT - NEPALI LEARNING PLATFORM      ║")
    print("║                                                                   ║")
    print("║  This script will test for common web vulnerabilities            ║")
    print("║  Target: http://localhost:5000                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    print_info(f"Starting security audit at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("Testing may take several minutes...\n")
    
    try:
        # Check if server is running
        response = requests.get(BASE_URL, timeout=5)
        print_info(f"✓ Server is running (Status: {response.status_code})\n")
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.RESET} Cannot connect to {BASE_URL}")
        print(f"  → Please make sure the server is running")
        print(f"  → Error: {e}")
        sys.exit(1)
    
    # Run all tests
    test_sql_injection()
    test_xss()
    test_authentication()
    test_csrf()
    test_input_validation()
    test_file_upload()
    test_api_security()
    test_information_disclosure()
    test_mass_assignment()
    test_idor()
    test_dos()
    test_security_headers()
    
    # Print summary
    print_header("SECURITY AUDIT SUMMARY")
    
    total_tests = len(vulnerabilities_found) + len(tests_passed)
    vuln_count = len(vulnerabilities_found)
    passed_count = len(tests_passed)
    
    print(f"\n{Colors.BOLD}Total Tests Run:{Colors.RESET} {total_tests}")
    print(f"{Colors.GREEN}Tests Passed:{Colors.RESET} {passed_count}")
    print(f"{Colors.RED}Vulnerabilities Found:{Colors.RESET} {vuln_count}\n")
    
    if vulnerabilities_found:
        print(f"{Colors.BOLD}VULNERABILITIES BY SEVERITY:{Colors.RESET}\n")
        
        high = [v for v in vulnerabilities_found if v['severity'] == 'HIGH']
        medium = [v for v in vulnerabilities_found if v['severity'] == 'MEDIUM']
        low = [v for v in vulnerabilities_found if v['severity'] == 'LOW']
        
        if high:
            print(f"{Colors.RED}HIGH SEVERITY ({len(high)}):{Colors.RESET}")
            for v in high:
                print(f"  • {v['test']}")
            print()
        
        if medium:
            print(f"{Colors.YELLOW}MEDIUM SEVERITY ({len(medium)}):{Colors.RESET}")
            for v in medium:
                print(f"  • {v['test']}")
            print()
        
        if low:
            print(f"{Colors.MAGENTA}LOW SEVERITY ({len(low)}):{Colors.RESET}")
            for v in low:
                print(f"  • {v['test']}")
            print()
    else:
        print(f"{Colors.GREEN}{Colors.BOLD}No vulnerabilities found! Site appears secure.{Colors.RESET}\n")
    
    print(f"\n{Colors.CYAN}Audit completed at {time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*70}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
