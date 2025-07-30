# Railway deployment - updated for clean deployment
#!/usr/bin/env python3
"""
Canva OAuth Integration for Railway Deployment
Job Search Automation Platform - Resume PDF Generation
"""

import http.server
import socketserver
import urllib.parse
import json
import requests
import os
from datetime import datetime

# Get port from Railway environment
PORT = int(os.environ.get('PORT', 8080))

class CanvaOAuthHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for Canva OAuth integration"""
    
    def do_GET(self):
        """Handle GET requests for OAuth flow"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        if path == '/':
            self.send_home_page()
        elif path == '/health':
            self.send_health_check()
        elif path == '/canva/auth':
            self.initiate_canva_auth()
        elif path == '/canva/callback':
            self.handle_canva_callback(query)
        else:
            self.send_404()
    
    def send_home_page(self):
        """Send the home page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Canva OAuth Integration - Job Search Automation</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { 
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                        padding: 40px; 
                        text-align: center; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        min-height: 100vh;
                        margin: 0;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .container { 
                        background: rgba(255,255,255,0.95); 
                        padding: 40px; 
                        border-radius: 16px; 
                        box-shadow: 0 20px 40px rgba(0,0,0,0.1); 
                        max-width: 600px; 
                        color: #333;
                    }
                    .btn { 
                        background: #1976d2; 
                        color: white; 
                        padding: 16px 32px; 
                        text-decoration: none; 
                        border-radius: 8px; 
                        display: inline-block; 
                        margin: 15px 10px; 
                        font-weight: 600;
                        transition: all 0.3s ease;
                    }
                    .btn:hover { 
                        background: #1565c0; 
                        transform: translateY(-2px);
                        box-shadow: 0 8px 16px rgba(25,118,210,0.3);
                    }
                    .btn.success { background: #4caf50; }
                    .btn.success:hover { background: #45a049; }
                    h1 { color: #333; margin-bottom: 10px; }
                    .subtitle { color: #666; margin-bottom: 30px; }
                    .status { 
                        background: #e3f2fd; 
                        color: #1976d2; 
                        padding: 20px; 
                        border-radius: 8px; 
                        margin: 20px 0; 
                        border-left: 4px solid #1976d2;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎨 Canva OAuth Integration</h1>
                    <p class="subtitle">Job Search Automation Platform<br>Resume PDF Generation Testing</p>
                    
                    <div class="status">
                        <strong>🧪 OAuth Testing Environment</strong><br>
                        This deployment tests the Canva OAuth flow required for API approval.
                    </div>
                    
                    <div>
                        <a href="/canva/auth" class="btn">🚀 Connect to Canva</a>
                        <a href="/health" class="btn success">❤️ Health Check</a>
                    </div>
                    
                    <div style="margin-top: 30px; font-size: 14px; color: #666;">
                        <p><strong>Callback URL:</strong> https://job-search-automation-production.up.railway.app/canva/callback</p>
                        <p><strong>Scopes:</strong> design:content, design:meta, app, asset, folder, profile</p>
                    </div>
                </div>
            </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def send_health_check(self):
        """Send health check response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        health_data = {
            "status": "healthy",
            "service": "canva-oauth-integration",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "home": "/",
                "auth": "/canva/auth",
                "callback": "/canva/callback",
                "health": "/health"
            },
            "canva_config": {
                "client_id": "OC-AZhcJXJ2NmnL",
                "callback_url": "https://job-search-automation-production.up.railway.app/canva/callback",
                "scopes": [
                    "design:content:read",
                    "design:content:write", 
                    "design:meta:read",
                    "app:read",
                    "app:write",
                    "asset:read",
                    "asset:write",
                    "folder:read",
                    "folder:write",
                    "profile:read"
                ]
            }
        }
        
        self.wfile.write(json.dumps(health_data, indent=2).encode())
    
    def initiate_canva_auth(self):
        """Initiate Canva OAuth flow"""
        client_id = "OC-AZhcJXJ2NmnL"
        redirect_uri = "https://job-search-automation-production.up.railway.app/canva/callback"
        scope = "design:content:read design:content:write design:meta:read app:read app:write asset:read asset:write folder:read folder:write profile:read"
        
        auth_url = (
            f"https://www.canva.com/api/oauth/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope={scope}"
        )
        
        print(f"Redirecting to Canva OAuth: {auth_url}")
        
        self.send_response(302)
        self.send_header('Location', auth_url)
        self.end_headers()
    
    def handle_canva_callback(self, query):
        """Handle Canva OAuth callback"""
        code = query.get('code', [None])[0]
        error = query.get('error', [None])[0]
        error_description = query.get('error_description', [None])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        if error:
            print(f"OAuth error: {error} - {error_description}")
            html = f"""
            <!DOCTYPE html>
            <html>
                <head><title>OAuth Error</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                    <h1 style="color: #d32f2f;">❌ OAuth Error</h1>
                    <p><strong>Error:</strong> {error}</p>
                    <p><strong>Description:</strong> {error_description or 'Unknown error'}</p>
                    <a href="/canva/auth" style="background: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Try Again</a>
                </body>
            </html>
            """
            self.wfile.write(html.encode())
            return
        
        if not code:
            html = """
            <!DOCTYPE html>
            <html>
                <head><title>Missing Code</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                    <h1 style="color: #d32f2f;">❌ Missing Authorization Code</h1>
                    <p>No authorization code received from Canva.</p>
                    <a href="/canva/auth" style="background: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Try Again</a>
                </body>
            </html>
            """
            self.wfile.write(html.encode())
            return
        
        # Exchange authorization code for access token
        try:
            print(f"Exchanging authorization code: {code[:10]}...")
            
            token_data = {
                'grant_type': 'authorization_code',
                'client_id': 'OC-AZhcJXJ2NmnL',
                'client_secret': os.environ.get('CANVA_CLIENT_SECRET', ''),
                'code': code,
                'redirect_uri': 'https://job-search-automation-production.up.railway.app/canva/callback'
            }
            
            response = requests.post('https://api.canva.com/rest/v1/oauth/token', data=token_data)
            
            if response.status_code == 200:
                token_response = response.json()
                access_token = token_response.get('access_token', '')
                
                print(f"✅ OAuth success! Token received: {access_token[:20]}...")
                
                # Try to get user profile to verify token
                try:
                    headers = {'Authorization': f'Bearer {access_token}'}
                    profile_response = requests.get('https://api.canva.com/rest/v1/me', headers=headers)
                    
                    if profile_response.status_code == 200:
                        profile = profile_response.json()
                        user_name = profile.get('display_name', 'User')
                        user_id = profile.get('id', 'unknown')
                    else:
                        user_name = 'User'
                        user_id = 'unknown'
                except:
                    user_name = 'User'
                    user_id = 'unknown'
                
                html = f"""
                <!DOCTYPE html>
                <html>
                    <head>
                        <title>OAuth Success</title>
                        <style>
                            body {{ 
                                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                                padding: 40px; 
                                text-align: center; 
                                background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
                                color: white;
                                min-height: 100vh;
                                margin: 0;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                            }}
                            .success-card {{ 
                                background: rgba(255,255,255,0.95); 
                                padding: 40px; 
                                border-radius: 16px; 
                                box-shadow: 0 20px 40px rgba(0,0,0,0.1); 
                                max-width: 600px; 
                                color: #333;
                            }}
                            .success-icon {{ color: #4caf50; font-size: 64px; margin-bottom: 20px; }}
                            h1 {{ color: #4caf50; margin-bottom: 20px; }}
                            .btn {{ 
                                background: #1976d2; 
                                color: white; 
                                padding: 12px 24px; 
                                text-decoration: none; 
                                border-radius: 8px; 
                                display: inline-block; 
                                margin: 10px; 
                                font-weight: 600;
                            }}
                            .success-box {{ 
                                background: #e8f5e8; 
                                color: #2e7d32; 
                                border: 2px solid #4caf50; 
                                padding: 20px; 
                                border-radius: 8px; 
                                margin: 20px 0; 
                            }}
                            .token-info {{ 
                                background: #f5f5f5; 
                                padding: 15px; 
                                border-radius: 8px; 
                                font-family: monospace; 
                                font-size: 12px; 
                                margin: 15px 0; 
                                word-break: break-all;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="success-card">
                            <div class="success-icon">✅</div>
                            <h1>OAuth Success!</h1>
                            <p><strong>Welcome, {user_name}!</strong></p>
                            <p>Your Canva account has been successfully connected to the Job Search Automation platform.</p>
                            
                            <div class="success-box">
                                <strong>🎉 Integration Working!</strong><br>
                                Your Canva OAuth flow is properly configured and ready for API review submission.
                            </div>
                            
                            <div class="token-info">
                                <strong>Token:</strong> {access_token[:30]}...<br>
                                <strong>User ID:</strong> {user_id}<br>
                                <strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                            </div>
                            
                            <div>
                                <a href="/" class="btn">🏠 Back to Home</a>
                                <a href="/health" class="btn">📊 Health Check</a>
                            </div>
                        </div>
                    </body>
                </html>
                """
                self.wfile.write(html.encode())
            else:
                print(f"❌ Token exchange failed: {response.status_code} - {response.text}")
                html = f"""
                <!DOCTYPE html>
                <html>
                    <head><title>Token Exchange Failed</title></head>
                    <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                        <h1 style="color: #d32f2f;">❌ Token Exchange Failed</h1>
                        <p><strong>Status:</strong> {response.status_code}</p>
                        <p><strong>Response:</strong> {response.text}</p>
                        <a href="/canva/auth" style="background: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Try Again</a>
                    </body>
                </html>
                """
                self.wfile.write(html.encode())
                
        except Exception as e:
            print(f"❌ Exception during token exchange: {e}")
            html = f"""
            <!DOCTYPE html>
            <html>
                <head><title>Exception</title></head>
                <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                    <h1 style="color: #d32f2f;">❌ Exception</h1>
                    <p><strong>Error:</strong> {str(e)}</p>
                    <a href="/canva/auth" style="background: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Try Again</a>
                </body>
            </html>
            """
            self.wfile.write(html.encode())
    
    def send_404(self):
        """Send 404 response"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
            <head><title>Not Found</title></head>
            <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                <h1>404 - Not Found</h1>
                <p>The requested resource was not found.</p>
                <a href="/" style="background: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px;">Go Home</a>
            </body>
        </html>
        """
        self.wfile.write(html.encode())

if __name__ == "__main__":
    print(f"🚀 Starting Canva OAuth Integration Server")
    print(f"📡 Port: {PORT}")
    print(f"🔗 Callback URL: https://job-search-automation-production.up.railway.app/canva/callback")
    print(f"🎨 Client ID: OC-AZhcJXJ2NmnL")
    
    try:
        with socketserver.TCPServer(("", PORT), CanvaOAuthHandler) as httpd:
            print(f"✅ Server running on port {PORT}")
            print(f"🌐 Access at: https://job-search-automation-production.up.railway.app/")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        exit(1)
