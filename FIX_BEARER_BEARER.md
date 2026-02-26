# Fix: "Bearer Bearer" Double Prefix & Missing Authorization Header

## Problem Summary

Backend logs showed three types of requests:

1. ✅ **Working**: `Authorization header: Bearer eyJhbGci...` → 200 OK
2. ❌ **Double Prefix**: `Authorization header: Bearer Bearer eyJhbGci...` → 401 Unauthorized
3. ❌ **Missing Header**: `Authorization header: None...` → 401 Unauthorized

This caused:
- `JWTError: Not enough segments` (from "Bearer Bearer" token)
- `401 Unauthorized` errors on protected endpoints

---

## Root Cause Analysis

### Cause 1: Double "Bearer" Prefix

**Problem**: Token was being prefixed with "Bearer " TWICE:

1. **First**: Manually in component code
   ```typescript
   // ❌ WRONG: Manual header in dashboard/page.tsx and chat/page.tsx
   await aiAgentClient.post("/chat", { message }, {
     headers: { Authorization: `Bearer ${token}` }
   });
   ```

2. **Second**: Axios interceptor automatically adds it
   ```typescript
   // api-client.ts interceptor ALWAYS adds "Bearer " prefix
   config.headers.Authorization = `Bearer ${token}`;
   ```

**Result**: `Authorization: Bearer Bearer eyJhbGci...`

### Cause 2: Token Stored with "Bearer" Prefix

**Problem**: Login was storing the token with "Bearer " prefix:
```typescript
// ❌ WRONG: Storing potentially prefixed token
localStorage.setItem('token', response.data.access_token);
```

If `response.data.access_token` ever contained "Bearer " (from a bug or manual test), 
then the interceptor would add ANOTHER "Bearer ", creating "Bearer Bearer".

### Cause 3: Missing Authorization Header

**Problem**: When `localStorage.getItem('token')` returned `null`, the interceptor 
didn't initialize `config.headers`, causing the header to be undefined.

---

## Fixes Applied

### Fix 1: Axios Interceptor (`frontend/app/api-client.ts`)

**Changes**:
1. Strip any existing "Bearer " prefix from token before adding it
2. Always initialize `config.headers` object
3. Don't log warnings for public endpoints (/auth/login, /auth/register)

```typescript
const addAuthHeader = (config: any) => {
  if (typeof window === 'undefined') return config;

  const token = localStorage.getItem('token');
  
  // Always initialize headers
  config.headers = config.headers || {};

  if (token) {
    // CRITICAL: Strip any existing "Bearer " prefix
    const cleanToken = token.replace(/^Bearer\s+/i, '').trim();
    
    // Set Authorization with clean token
    config.headers.Authorization = `Bearer ${cleanToken}`;
    config.headers['Content-Type'] = 'application/json';
  } else {
    // Still set Content-Type for public endpoints
    config.headers['Content-Type'] = 'application/json';
  }

  return config;
};
```

### Fix 2: Login Page (`frontend/app/auth/login/page.tsx`)

**Changes**: Store ONLY the raw JWT token, strip any "Bearer " prefix:

```typescript
const rawToken = response.data.access_token.trim();
const cleanToken = rawToken.replace(/^Bearer\s+/i, '');
localStorage.setItem('token', cleanToken);
```

### Fix 3: Signup Page (`frontend/app/auth/signup/page.tsx`)

**Changes**: Same as login - store clean token:

```typescript
const rawToken = loginResponse.data.access_token.trim();
const cleanToken = rawToken.replace(/^Bearer\s+/i, '');
localStorage.setItem('token', cleanToken);
```

### Fix 4: Dashboard Page (`frontend/app/dashboard/page.tsx`)

**Changes**: Remove manual Authorization header - let interceptor handle it:

```typescript
// ❌ BEFORE (WRONG)
const token = localStorage.getItem("token");
const response = await aiAgentClient.post(
  "/chat",
  { message: inputMessage },
  {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  },
);

// ✅ AFTER (CORRECT)
const response = await aiAgentClient.post(
  "/chat",
  { message: inputMessage },
);
// Interceptor automatically adds Authorization header
```

