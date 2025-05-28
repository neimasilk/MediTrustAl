# Frontend Security Implementation

This document outlines the security measures implemented in the MediTrustAI frontend application.

## Overview

The frontend implements multiple layers of security to protect user data and prevent common web vulnerabilities:

1. **Token Management with Expiry**
2. **Centralized Error Handling**
3. **API Request Security**
4. **Automatic Session Management**

## 1. Enhanced Token Management

### Location: `src/utils/tokenManager.js`

**Features:**
- Token expiry tracking with configurable timeout (default: 30 minutes)
- Automatic token cleanup when expired
- Secure token validation before usage

**Security Benefits:**
- Reduces risk of token replay attacks
- Limits exposure window if token is compromised
- Automatic cleanup prevents stale token usage

**Usage:**
```javascript
// Save token with 30-minute expiry
saveToken(token, 30);

// Get token (returns null if expired)
const token = getToken();

// Check expiry without removing token
if (isTokenExpired()) {
  // Handle expired token
}
```

## 2. Centralized Error Handling

### Location: `src/utils/errorHandler.js`

**Features:**
- Standardized error message extraction
- Structured error logging (development only)
- Authentication error handling with automatic logout
- User-friendly error notifications

**Security Benefits:**
- Prevents sensitive error information leakage
- Consistent error handling across application
- Automatic session cleanup on auth errors

**Usage:**
```javascript
try {
  // API call
} catch (error) {
  const { userMessage } = getErrorMessage(error);
  logError('Operation Name', error, { context: 'additional info' });
  // Show user-friendly message
}
```

## 3. API Request Security

### Location: `src/utils/apiInterceptor.js`

**Features:**
- Automatic token validation before requests
- Centralized authentication header management
- Authenticated fetch wrapper with error handling
- Periodic token expiry checking

**Security Benefits:**
- Prevents requests with expired tokens
- Automatic session cleanup on authentication failures
- Consistent authentication across all API calls

**Usage:**
```javascript
// Validate token before request
if (!validateTokenBeforeRequest()) {
  // Handle authentication required
}

// Make authenticated request
const response = await authenticatedFetch('/api/endpoint', {
  method: 'POST',
  body: JSON.stringify(data)
});
```

## 4. Redux Authentication State Management

### Location: `src/store/slices/authSlice.js`

**Features:**
- Token validation on application initialization
- Automatic cleanup of expired tokens
- Session expiry action with user notification
- Enhanced token storage with expiry information

**Security Benefits:**
- Consistent authentication state across application
- Automatic session management
- Clear separation of authentication logic

## 5. Automatic Session Management

### Location: `src/App.jsx`

**Features:**
- Periodic token expiry checking (every minute)
- Automatic cleanup when user logs out
- Integration with Redux authentication state

**Security Benefits:**
- Proactive session management
- Automatic logout on token expiry
- Consistent user experience

## Security Considerations

### Current Limitations

1. **localStorage Vulnerability**: Tokens are stored in localStorage, which is vulnerable to XSS attacks.

2. **Client-Side Token Management**: Token expiry is managed client-side, which can be manipulated.

### Production Recommendations

1. **Use httpOnly Cookies**: Store tokens in httpOnly cookies to prevent XSS access.
   ```javascript
   // Server should set httpOnly cookie
   Set-Cookie: authToken=...; HttpOnly; Secure; SameSite=Strict
   ```

2. **Implement Content Security Policy (CSP)**:
   ```html
   <meta http-equiv="Content-Security-Policy" 
         content="default-src 'self'; script-src 'self' 'unsafe-inline'">
   ```

3. **Use HTTPS Only**: Ensure all communication is encrypted.

4. **Implement Token Refresh**: Use short-lived access tokens with refresh tokens.

5. **Server-Side Session Validation**: Always validate tokens server-side.

6. **Rate Limiting**: Implement rate limiting on authentication endpoints.

## Implementation Status

✅ **Completed:**
- Enhanced token management with expiry
- Centralized error handling
- API request security layer
- Automatic session management
- Redux authentication state management

🔄 **In Progress:**
- Integration across all components
- Testing and validation

📋 **Future Enhancements:**
- httpOnly cookie implementation
- Token refresh mechanism
- Enhanced CSP headers
- Security audit and penetration testing

## Testing Security Features

### Token Expiry Testing
1. Login to application
2. Wait for token expiry (or manually expire in localStorage)
3. Attempt to make API request
4. Verify automatic logout and redirect to login

### Error Handling Testing
1. Trigger various API errors (network, 401, 403, 500)
2. Verify user-friendly messages are displayed
3. Check that sensitive information is not exposed
4. Verify proper logging in development console

### Session Management Testing
1. Login and verify periodic token checking
2. Manually expire token and verify automatic logout
3. Test multiple tabs/windows for consistent behavior

## Security Monitoring

### Recommended Monitoring
1. **Authentication Failures**: Monitor failed login attempts
2. **Token Expiry Events**: Track token expiry patterns
3. **API Error Rates**: Monitor for unusual error patterns
4. **Session Duration**: Track average session lengths

### Logging
- Error logging is enabled in development mode only
- Production logging should be implemented server-side
- Avoid logging sensitive information (tokens, passwords)

## Contact

For security concerns or questions about this implementation, please contact the development team.