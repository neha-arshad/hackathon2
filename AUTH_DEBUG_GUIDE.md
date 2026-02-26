# Authentication Debug Guide

## Problem Summary

You're getting `401 Unauthorized` when creating tasks, even though:
- ✅ Backend is working correctly
- ✅ Login returns valid JWT token
- ✅ `/tasks` endpoint works with manual token testing

## Root Cause

The issue is in **how the frontend sends the Authorization header**. The axios interceptor may not be properly attaching the token to requests.

---

## Quick Fix Applied

### Changes Made to `frontend/app/api-client.ts`:

1. **Removed default headers from axios.create()** - These can interfere with interceptor header merging
2. **Explicit header initialization** in interceptor: `config.headers = config.headers || {}`
3. **Set both Authorization AND Content-Type** in the interceptor
4. **Added comprehensive debug logging** to track token flow

---

## Step-by-Step Debugging

### Step 1: Verify Token Storage

1. Open your app at `http://localhost:3000`
2. Login with your credentials
3. Open DevTools (F12) → Console
4. Run:
   ```javascript
   localStorage.getItem('token')
   ```
5. **Expected:** You should see a JWT token (starts with `eyJ...`)
6. **If null:** Login isn't saving the token correctly

### Step 2: Check Console Logs

After logging in, try to create a task and look for these logs:

```
[API Client] Request to: /tasks
[API Client] Token present: true
[API Client] Token length: 139
[API Client] Authorization header set: Bearer eyJhbGciOiJIUzI1...
```

**If you DON'T see these logs:**
- The interceptor isn't running
- Check if `api-client.ts` is being imported correctly

**If you see "Token present: false":**
- Token wasn't saved during login
- Check login page flow

### Step 3: Check Network Tab

1. Open DevTools → Network tab
2. Clear existing logs
3. Try to create a task
4. Click on the `tasks` request
5. Check **Request Headers**:

**Look for:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json
```

**If Authorization header is MISSING:**
- Interceptor isn't attaching the header
- This is the bug we fixed

**If Authorization header is PRESENT but still 401:**
- Token might be expired
- Token might be malformed
- Backend might have different SECRET_KEY

### Step 4: Use the Debug Script

1. Open `frontend/auth-debug-console.js`
2. Copy the entire contents
3. Paste into browser console on your app
4. Follow the diagnostic output

The script will:
- Check if token exists
- Decode and validate the JWT
- Test the API directly
- Tell you exactly what's wrong

### Step 5: Manual API Test

In the console, run:
```javascript
// Get token
const token = localStorage.getItem('token');
console.log('Token:', token?.substring(0, 30) + '...');

// Test API
fetch('http://localhost:8000/tasks', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
})
.then(r => r.json())
.then(console.log);
```

**If this works:** Backend is fine, issue is in axios
**If this fails:** Token is invalid or backend issue

---

## Common Issues & Solutions

### Issue 1: Token Not Saved After Login

**Symptom:** `localStorage.getItem('token')` returns `null` after login

**Check:** Login page is using correct key:
```typescript
// In login handler
localStorage.setItem('token', response.data.access_token);
```

**Fix:** Make sure you're not using a different key like `'authToken'` or `'jwt'`

---

### Issue 2: Interceptor Not Running

**Symptom:** No `[API Client]` logs in console

**Possible causes:**
1. Using Server Component instead of Client Component
2. Axios instance not imported correctly
3. Interceptor registration failed

**Fix:** Ensure page has `'use client'` directive:
```typescript
'use client'  // Must be first line

import { apiClient } from '../api-client';
```

---

### Issue 3: Wrong Backend URL

**Symptom:** Network error or 404 instead of 401

**Check:** `frontend/app/api.config.ts`:
```typescript
export const API_BASE_URL = 'http://localhost:8000';
```

**Verify backend is running:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

---

### Issue 4: Token Expired

**Symptom:** Gets 401 with "Token has expired"

**Check token expiration in console:**
```javascript
const token = localStorage.getItem('token');
const payload = JSON.parse(atob(token.split('.')[1]));
console.log('Expires:', new Date(payload.exp * 1000));
console.log('Expired:', payload.exp < Date.now() / 1000);
```

**Fix:** Login again to get fresh token (default: 30 min expiry)

---

### Issue 5: Header Case Sensitivity

**Symptom:** Header present but backend doesn't see it

Axios normalizes headers to lowercase. Backend should handle this, but verify:

**Backend (FastAPI) handles both cases:**
```python
authorization = request.headers.get("authorization")  # lowercase
# OR
authorization = request.headers.get("Authorization")  # capitalized
```

Our backend already handles this correctly.

---

## Testing the Fix

### 1. Restart Frontend Development Server

```bash
cd E:\hackathon2\frontend
npm run dev
```

### 2. Clear Browser Cache & Storage

1. DevTools → Application → Storage
2. Click "Clear site data"
3. Or use Ctrl+Shift+Delete

### 3. Fresh Login

1. Go to `http://localhost:3000/auth/login`
2. Login with credentials
3. Check console for `[API Client]` logs

### 4. Create Task

1. Go to dashboard
2. Create a new task
3. Check Network tab for Authorization header

---

## Expected Flow

```
1. User enters credentials
   ↓
2. POST /auth/login
   ↓
3. Backend returns: { access_token: "eyJ...", token_type: "bearer" }
   ↓
4. Frontend saves: localStorage.setItem('token', access_token)
   ↓
5. User creates task
   ↓
6. Axios interceptor runs:
   - Gets token from localStorage
   - Sets: headers.Authorization = `Bearer ${token}`
   ↓
7. POST /tasks with Authorization header
   ↓
8. Backend validates token → 200 OK
```

---

## Files Modified

| File | Change |
|------|--------|
| `frontend/app/api-client.ts` | Fixed header initialization, added debug logs |
| `frontend/app/hooks/useAuth.ts` | Created auth hook for better token management |
| `frontend/app/lib/api.ts` | Created utility functions for explicit header control |
| `frontend/auth-debug-console.js` | Created debug script for browser console |

---

## Production Checklist

- [ ] Token stored with correct key (`'token'`)
- [ ] Interceptor logs show token being attached
- [ ] Network tab shows `Authorization: Bearer ...` header
- [ ] Backend returns 200 for authenticated requests
- [ ] 401 responses clear token and redirect to login
- [ ] Token expiration is handled gracefully

---

## Still Having Issues?

Run this in console and share the output:

```javascript
console.log('Token exists:', !!localStorage.getItem('token'));
console.log('API URL:', process.env.NEXT_PUBLIC_API_BASE_URL);
console.log('Axios version:', require('axios/package.json').version);
```

Then check:
1. Backend logs for authentication attempts
2. Browser console for `[API Client]` logs
3. Network tab for exact request headers