### Fix 5: Chat Page (`frontend/app/chat/page.tsx`)

**Changes**: Same as dashboard - remove manual header:

```typescript
// ✅ CORRECT: Let interceptor handle authentication
const response = await aiAgentClient.post(
  "/chat",
  { message: inputMessage },
);
```

---

## Why "Not Enough Segments" JWT Error Happens

JWT tokens have 3 parts separated by dots: `header.payload.signature`

Example: `eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.abc123`

When you send `Bearer Bearer eyJhbGci...`:

1. Backend extracts token after "Bearer " → gets `Bearer eyJhbGci...`
2. JWT library tries to decode `Bearer eyJhbGci...`
3. Splits by `.` → only finds 2 segments (or malformed)
4. Throws: `JWTError: Not enough segments`

**Correct flow**:
1. Send: `Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.abc123`
2. Backend extracts: `eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0In0.abc123`
3. JWT decodes 3 segments successfully ✓

---

## Testing the Fix

### 1. Clear Old Token

In browser console:
```javascript
localStorage.clear();
console.log('Storage cleared');
```

### 2. Fresh Login

1. Go to http://localhost:3000/auth/login
2. Login with credentials
3. Check console for: `[Login] Token saved successfully, length: XXX`

### 3. Verify Token Format

In browser console:
```javascript
const token = localStorage.getItem('token');
console.log('Token starts with "Bearer ":', token.startsWith('Bearer '));
// Should print: false
console.log('Token looks like JWT:', token.startsWith('eyJ'));
// Should print: true
```

### 4. Create Task

1. Go to dashboard
2. Create a task
3. Check console for:
   ```
   [API Client] Request to: /tasks
   [API Client] Token present: true
   [API Client] Authorization header set: Bearer eyJhbGci...
   ```

### 5. Check Backend Logs

Should see:
```
DEBUG:dependencies:Authorization header: Bearer eyJhbGci...
DEBUG:security:Token decoded successfully, email: test@example.com
DEBUG:dependencies:User authenticated successfully: test@example.com
```

Should NOT see:
```
❌ Authorization header: Bearer Bearer...
❌ JWT error: Not enough segments
```

---

## Files Modified

| File | Change |
|------|--------|
| `frontend/app/api-client.ts` | Strip "Bearer " prefix, always init headers |
| `frontend/app/auth/login/page.tsx` | Store clean token only |
| `frontend/app/auth/signup/page.tsx` | Store clean token only |
| `frontend/app/dashboard/page.tsx` | Remove manual Authorization header |
| `frontend/app/chat/page.tsx` | Remove manual Authorization header |

---

## Production Checklist

- [ ] Clear all existing tokens in browser storage
- [ ] Users must login again after deploy
- [ ] Verify no code manually sets "Bearer " prefix
- [ ] All API calls use axios instances with interceptor
- [ ] Backend logs show clean "Bearer " prefix (not double)

---

## Prevention

To prevent this bug in the future:

1. **NEVER** manually set `Authorization` header when using axios
2. **ALWAYS** let the interceptor handle authentication
3. **STORE** only the raw JWT token (no "Bearer " prefix)
4. **USE** `apiClient` or `aiAgentClient` for all API calls

### Correct Pattern

```typescript
// ✅ CORRECT: Use axios instance, let interceptor handle auth
await apiClient.post('/tasks', { title: 'New Task' });

// ✅ CORRECT: If you MUST set custom headers, don't include Authorization
await apiClient.post('/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});

// ❌ WRONG: Manual Authorization header
await apiClient.post('/tasks', data, {
  headers: { Authorization: `Bearer ${token}` }
});
```

---

## Summary

**Problem**: Double "Bearer " prefix and missing headers caused 401 errors

**Root Cause**: 
- Manual headers + interceptor = double prefix
- Token stored with "Bearer " prefix
- Headers not initialized when token missing

**Solution**:
- Strip "Bearer " prefix in interceptor
- Store only raw JWT token
- Remove manual Authorization headers
- Always initialize headers object

**Result**: Consistent, working authentication across all endpoints
