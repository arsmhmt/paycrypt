// Run this in your browser's console after logging in to check JWT cookies
function checkJWTCookies() {
    console.log("=== JWT Cookie Check ===\n");
    
    // Get all cookies
    const cookies = document.cookie.split(';')
        .map(cookie => cookie.trim())
        .reduce((acc, cookie) => {
            const [name, value] = cookie.split('=');
            acc[name] = value;
            return acc;
        }, {});
    
    // Check for JWT cookies
    const jwtCookies = {};
    
    // Access token
    if (cookies.access_token_cookie) {
        jwtCookies.access_token = {
            exists: true,
            value: cookies.access_token_cookie,
            httpOnly: document.cookie.indexOf('HttpOnly') !== -1,
            secure: document.cookie.indexOf('Secure') !== -1,
            sameSite: document.cookie.match(/SameSite=([^;]+)/)?.[1] || 'Not set'
        };
    } else {
        jwtCookies.access_token = { exists: false };
    }
    
    // Refresh token
    if (cookies.refresh_token_cookie) {
        jwtCookies.refresh_token = {
            exists: true,
            value: cookies.refresh_token_cookie,
            httpOnly: document.cookie.indexOf('HttpOnly') !== -1,
            secure: document.cookie.indexOf('Secure') !== -1,
            sameSite: document.cookie.match(/SameSite=([^;]+)/)?.[1] || 'Not set'
        };
    } else {
        jwtCookies.refresh_token = { exists: false };
    }
    
    // Print results
    console.log("JWT Cookies:", jwtCookies);
    
    // Try to decode the token (just header and payload for display)
    if (jwtCookies.access_token.exists) {
        try {
            const tokenParts = jwtCookies.access_token.value.split('.');
            if (tokenParts.length === 3) {
                const header = JSON.parse(atob(tokenParts[0]));
                const payload = JSON.parse(atob(tokenParts[1]));
                
                console.log("\nAccess Token Details:");
                console.log("Header:", header);
                console.log("Payload:", {
                    ...payload,
                    // Convert JWT timestamp to human-readable date
                    iat: new Date(payload.iat * 1000).toISOString(),
                    exp: new Date(payload.exp * 1000).toISOString(),
                    nbf: payload.nbf ? new Date(payload.nbf * 1000).toISOString() : null
                });
            }
        } catch (e) {
            console.error("Error decoding token:", e);
        }
    }
    
    // Check if the page is loaded over HTTPS
    console.log("\nPage loaded over HTTPS:", window.location.protocol === 'https:');
    
    // Check if cookies are accessible via document.cookie
    console.log("\nCookies accessible via document.cookie:", document.cookie ? "Yes" : "No");
    
    // Check if we can detect HTTP-only cookies (should be false for HTTP-only cookies)
    console.log("Can access HTTP-only cookies:", 
        document.cookie.indexOf('access_token_cookie') === -1 && 
        document.cookie.indexOf('refresh_token_cookie') === -1 ? "No (expected)" : "Yes (potential security issue)");
}

// Run the check
checkJWTCookies();
