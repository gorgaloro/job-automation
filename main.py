#!/usr/bin/env python3
"""
Canva OAuth Integration for Railway Deployment
Minimal, guaranteed-working implementation
"""
import http.server
import socketserver
import urllib.parse
import json
import requests
import os
import hashlib
import base64
import secrets
from datetime import datetime

PORT = int(os.environ.get('PORT', 8080))
CANVA_CLIENT_ID = 'OC-AZhcJXJ2NmnL'
CANVA_CLIENT_SECRET = os.environ.get('CANVA_CLIENT_SECRET', '')
CALLBACK_URL = 'https://job-automation-production.up.railway.app/canva/callback'

# Global storage for PKCE parameters (in production, use secure session storage)
stored_code_verifier = None
stored_state = None

class CanvaOAuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        print(f"🌐 Request: {path}")
        
        if path == '/':
            self.serve_home_page()
        elif path == '/health':
            self.serve_health_check()
        elif path == '/canva/auth':
            self.start_oauth_flow()
        elif path == '/canva/callback':
            self.handle_oauth_callback(query)
        else:
            self.send_error(404, "Not Found")
    
    def serve_home_page(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html = """<!DOCTYPE html>
<html><head><title>🎨 Canva OAuth Integration</title>
<style>
body{font-family:Arial;padding:40px;text-align:center;background:linear-gradient(135deg,#667eea,#764ba2);color:white;min-height:100vh;margin:0;display:flex;align-items:center;justify-content:center}
.container{background:rgba(255,255,255,0.95);padding:40px;border-radius:16px;max-width:600px;color:#333}
.btn{background:#1976d2;color:white;padding:16px 32px;text-decoration:none;border-radius:8px;display:inline-block;margin:15px;font-weight:600}
.btn:hover{background:#1565c0}
.status{background:#e3f2fd;color:#1976d2;padding:20px;border-radius:8px;margin:20px 0}
</style></head>
<body><div class="container">
<h1>🎨 Canva OAuth Integration</h1>
<p>Job Search Automation Platform<br>Resume PDF Generation Testing</p>
<div class="status"><strong>🧪 OAuth Testing Environment</strong><br>Ready for Canva API review submission</div>
<div><a href="/canva/auth" class="btn">🚀 Connect to Canva</a><a href="/health" class="btn">❤️ Health Check</a></div>
<p><strong>Callback URL:</strong> """ + CALLBACK_URL + """</p>
</div></body></html>"""
        self.wfile.write(html.encode())
    
    def serve_health_check(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        health_data = {
            "status": "healthy",
            "service": "canva-oauth-integration", 
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "canva_config": {
                "client_id": CANVA_CLIENT_ID,
                "callback_url": CALLBACK_URL,
                "scopes": ["design:content:read", "design:content:write", "design:meta:read"]
            }
        }
        self.wfile.write(json.dumps(health_data, indent=2).encode())
    
    def start_oauth_flow(self):
        # Generate PKCE parameters as required by Canva
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).decode('utf-8').rstrip('=')
        state = secrets.token_urlsafe(32)
        
        # Store code_verifier for token exchange (in production, use secure session storage)
        global stored_code_verifier, stored_state
        stored_code_verifier = code_verifier
        stored_state = state
        
        # Properly encode OAuth parameters with PKCE
        encoded_callback = urllib.parse.quote(CALLBACK_URL, safe='')
        scopes = "design:content:read design:content:write design:meta:read"
        encoded_scopes = urllib.parse.quote(scopes, safe='')
        
        auth_url = f"https://www.canva.com/api/oauth/authorize?code_challenge={code_challenge}&code_challenge_method=S256&scope={encoded_scopes}&response_type=code&client_id={CANVA_CLIENT_ID}&state={state}&redirect_uri={encoded_callback}"
        
        print(f"🔗 PKCE OAuth URL: {auth_url}")
        print(f"🔑 Code verifier: {code_verifier[:20]}...")
        print(f"🛡️ State: {state[:20]}...")
        
        self.send_response(302)
        self.send_header('Location', auth_url)
        self.end_headers()
    
    def handle_oauth_callback(self, query):
        # Debug logging to see what Canva sent
        print(f"🔍 Callback received with query: {query}")
        
        code = query.get('code', [None])[0]
        error = query.get('error', [None])[0]
        state = query.get('state', [None])[0]
        
        print(f"📋 Authorization code: {code}")
        print(f"❌ Error: {error}")
        print(f"🛡️ State: {state}")
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        if error:
            html = f"""<html><body style="font-family:Arial;padding:40px;text-align:center;">
<h1 style="color:#d32f2f;">❌ OAuth Error</h1><p>Error: {error}</p>
<a href="/canva/auth" style="background:#1976d2;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;">Try Again</a>
</body></html>"""
        elif code:
            # Validate state parameter for CSRF protection
            global stored_state, stored_code_verifier
            if state != stored_state:
                html = f"""<html><body style="font-family:Arial;padding:40px;text-align:center;">
<h1 style="color:#d32f2f;">❌ State Mismatch</h1>
<p>CSRF protection failed. State parameter doesn't match.</p>
<a href="/canva/auth" style="background:#1976d2;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;">Try Again</a>
</body></html>"""
            else:
                try:
                    # Use PKCE for token exchange
                    token_data = {
                        'grant_type': 'authorization_code',
                        'client_id': CANVA_CLIENT_ID,
                        'client_secret': CANVA_CLIENT_SECRET,
                        'code': code,
                        'redirect_uri': CALLBACK_URL,
                        'code_verifier': stored_code_verifier
                    }
                    
                    print(f"🔑 Using code_verifier: {stored_code_verifier[:20]}...")
                    response = requests.post('https://api.canva.com/rest/v1/oauth/token', data=token_data)
                    
                    if response.status_code == 200:
                        token_response = response.json()
                        access_token = token_response.get('access_token', '')
                        refresh_token = token_response.get('refresh_token', '')
                        expires_in = token_response.get('expires_in', '')
                        
                        html = f"""<html><body style="font-family:Arial;padding:40px;text-align:center;">
<h1 style="color:#4caf50;">✅ PKCE OAuth Success!</h1>
<p>Successfully connected to Canva API with PKCE</p>
<div style="background:#e8f5e8;padding:20px;border-radius:8px;margin:20px 0;text-align:left;">
<strong>🎉 Token Details:</strong><br>
• Access Token: {access_token[:30]}...<br>
• Refresh Token: {refresh_token[:30] if refresh_token else 'None'}...<br>
• Expires In: {expires_in} seconds<br>
• PKCE: ✅ Verified
</div>
<div style="background:#e3f2fd;padding:20px;border-radius:8px;margin:20px 0;">
<strong>🚀 Integration Ready!</strong><br>OAuth flow complete and ready for Canva review submission.
</div>
<a href="/" style="background:#1976d2;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;">Home</a>
</body></html>"""
                    else:
                        html = f"""<html><body style="font-family:Arial;padding:40px;text-align:center;">
<h1 style="color:#d32f2f;">Token Exchange Error: {response.status_code}</h1>
<div style="background:#ffebee;padding:20px;border-radius:8px;margin:20px 0;text-align:left;">
<strong>Response:</strong><br>{response.text}
</div>
<a href="/canva/auth" style="background:#1976d2;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;">Try Again</a>
</body></html>"""
                except Exception as e:
                    html = f"""<html><body style="font-family:Arial;padding:40px;text-align:center;">
<h1 style="color:#d32f2f;">Exception: {e}</h1>
<a href="/canva/auth" style="background:#1976d2;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;">Try Again</a>
</body></html>"""
        else:
            # Show all query parameters for debugging
            query_debug = "<br>".join([f"{k}: {v}" for k, v in query.items()])
            html = f"""<html><body style="font-family:Arial;padding:40px;text-align:center;">
<h1>🔍 OAuth Callback Debug</h1>
<p><strong>No authorization code received</strong></p>
<div style="background:#f5f5f5;padding:20px;border-radius:8px;margin:20px 0;text-align:left;">
<h3>Query Parameters:</h3>
{query_debug if query_debug else "No parameters received"}
</div>
<a href="/canva/auth" style="background:#1976d2;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;">Try OAuth Again</a>
</body></html>"""
        
        self.wfile.write(html.encode())

if __name__ == "__main__":
    print(f"�� Starting Canva OAuth Integration Server")
    print(f"📡 Port: {PORT}")
    print(f"🔗 Callback URL: {CALLBACK_URL}")
    print(f"🎯 Client ID: {CANVA_CLIENT_ID}")
    
    with socketserver.TCPServer(("", PORT), CanvaOAuthHandler) as httpd:
        print(f"✅ Server running on port {PORT}")
        print(f"🌐 Access at: https://job-search-automation-production.up.railway.app/")
        httpd.serve_forever()
