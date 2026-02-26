/**
 * Browser Console Debug Script for Authentication Issues
 * 
 * HOW TO USE:
 * 1. Open your browser DevTools (F12)
 * 2. Go to the Console tab
 * 3. Copy and paste this entire script
 * 4. Press Enter
 * 5. Follow the instructions shown
 */

(function() {
  const API_BASE = 'http://localhost:8000';
  const TOKEN_KEY = 'token';

  console.log('%c=== AUTHENTICATION DEBUG TOOL ===', 'font-size: 16px; font-weight: bold; color: #007bff;');
  console.log('');

  // Check 1: Token in localStorage
  console.log('%c[1] Checking localStorage...', 'font-weight: bold;');
  const token = localStorage.getItem(TOKEN_KEY);
  
  if (!token) {
    console.error('❌ No token found in localStorage');
    console.log('💡 Solution: Login first at http://localhost:3000/auth/login');
  } else {
    console.log('✅ Token found in localStorage');
    console.log('   Length:', token.length, 'characters');
    console.log('   Starts with:', token.substring(0, 30) + '...');
    
    // Decode JWT payload
    try {
      const parts = token.split('.');
      if (parts.length === 3) {
        const payload = JSON.parse(atob(parts[1]));
        console.log('');
        console.log('%c[2] Token Contents:', 'font-weight: bold;');
        console.log('   Email (sub):', payload.sub || 'N/A');
        console.log('   Expires:', payload.exp ? new Date(payload.exp * 1000).toLocaleString() : 'N/A');
        
        const isExpired = payload.exp && payload.exp < Date.now() / 1000;
        if (isExpired) {
          console.error('   Status: ❌ EXPIRED');
          console.log('💡 Solution: Login again to get a fresh token');
        } else {
          console.log('   Status: ✅ Valid');
        }
      }
    } catch (e) {
      console.error('❌ Could not decode JWT:', e.message);
    }
  }
  
  console.log('');
  
  // Check 2: Test API directly
  console.log('%c[3] Testing API directly...', 'font-weight: bold;');
  
  if (!token) {
    console.log('⚠️  Skipping API test - no token available');
  } else {
    console.log('   Sending test request to GET /tasks...');
    
    fetch(`${API_BASE}/tasks`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })
    .then(response => {
      console.log('');
      console.log('%c[4] API Response:', 'font-weight: bold;');
      console.log('   Status:', response.status, response.ok ? '✅' : '❌');
      
      if (response.ok) {
        return response.json();
      } else {
        return response.json().then(data => {
          console.error('   Error:', data);
          throw new Error(data.detail || 'API request failed');
        });
      }
    })
    .then(data => {
      console.log('   Tasks found:', data.length);
      console.log('');
      console.log('%c=== DIAGNOSIS ===', 'font-size: 16px; font-weight: bold;');
      console.log('');
      console.log('✅ Backend is working correctly');
      console.log('✅ Token is valid');
      console.log('');
      console.log('⚠️  If you still see 401 in your app, the issue is:');
      console.log('   - Axios interceptor not attaching the header');
      console.log('   - Request being made before token is set');
      console.log('   - Different localStorage key being used');
      console.log('');
      console.log('💡 Next steps:');
      console.log('   1. Check browser Network tab for the failing request');
      console.log('   2. Verify Authorization header is present in request');
      console.log('   3. Check console for [API Client] logs');
    })
    .catch(error => {
      console.log('');
      console.log('%c=== DIAGNOSIS ===', 'font-size: 16px; font-weight: bold;');
      console.log('');
      console.error('❌ API request failed:', error.message);
      console.log('');
      console.log('💡 Possible causes:');
      console.log('   - Backend server not running');
      console.log('   - Wrong backend URL');
      console.log('   - Token is invalid/expired');
    });
  }
  
  // Helper functions you can call manually
  console.log('');
  console.log('%c=== HELPER FUNCTIONS ===', 'font-weight: bold;');
  console.log('Run these commands manually:');
  console.log('');
  console.log('  window.authDebug.getToken()     - Get current token');
  console.log('  window.authDebug.clearToken()   - Remove token');
  console.log('  window.authDebug.testLogin()    - Test login API');
  console.log('  window.authDebug.testCreate()   - Test create task');
  console.log('');
  
  // Expose helper functions
  window.authDebug = {
    getToken: () => {
      const t = localStorage.getItem(TOKEN_KEY);
      console.log('Token:', t ? t.substring(0, 50) + '...' : 'null');
      return t;
    },
    
    clearToken: () => {
      localStorage.removeItem(TOKEN_KEY);
      console.log('✅ Token cleared');
    },
    
    testLogin: async () => {
      console.log('Testing login...');
      try {
        const response = await fetch(`${API_BASE}/auth/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'testpassword123'
          }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
          console.log('✅ Login successful');
          localStorage.setItem(TOKEN_KEY, data.access_token);
          console.log('✅ Token saved to localStorage');
        } else {
          console.error('❌ Login failed:', data);
        }
      } catch (error) {
        console.error('❌ Login error:', error.message);
      }
    },
    
    testCreate: async () => {
      const t = localStorage.getItem(TOKEN_KEY);
      if (!t) {
        console.error('❌ No token. Run testLogin() first');
        return;
      }
      
      console.log('Testing create task...');
      try {
        const response = await fetch(`${API_BASE}/tasks`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${t}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: `Test task ${new Date().toLocaleTimeString()}`,
            description: 'Created from console debug script',
            priority: 'medium',
          }),
        });
        
        const data = await response.json();
        
        if (response.ok || response.status === 200) {
          console.log('✅ Task created successfully! ID:', data.id);
        } else {
          console.error('❌ Create failed:', data);
        }
      } catch (error) {
        console.error('❌ Create error:', error.message);
      }
    },
  };
  
})();
