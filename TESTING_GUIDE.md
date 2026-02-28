# Error Handling & Validation - Quick Test Guide

**Quick Reference for Testing All Improvements**

---

## 🚀 Server Status

Run the development server:
```powershell
cd d:\Hackrivals\backend
python manage.py runserver
# Access at http://127.0.0.1:8000
```

---

## ✅ Test Cases (Copy-Paste Ready)

### 1️⃣ Invalid Form - Description Over 500 Characters

**How to Test:**
1. Go to `/create-event`
2. Fill out form with:
   - Name: "Test Event"
   - Description: Copy this 550-character text:
     ```
     Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
     Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
     Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris 
     nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in 
     reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla 
     pariatur. Excepteur sint occaecat cupidatat non proident, sunt in 
     culpa qui officia deserunt mollit anim id est laborum exercitation.
     ```
   - Date: Tomorrow's date
   - Time: 2:00 PM
   - Location: "Virtual"
   - Category: "Tech"

**Expected Result:**
- ❌ Character counter shows "550 / 500" in RED
- ❌ Submit fails with: "Description must be at most 500 characters"
- ❌ Error message appears below description field

---

### 2️⃣ Empty Dashboard (No Events Created)

**How to Test:**
1. Create a new account or login with a user who hasn't created events
2. Go to `/dashboard`
3. Click "My Events" tab (should already be selected)

**Expected Result:**
- ✅ Shows: "You haven't created any events yet"
- ✅ Displays "Create Event" button
- ✅ Button takes you to `/create-event`

---

### 3️⃣ Empty Search Results

**How to Test:**
1. Go to home page
2. In the search box, type: `xyzabc123notfound`
3. Press Enter or wait for debounce

**Expected Result:**
- ✅ Shows: "No events found for 'xyzabc123notfound'"
- ✅ Shows: "Try different keywords or browse all events"
- ✅ Helpful text instead of error

---

### 4️⃣ Expired Token / Unauthorized Access

**How to Test:**
1. Create account and login
2. Go to `/dashboard`
3. Open browser DevTools (F12)
4. Go to Application/Storage → LocalStorage → check `access_token`
5. Edit the token:
   - Change last few characters to garbage
   - Save to LocalStorage
6. Click "My Events" → Try to delete an event (or refresh page)

**Expected Result:**
- ✅ Detects 401 error
- ✅ Browser shows: "Your session has expired. Please login again."
- ✅ Has clickable login link
- ✅ Console shows: `[TOKEN] Attempting token refresh...` then fails
- ✅ Redirects to login or shows message

---

### 5️⃣ Permission Denied / Forbidden (403)

**How to Test:**
1. User A creates an event
2. Login as User B
3. Use browser DevTools to get User A's event ID
4. Open console and run:
   ```javascript
   fetch('/api/events/1/delete/', {
     method: 'DELETE',
     headers: {'Authorization': 'Bearer YOUR_TOKEN'}
   }).then(r => r.json()).then(d => console.log(d))
   ```

**Expected Result:**
- ✅ HTTP Response: `403 Forbidden`
- ✅ Error message: "You can only delete events you created"
- ✅ Console logs the detailed error

---

### 6️⃣ Form Validation - All Fields

**How to Test - Each Field:**

```
Test Username (too short):
- Input: "ab"
- Expected: "Username must be at least 3 characters"

Test Email (invalid):
- Input: "notanemail"
- Expected: "Please enter a valid email address"

Test Password (too short):
- Input: "12345"
- Expected: "Password must be at least 6 characters"

Test Event Name (empty):
- Input: ""
- Expected: "Event name is required"

Test Description (too short):
- Input: "short"
- Expected: "Description must be at least 10 characters"

Test Location (empty):
- Input: ""
- Expected: "Location is required"

Test Category (none selected):
- Input: "--Select--"
- Expected: "Please select a category"

Test Date (past date):
- Input: Yesterday's date
- Expected: (HTML5 validation prevents selection)

Test Cover Image (invalid URL):
- Input: "not a url"
- Expected: (HTML5 URL validation)
```

---

### 7️⃣ Description Character Counter

**How to Test:**
1. Go to `/create-event`
2. Focus on Description field
3. Type characters one by one and watch counter

**Expected Behavior:**
- ✅ Counter shows "0 / 500" initially
- ✅ Updates as you type: "25 / 500"
- ✅ At 450+ chars: Counter turns YELLOW (warning)
- ✅ At 500+ chars: Counter turns RED (error)
- ✅ Input is maxlength="500" - can't exceed
- ✅ Warning disappears when under 450

---

### 8️⃣ Successful Event Creation

**How to Test:**
1. **Go to:** `/create-event`
2. **Fill form:**
   ```
   Name: "Amazing Tech Conference"
   Description: "Join us for a day of exciting tech talks, networking, and workshops. Learn from industry experts and connect with fellow tech enthusiasts."
   Date: Select any future date
   Time: 10:00 AM
   Location: "Convention Center, San Francisco"
   Category: "Tech"
   Cover Image: (leave blank or enter valid image URL)
   ```
3. **Click:** "Create Event"

**Expected Success:**
- ✅ Button shows "Creating..."
- ✅ Page shows: "✅ Event 'Amazing Tech Conference' created successfully"
- ✅ Redirects to `/dashboard` after 2 seconds
- ✅ New event appears in your events list

