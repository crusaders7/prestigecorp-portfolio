#!/usr/bin/env python3
"""Test news.prestigecorp.au for government network compatibility issues"""

import requests
import ssl
import socket
from urllib.parse import urlparse
import json


def test_ssl_security():
    """Test SSL/TLS configuration"""
    print("🔒 TESTING SSL/TLS SECURITY")
    print("=" * 50)

    try:
        # Test SSL connection
        hostname = "news.prestigecorp.au"
        port = 443

        # Create SSL context
        context = ssl.create_default_context()

        # Connect and get certificate info
        with socket.create_connection((hostname, port)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

                print(f"✅ SSL Connection successful")
                print(f"📜 Subject: {cert.get('subject', 'Unknown')}")
                print(f"🏢 Issuer: {cert.get('issuer', 'Unknown')}")
                print(f"📅 Valid from: {cert.get('notBefore', 'Unknown')}")
                print(f"📅 Valid until: {cert.get('notAfter', 'Unknown')}")
                print(f"🔐 SSL Version: {ssock.version()}")

                # Check for government-friendly certificate authorities
                issuer_info = str(cert.get('issuer', ''))
                if "Let's Encrypt" in issuer_info:
                    print("⚠️  WARNING: Using Let's Encrypt (some gov networks block)")

    except Exception as e:
        print(f"❌ SSL Error: {e}")


def test_headers_security():
    """Test HTTP security headers"""
    print("\n🛡️  TESTING SECURITY HEADERS")
    print("=" * 50)

    try:
        response = requests.get("https://news.prestigecorp.au", timeout=10)
        headers = response.headers

        security_headers = {
            'Strict-Transport-Security': 'HSTS protection',
            'Content-Security-Policy': 'CSP protection',
            'X-Frame-Options': 'Clickjacking protection',
            'X-Content-Type-Options': 'MIME sniffing protection',
            'X-XSS-Protection': 'XSS protection',
            'Referrer-Policy': 'Referrer control'
        }

        print("Present headers:")
        for header, description in security_headers.items():
            if header in headers:
                print(f"✅ {header}: {headers[header]}")
            else:
                print(f"❌ {header}: Missing ({description})")

        # Check for problematic headers
        problematic = ['Access-Control-Allow-Origin']
        for header in problematic:
            if header in headers:
                value = headers[header]
                if value == '*':
                    print(
                        f"⚠️  {header}: {value} (Too permissive for gov networks)")

    except Exception as e:
        print(f"❌ Header test error: {e}")


def test_content_issues():
    """Test for content that might be blocked"""
    print("\n📄 TESTING CONTENT ISSUES")
    print("=" * 50)

    try:
        response = requests.get("https://news.prestigecorp.au", timeout=10)
        content = response.text.lower()

        # Check for external resources that might be blocked
        external_patterns = [
            'cdn.jsdelivr.net',
            'cdnjs.cloudflare.com',
            'fonts.googleapis.com',
            'ajax.googleapis.com'
        ]

        blocked_found = []
        for pattern in external_patterns:
            if pattern in content:
                blocked_found.append(pattern)

        if blocked_found:
            print("⚠️  External resources that may be blocked:")
            for resource in blocked_found:
                print(f"   - {resource}")
        else:
            print("✅ No commonly blocked external resources found")

        # Check for JavaScript that might trigger security filters
        if 'eval(' in content:
            print("⚠️  WARNING: eval() usage detected (security risk)")
        if 'document.write' in content:
            print("⚠️  WARNING: document.write usage detected")

    except Exception as e:
        print(f"❌ Content test error: {e}")


def test_network_connectivity():
    """Test basic connectivity from different perspectives"""
    print("\n🌐 TESTING NETWORK CONNECTIVITY")
    print("=" * 50)

    try:
        # Test HTTP redirect
        http_response = requests.get(
            "http://news.prestigecorp.au", timeout=10, allow_redirects=False)
        if http_response.status_code in [301, 302, 308]:
            print(f"✅ HTTP to HTTPS redirect: {http_response.status_code}")
        else:
            print(f"⚠️  No HTTP redirect: {http_response.status_code}")

        # Test HTTPS directly
        https_response = requests.get(
            "https://news.prestigecorp.au", timeout=10)
        print(f"✅ HTTPS response: {https_response.status_code}")
        print(f"📊 Content size: {len(https_response.content):,} bytes")

        # Test response time
        import time
        start_time = time.time()
        requests.get("https://news.prestigecorp.au", timeout=10)
        response_time = time.time() - start_time
        print(f"⏱️  Response time: {response_time:.2f} seconds")

        if response_time > 5:
            print("⚠️  Slow response time may cause timeouts on restrictive networks")

    except Exception as e:
        print(f"❌ Connectivity error: {e}")


def test_government_network_compatibility():
    """Test specific issues common with government networks"""
    print("\n🏛️  GOVERNMENT NETWORK COMPATIBILITY")
    print("=" * 50)

    issues = []

    try:
        response = requests.get("https://news.prestigecorp.au", timeout=10)

        # Check certificate authority
        if "Let's Encrypt" in str(response.request.url):
            issues.append("Let's Encrypt certificates may be blocked")

        # Check for external CDNs
        content = response.text
        if 'cdn.tailwindcss.com' in content:
            issues.append("External Tailwind CSS CDN may be blocked")
        if 'cdnjs.cloudflare.com' in content:
            issues.append("Cloudflare CDN may be blocked")
        if 'fonts.googleapis.com' in content:
            issues.append("Google Fonts may be blocked")

        # Check CORS policy
        headers = response.headers
        if headers.get('Access-Control-Allow-Origin') == '*':
            issues.append(
                "Permissive CORS policy may trigger security filters")

        if issues:
            print("⚠️  Potential government network issues:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ No obvious government network compatibility issues")

    except Exception as e:
        print(f"❌ Compatibility test error: {e}")


def main():
    print("🔍 COMPREHENSIVE DOMAIN SECURITY TEST")
    print("Testing: news.prestigecorp.au")
    print("=" * 70)

    test_ssl_security()
    test_headers_security()
    test_content_issues()
    test_network_connectivity()
    test_government_network_compatibility()

    print("\n" + "=" * 70)
    print("🎯 RECOMMENDATIONS FOR GOVERNMENT NETWORK ACCESS:")
    print("1. Consider using self-hosted resources instead of external CDNs")
    print("2. Add stricter Content-Security-Policy headers")
    print("3. Consider enterprise SSL certificate instead of Let's Encrypt")
    print("4. Add X-Frame-Options and other security headers")
    print("5. Test with specific government network requirements")


if __name__ == '__main__':
    main()
