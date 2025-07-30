# OAuth URL should be constructed like this:
auth_url = f"https://www.canva.com/api/oauth/authorize?client_id={CANVA_CLIENT_ID}&redirect_uri={urllib.parse.quote(CALLBACK_URL)}&response_type=code&scope=design%3Acontent%3Aread%20design%3Acontent%3Awrite%20design%3Ameta%3Aread"