---

### 9️⃣ Unauthorized Request (No Token)

**How to Test:**
1. Go to DevTools Console
2. Run this command:
   ```javascript
   fetch('/api/events/my/', {
     method: 'GET',
     headers: {'Content-Type': 'application/json'}
   }).then(r => r.json()).then(data => console.log(data))
   ```

**Expected Result:**
- ✅ HTTP 401 Unauthorized
- ✅ Error message in response
- ❌ No user events returned
- ✅ Should have `detail` field in response

---

### 🔟 Network Error / Server Error

**How to Test:**
1. Stop the Django server
2. Try to load events on home page
3. Or try to create event

**Expected Result:**
- ✅ Shows: "Error loading events" or "Error creating event"
- ✅ Shows helper text: "Please try again or refresh the page"
- ✅ Has retry button (if implemented)
- ✅ User is not confused by technical errors

---

## 🧪 Automated Test Execution

### Test Invalid Inputs
```bash
# Run the included test deletion utility
cd d:\Hackrivals\backend
python test_deletion.py
```

### Django System Checks
```bash
python manage.py check
# Expected: "System check identified no issues"
```

---

## 📝 Common Test Combinations

### Scenario A: Fresh User Journey
1. Register new account
2. See empty dashboard
3. Click "Create Event"
4. Fill form successfully
5. See event in dashboard
6. Logout (token expires)
7. Try to access dashboard → session expired message

### Scenario B: Form Validation Complete
1. Go to create event
2. Leave all fields empty → submit → multiple errors
3. Fill name only → submit → multiple errors
4. Fill everything correctly → submit → success
5. Edit token → try to create → 401 → tries refresh → redirects

### Scenario C: Search Operations
1. Search "Tech" → shows results
2. Search "xyz" → "No events found"
3. Filter by "Arts" → shows arts events or empty
4. Search + filter → context-aware message

---

## 🎯 HTTP Status Codes Tested

Monitor the Network tab in DevTools to see:

| Code | When | Fix |
|------|------|-----|
| **200** | Successful GET | ✅ Normal |
| **201** | Event created | ✅ Redirect to dashboard |
| **400** | Form invalid | ❌ Show validation errors |
| **401** | Token expired | 🔄 Try refresh or re-login |
| **403** | No permission | ❌ Show permission error |
| **404** | Not found | ❌ Show "not found" message |
| **500** | Server error | ❌ Show "try again" message |

---

## 🔍 Browser Console Logs

Open DevTools Console (F12) and look for logs:

```
✅ User authentication working:
   [LOGIN] Submitting login form...
   [LOGIN] Tokens stored successfully
   Login successful! Redirecting...

✅ Event creation working:
   [CREATE] Submitting create event form...
   [CREATE] Event data: {...}
   [CREATE] Event created successfully

✅ Empty dashboard working:
   [LOAD] Loading user events...
   [LOAD] Successfully loaded 0 user events
   [LOAD] Events rendered successfully

✅ Token refresh working:
   [TOKEN] Unauthorized (401) - Token may be expired
   [TOKEN] Attempting token refresh...
   [TOKEN] Token refreshed successfully - retrying request
```

---

## ✨ What's Been Improved

### Backend Improvements
- ✅ Better error messages with character counts
- ✅ Proper HTTP status codes (400/401/403/404/500)
- ✅ Validation messages that help users fix issues
- ✅ Logging for debugging
- ✅ Empty state indicators

### Frontend Improvements
- ✅ Real-time character counter with warnings
- ✅ Field-specific error display
- ✅ Token expiration handling
- ✅ Context-aware empty state messages
- ✅ Permission denied messages
- ✅ Auto-retry on token refresh
- ✅ Better error recovery

### Form Improvements
- ✅ Create-event.html form with complete validation
- ✅ Live character counter for description
- ✅ Date picker with min date
- ✅ Clear field hints
- ✅ Success confirmation before redirect
- ✅ Responsive design

---

## 🎓 Key Features to Test

**Most Important:**
1. [ ] Description character limit (> 500)
2. [ ] Empty dashboard message
3. [ ] Empty search results
4. [ ] Token expiration handling
5. [ ] Permission denied (403)

**Secondary:**
6. [ ] Form validation on all fields
7. [ ] Character counter warnings
8. [ ] Success messages
9. [ ] Error recovery
10. [ ] Session redirect

---

## 💡 Pro Tips for Testing

- **Use multiple browsers** to test simultaneous users
- **Check DevTools Network tab** to see HTTP status codes
- **Check Console** for detailed logging
- **Test on mobile** to ensure responsive design
- **Clear localStorage** to test fresh login
- **Manipulate tokens** to test expiration handling
- **Stop server** to test error handling

---

## 📞 Troubleshooting

| Issue | Solution |
|-------|----------|
| Form not validating | Check browser console for JS errors |
| Token not refreshing | Verify refresh_token in localStorage |
| Empty state not showing | Check `is_empty` flag in API response |
| Session not expiring | Wait longer or manually edit token |
| Create event not working | Check form validation errors |

---

**Happy Testing! 🎉**

*All error handling, validation, and user feedback improvements are now live and ready to test.*
