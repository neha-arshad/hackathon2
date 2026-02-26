/**
 * Token Cleanup Script
 * 
 * Run this in your browser console ONCE to fix any corrupted tokens
 * 
 * HOW TO USE:
 * 1. Open your app at http://localhost:3000
 * 2. Press F12 to open DevTools
 * 3. Go to Console tab
 * 4. Copy and paste this entire script
 * 5. Press Enter
 * 6. Refresh the page
 */

(function cleanupTokens() {
  const TOKEN_KEY = 'token';
  
  console.log('=== TOKEN CLEANUP ===');
  
  const currentToken = localStorage.getItem(TOKEN_KEY);
  
  if (!currentToken) {
    console.log('No token found in localStorage - nothing to clean');
    console.log('You will need to login again');
    return;
  }
  
  console.log('Current token length:', currentToken.length);
  console.log('Current token starts with "Bearer ":', currentToken.startsWith('Bearer '));
  console.log('Current token starts with "eyJ":', currentToken.startsWith('eyJ'));
  
  // Strip any "Bearer " prefix
  const cleanToken = currentToken.replace(/^Bearer\s+/i, '').trim();
  
  console.log('Clean token length:', cleanToken.length);
  console.log('Clean token starts with "eyJ":', cleanToken.startsWith('eyJ'));
  
  // Validate it looks like a JWT
  const parts = cleanToken.split('.');
  if (parts.length !== 3) {
    console.error('ERROR: Token does not look like a valid JWT');
    console.error('Expected 3 parts separated by dots, found:', parts.length);
    console.error('Token will be removed - please login again');
    localStorage.removeItem(TOKEN_KEY);
    return;
  }
  
  // Try to decode the payload
  try {
    const payload = JSON.parse(atob(parts[1]));
    console.log('Token payload:', payload);
    console.log('Token email (sub):', payload.sub);
    console.log('Token expires:', payload.exp ? new Date(payload.exp * 1000).toLocaleString() : 'N/A');
    
    const isExpired = payload.exp && payload.exp < Date.now() / 1000;
    if (isExpired) {
      console.warn('Token is EXPIRED - will be removed');
      localStorage.removeItem(TOKEN_KEY);
      console.log('Please login again');
      return;
    }
  } catch (e) {
    console.error('ERROR: Could not decode JWT payload:', e.message);
    console.error('Token will be removed - please login again');
    localStorage.removeItem(TOKEN_KEY);
    return;
  }
  
  // Save the clean token
  localStorage.setItem(TOKEN_KEY, cleanToken);
  console.log('');
  console.log('✅ Token cleaned and saved successfully!');
  console.log('✅ You can now use the app normally');
  console.log('');
  console.log('Next steps:');
  console.log('1. Refresh the page (F5 or Ctrl+R)');
  console.log('2. Try creating a task');
  console.log('3. Check console for "[API Client] Authorization header set: Bearer ..."');
  
})();
