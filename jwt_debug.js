/**
 * JWT Debugging Helper
 * 
 * Copy and paste this script into your browser's console to debug JWT tokens.
 * This will help you verify if JWT tokens are being set and are valid.
 */

class JWTDebugger {
  constructor() {
    this.token = null;
    this.decodedToken = null;
    this.cookies = {};
    this.init();
  }

  /**
   * Initialize the debugger
   */
  init() {
    this.parseCookies();
    this.extractTokens();
  }

  /**
   * Parse all cookies into an object
   */
  parseCookies() {
    document.cookie.split(';').forEach(cookie => {
      const [name, value] = cookie.trim().split('=');
      this.cookies[name] = value;
    });
  }

  /**
   * Extract and decode JWT tokens from cookies
   */
  extractTokens() {
    const accessToken = this.cookies['access_token_cookie'];
    const refreshToken = this.cookies['refresh_token_cookie'];

    if (accessToken) {
      console.log('\n🔑 Access Token Found');
      console.log('-------------------');
      this.decodeAndPrintToken(accessToken, 'Access Token');
    } else {
      console.log('\n❌ No Access Token found in cookies');
    }

    if (refreshToken) {
      console.log('\n🔄 Refresh Token Found');
      console.log('---------------------');
      this.decodeAndPrintToken(refreshToken, 'Refresh Token');
    } else {
      console.log('\n❌ No Refresh Token found in cookies');
    }
  }

  /**
   * Decode a JWT token and print its contents
   * @param {string} token - The JWT token to decode
   * @param {string} tokenName - Display name for the token
   */
  decodeAndPrintToken(token, tokenName) {
    try {
      // Split the token into its parts
      const [headerB64, payloadB64, signature] = token.split('.');
      
      if (!headerB64 || !payloadB64) {
        throw new Error('Invalid token format');
      }

      // Decode the header and payload
      const header = JSON.parse(atob(headerB64));
      const payload = JSON.parse(atob(payloadB64));
      
      // Format the output
      console.log(`🔍 ${tokenName} Details:`);
      console.log('Header:', header);
      
      console.log('\n📋 Payload:');
      // Format dates for better readability
      const formattedPayload = { ...payload };
      
      if (formattedPayload.iat) {
        formattedPayload.iat = `${formattedPayload.iat} (${new Date(formattedPayload.iat * 1000).toISOString()})`;
      }
      if (formattedPayload.exp) {
        const expDate = new Date(formattedPayload.exp * 1000);
        const now = new Date();
        const expiresIn = Math.ceil((expDate - now) / 1000); // in seconds
        const expiresInMinutes = Math.ceil(expiresIn / 60);
        
        formattedPayload.exp = `${formattedPayload.exp} (${expDate.toISOString()})`;
        formattedPayload.expires_in = `${expiresIn} seconds (${expiresInMinutes} minutes) from now`;
        
        if (expiresIn <= 0) {
          console.warn('⚠️ This token has expired!');
        }
      }
      
      console.table(formattedPayload);
      
      // Check token expiration
      if (formattedPayload.exp) {
        const expTime = new Date(payload.exp * 1000);
        const now = new Date();
        
        if (now > expTime) {
          console.warn('⚠️ This token has expired!');
        } else {
          console.log('✅ Token is valid');
        }
      }
      
      return { header, payload, signature };
    } catch (error) {
      console.error(`❌ Error decoding ${tokenName}:`, error.message);
      return null;
    }
  }

  /**
   * Check if JWT tokens are being sent with requests
   */
  monitorRequests() {
    console.log('\n🔍 Monitoring AJAX requests for JWT tokens...');
    
    // Store the original fetch function
    const originalFetch = window.fetch;
    
    // Override the fetch function
    window.fetch = async (...args) => {
      const [resource, config = {}] = args;
      
      // Log the request
      console.log(`\n📤 Outgoing request to: ${resource}`);
      
      // Check for JWT in headers
      const authHeader = config.headers?.get?.('Authorization') || 
                        config.headers?.Authorization ||
                        (typeof config.headers?.get === 'function' ? config.headers.get('Authorization') : null);
      
      if (authHeader?.startsWith('Bearer ')) {
        console.log('🔑 JWT found in Authorization header');
      } else {
        console.log('ℹ️ No JWT found in Authorization header');
      }
      
      // Check for cookies being sent
      const credentials = config.credentials || 'same-origin';
      console.log(`🔐 Credentials mode: ${credentials}`);
      
      // Make the actual request
      const response = await originalFetch(resource, config);
      
      // Check for Set-Cookie in response
      const setCookieHeader = response.headers.get('set-cookie');
      if (setCookieHeader) {
        console.log('🍪 Set-Cookie header found in response');
        
        // Check if it's setting JWT cookies
        if (setCookieHeader.includes('access_token_cookie') || 
            setCookieHeader.includes('refresh_token_cookie')) {
          console.log('🎉 JWT cookies are being set!');
        }
      }
      
      return response;
    };
    
    console.log('✅ Request monitoring enabled. Make some requests to see JWT details.');
  }
}

// Create and run the debugger
console.clear();
console.log('%c🔍 JWT Debugger Initialized', 'font-size: 16px; font-weight: bold; color: #4CAF50;');
console.log('Use the following methods to debug JWT:');
console.log('- `jwtDebugger.monitorRequests()` - Monitor AJAX requests for JWT tokens');
console.log('- `jwtDebugger.extractTokens()` - Check current JWT tokens in cookies');

const jwtDebugger = new JWTDebugger();

// Add to global scope for easy access
window.jwtDebugger = jwtDebugger;
