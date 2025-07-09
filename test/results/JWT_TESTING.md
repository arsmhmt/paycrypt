# JWT Authentication Testing Guide

This guide provides instructions for testing the JWT authentication flow in the application.

## Prerequisites

1. Ensure the Flask application is running:
   ```bash
   flask run
   ```

2. Make sure you have the test admin user created:
   - Username: `testadmin`
   - Password: `testpass123`

## Testing the Login Flow

### 1. Using the Web Interface

1. Open your browser and navigate to: `http://localhost:5000/auth/login`
2. Enter the test admin credentials
3. Check the browser's developer tools (F12) > Application > Cookies to verify JWT cookies are set

### 2. Using the Test Scripts

Run the following scripts in order to test the authentication flow:

1. **Check JWT Configuration**:
   ```bash
   python check_jwt_config.py
   ```

2. **Test Login and Dashboard Access**:
   ```bash
   python verify_login.py
   ```

3. **Run All Tests**:
   ```bash
   python run_auth_tests.py
   ```

## Verifying JWT Cookies in Browser

After logging in, you can check the JWT cookies in the browser:

1. Open Developer Tools (F12)
2. Go to the Console tab
3. Paste the contents of `check_browser_cookies.js` and press Enter
4. This will display information about the JWT cookies and their properties

## Common Issues and Solutions

### 1. JWT Cookies Not Being Set

- Verify that `JWT_TOKEN_LOCATION` is set to `['cookies', 'headers']` in your config
- Check that `JWT_COOKIE_SECURE` is `False` in development (or `True` in production with HTTPS)
- Ensure the response includes the `Set-Cookie` headers

### 2. 401 Unauthorized When Accessing Protected Routes

- Verify the JWT cookie is being sent with the request
- Check that the token hasn't expired
- Ensure the JWT secret key matches between the server and client

### 3. CSRF Token Mismatch

- If you're getting CSRF token errors, ensure:
  - `JWT_COOKIE_CSRF_PROTECT` is set correctly
  - CSRF token is included in the request headers for API calls
  - The `X-CSRF-TOKEN` header matches the CSRF token in the cookie

## Debugging Tips

1. **Check Server Logs**: Look for any error messages in the Flask console output
2. **Inspect Network Traffic**: Use browser developer tools to inspect the login request/response
3. **Verify Token**: Use a JWT debugger (like [jwt.io](https://jwt.io/)) to inspect the token contents
4. **Check Cookie Settings**: Ensure cookies are being set with the correct domain and path

## Security Considerations

- In production, always use HTTPS
- Set `JWT_COOKIE_SECURE = True` in production
- Consider enabling CSRF protection in production
- Set appropriate `SameSite` cookie attributes based on your requirements
