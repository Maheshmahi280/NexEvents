# Testing Guide: Login and Registration Redirect Fix

## Server Status
✅ Django development server is running on `http://localhost:8000`

## What Was Fixed

### The Issue
When you logged in, the JavaScript was redirecting you to the home page (`/`) instead of your role-based dashboard:
- Seeker users should go to `/seeker-dashboard`
- Organizer users should go to `/organizer-dashboard`

### Root Cause
The `handleLoginSubmit()` function in `static/js/auth.js` was hardcoded to redirect all users to home (`/`), ignoring the role returned from the API.

### The Solution
We updated the redirect logic in `auth.js` to:
1. Extract the `role` from the API response
2. Check if the role is "Seeker" or "Organizer"
3. Redirect to the appropriate dashboard accordingly

## How to Test

### Step 1: Clear Your Browser Cache
Since we modified JavaScript files, clear your browser cache to ensure you get the latest version:
- **Windows:** Press `Ctrl + Shift + Delete`
- Select "Cached images and files" or "All time"
- Click "Clear data"

### Step 2: Hard Refresh the Browser
- Press `Ctrl + Shift + R` (or `Cmd + Shift + R` on Mac)
- This ensures you get the latest JavaScript files

### Step 3: Test New Registration (Seeker)
1. Navigate to `http://localhost:8000/register`
2. Fill out the form:
   - **First Name:** John
   - **Last Name:** Seeker
   - **Username:** johnseeker
   - **Email:** johnseeker@example.com
   - **Password:** securepass123
   - **Confirm Password:** securepass123
   - **Role:** Select "🎫 Attending" (Seeker)
3. Click "Create Account"
4. **Expected Result:** You should see "Account created successfully! Redirecting..."
5. **You should be redirected to `/seeker-dashboard`** ✅

### Step 4: Test New Registration (Organizer)
1. Navigate to `http://localhost:8000/register`
2. Fill out the form:
   - **First Name:** Jane
   - **Last Name:** Organizer
   - **Username:** janeorg
   - **Email:** janeorg@example.com
   - **Password:** securepass123
   - **Confirm Password:** securepass123
   - **Role:** Select "📋 Organizing" (Organizer)
3. Click "Create Account"
4. **Expected Result:** You should see "Account created successfully! Redirecting..."
5. **You should be redirected to `/organizer-dashboard`** ✅

### Step 5: Test Login (Seeker)
1. Navigate to `http://localhost:8000/login`
2. Log in with the Seeker account:
   - **Username:** johnseeker
   - **Password:** securepass123
3. Click "Sign In"
4. **Expected Result:** You should see "Login successful! Redirecting..."
5. **You should be redirected to `/seeker-dashboard`** ✅

### Step 6: Test Login (Organizer)
1. Navigate to `http://localhost:8000/login`
2. Log in with the Organizer account:
   - **Username:** janeorg
   - **Password:** securepass123
3. Click "Sign In"
4. **Expected Result:** You should see "Login successful! Redirecting..."
5. **You should be redirected to `/organizer-dashboard`** ✅

## Debugging

### If Redirect Still Doesn't Work

#### Option 1: Check Browser Console
1. Press `F12` to open Developer Tools
2. Go to the "Console" tab
3. You should see messages like:
   ```
   [LOGIN] Submitting login form...
   [LOGIN] Sending credentials to server...
   [LOGIN] Server response received
   [LOGIN] Tokens stored successfully
   [LOGIN] User role: Seeker
   [LOGIN] Redirecting to seeker dashboard...
   ```

#### Option 2: Check Network Tab
1. Press `F12` to open Developer Tools
2. Go to the "Network" tab
3. Refresh the page
4. Look for a POST request to `/api/login/`
5. Click on it and check the Response tab
6. You should see JSON with fields:
   - `access` (JWT token)
   - `refresh` (JWT token)
   - `role` (should be "Seeker" or "Organizer")

#### Option 3: Clear Everything and Retry
If issues persist:
1. Clear localStorage: Press F12 → Console → Type: `localStorage.clear()`
2. Clear browser cache: `Ctrl + Shift + Delete`
3. Close all browser tabs
4. Close the browser completely
5. Restart the browser
6. Navigate to `http://localhost:8000/login`
7. Try again

### Common Issues and Solutions

**Issue:** "Login failed. Please try again."
- **Solution:** Check that your Django server is running (you should see output in the terminal)
- **Solution:** Clear localStorage first: `localStorage.clear()` in console

**Issue:** Redirect to home page instead of dashboard
- **Solution:** This means the API is not returning a role. Check Network tab in DevTools
- **Solution:** Ensure the API is returning `{"access": "...", "refresh": "...", "role": "Seeker"}`

**Issue:** Getting 404 errors in Network tab
- **Solution:** Make sure the backend server is running
- **Solution:** Check that all routes are configured correctly in `backend/urls.py`

**Issue:** CSS not loading on dashboard
- **Solution:** This was fixed previously. Run `Ctrl + Shift + R` to hard refresh
- **Solution:** Clear browser cache completely

## Files Modified

### 1. `static/js/auth.js`
- Updated `handleLoginSubmit()` to redirect based on user role
- Updated `handleRegisterSubmit()` to handle role selection and redirect accordingly
- Added extraction of firstName and lastName fields

### 2. `static/js/api.js`
- Updated `registerUser()` function to accept and pass firstName, lastName, and role parameters

## Expected Behavior After Fix

```
User Registration Flow:
┌─────────────────────────┐
│ User fills registration │
│ form with role selected │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Form submitted to API   │
│ POST /api/register/     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ API returns tokens      │
│ + role (Seeker/Org)     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Store tokens in storage │
│ Extract role from resp  │
└────────────┬────────────┘
             │
             ▼
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌────────────┐  ┌────────────────┐
│ Role =     │  │ Role =         │
│ Seeker?    │  │ Organizer?     │
└─────┬──────┘  └────────┬───────┘
      │                  │
      ▼                  ▼
┌──────────────────┐  ┌──────────────────────┐
│ Redirect to      │  │ Redirect to          │
│ /seeker-dash     │  │ /organizer-dashboard │
│ board ✅         │  │ ✅                   │
└──────────────────┘  └──────────────────────┘
```

## Success Indicators

You'll know the fix is working when:
1. ✅ After login, you see the success message briefly
2. ✅ You are redirected to the correct dashboard for your role
3. ✅ The dashboard loads with all CSS styling intact
4. ✅ You can see your role-specific content
5. ✅ Browser console shows debug messages (no errors)
6. ✅ Network tab shows `/api/login/` returning 200 OK with role in response

## Next Steps

Once testing is complete:
1. Test all CRUD operations on the dashboards
2. Test that Seekers can see events and RSVP
3. Test that Organizers can create and manage events
4. Test logout functionality
5. Consider deploying to production

---

**Need Help?** Check the [LOGIN_REDIRECT_FIX.md](LOGIN_REDIRECT_FIX.md) for technical details about the changes.
