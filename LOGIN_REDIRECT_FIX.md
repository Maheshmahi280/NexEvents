# Login/Registration Redirect Fix

## Problem Identified
The login and registration redirects were not working correctly because there were two competing functions handling form submissions:

1. **login.html** - Had an inline script with `loginUser()` function that correctly redirects based on user role
2. **auth.js** - Had a `handleLoginSubmit()` function that was hijacking the form submission and always redirecting to `/` (home page) instead of checking the user's role

## Root Cause
The `auth.js` file was binding a listener to the login form that would intercept the submit event before the inline script could execute. The `handleLoginSubmit()` function:
- Correctly fetched the login API
- Correctly stored the tokens
- **But incorrectly redirected to `/` instead of using the role-based routing**

## Files Modified

### 1. **d:\Hackrivals\backend\static\js\auth.js**

**Change in `handleLoginSubmit()` function (lines 139-152):**
- Was redirecting all users to `/` (home page)
- **Now redirects based on user role:**
  - `Seeker` role → `/seeker-dashboard`
  - `Organizer` role → `/organizer-dashboard`
  - Unknown role → `/` (fallback)

**Change in `handleRegisterSubmit()` function (lines ~290-350):**
- Was redirecting to `/login` after registration
- **Now:**
  - Extracts the selected role from radio buttons
  - Passes role to `registerUser()` function
  - Redirects based on role to the appropriate dashboard
  - Added firstName and lastName extraction

### 2. **d:\Hackrivals\backend\static\js\api.js**

**Updated `registerUser()` function (line 323):**
```javascript
// Before:
async function registerUser(username, email, password) {
    return apiPost('register/', {
        username: username,
        email: email,
        password: password,
    });
}

// After:
async function registerUser(username, email, password, firstName = '', lastName = '', role = 'Seeker') {
    return apiPost('register/', {
        username: username,
        email: email,
        password: password,
        first_name: firstName,
        last_name: lastName,
        role: role,
    });
}
```

## What Now Happens

### Login Flow
1. User enters credentials and submits form
2. `handleLoginSubmit()` in auth.js processes the submission
3. Fetches `/api/login/` endpoint
4. Receives response with `access_token`, `refresh_token`, and **`role`**
5. Stores all three in localStorage
6. **Checks the user's role:**
   - If role is "Seeker" → Redirects to `/seeker-dashboard`
   - If role is "Organizer" → Redirects to `/organizer-dashboard`
   - Otherwise → Redirects to home `/`
7. Login successful! ✅

### Registration Flow
1. User fills form (firstName, lastName, username, email, password, selects role)
2. `handleRegisterSubmit()` in auth.js processes the submission
3. Extracts the selected role from radio buttons
4. Fetches `/api/register/` with all data including role
5. Receives response with tokens and role
6. Stores tokens and role in localStorage
7. **Checks the user's role:**
   - If role is "Seeker" → Redirects to `/seeker-dashboard`
   - If role is "Organizer" → Redirects to `/organizer-dashboard`
   - Otherwise → Redirects to home `/`
8. Registration successful with immediate redirect to dashboard! ✅

## Testing
To test the fix:

1. **New Seeker Account:**
   - Go to `/register`
   - Fill form with role "🎫 Attending" (Seeker)
   - Should redirect to `/seeker-dashboard`

2. **New Organizer Account:**
   - Go to `/register`
   - Fill form with role "📋 Organizing" (Organizer)
   - Should redirect to `/organizer-dashboard`

3. **Login as Seeker:**
   - Go to `/login`
   - Login with a Seeker account
   - Should redirect to `/seeker-dashboard`

4. **Login as Organizer:**
   - Go to `/login`
   - Login with an Organizer account
   - Should redirect to `/organizer-dashboard`

## Benefits
✅ Proper role-based routing for all users
✅ Immediate access to correct dashboard after login/registration
✅ Tokens stored securely in localStorage
✅ Role information available for JavaScript features
✅ Clear console logging for debugging (if needed)

## Browser Console Output (Debugging)
When logging in, you should see messages like:
```
[LOGIN] Submitting login form...
[LOGIN] Sending credentials to server...
[LOGIN] Server response received
[LOGIN] Tokens stored successfully
[LOGIN] User role: Seeker
[LOGIN] Redirecting to seeker dashboard...
```
