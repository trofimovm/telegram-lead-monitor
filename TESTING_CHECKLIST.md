# Manual Testing Checklist

This document provides a comprehensive manual testing checklist for Telegram Lead Monitor. Use this checklist before releasing to production or after major updates.

## Testing Environment Setup

- [ ] Backend is running on http://localhost:8000
- [ ] Frontend is running on http://localhost:3000
- [ ] PostgreSQL database is accessible
- [ ] Redis is running
- [ ] You have test Telegram account credentials
- [ ] You have test email account for notifications

---

## 1. Authentication & User Management

### Registration

- [ ] **Test Case 1.1**: Register with valid data
  - Navigate to `/auth/register`
  - Fill in: email, password, full name, tenant name
  - Submit form
  - **Expected**: User created, redirected to login

- [ ] **Test Case 1.2**: Register with existing email
  - Try to register with already used email
  - **Expected**: Error message "Email already registered"

- [ ] **Test Case 1.3**: Register with invalid email
  - Try email like "invalid-email"
  - **Expected**: Validation error

- [ ] **Test Case 1.4**: Register with weak password
  - Try password < 8 characters
  - **Expected**: Validation error

### Login

- [ ] **Test Case 2.1**: Login with correct credentials
  - Navigate to `/auth/login`
  - Enter valid email and password
  - **Expected**: Successful login, redirected to dashboard

- [ ] **Test Case 2.2**: Login with wrong password
  - Enter valid email, wrong password
  - **Expected**: Error message "Incorrect credentials"

- [ ] **Test Case 2.3**: Login with non-existent email
  - Enter email that doesn't exist
  - **Expected**: Error message "Incorrect credentials"

- [ ] **Test Case 2.4**: Session persistence
  - Login and close browser
  - Reopen browser and navigate to dashboard
  - **Expected**: Still logged in (if "Remember me" was checked)

### Logout

- [ ] **Test Case 3.1**: Logout
  - Click logout button
  - **Expected**: Logged out, redirected to login page
  - Try to access protected page
  - **Expected**: Redirected to login

---

## 2. Telegram Account Management

### Adding Telegram Account

- [ ] **Test Case 4.1**: Add new Telegram account
  - Navigate to `/dashboard/telegram-accounts`
  - Click "Add Account"
  - Enter phone number
  - **Expected**: Account created, status "Pending Verification"

- [ ] **Test Case 4.2**: Send verification code
  - Click "Send Code" on pending account
  - **Expected**: Telegram code received on your phone

- [ ] **Test Case 4.3**: Verify account with correct code
  - Enter the received code
  - **Expected**: Account status changed to "Verified", "Active"

- [ ] **Test Case 4.4**: Verify with wrong code
  - Enter incorrect code
  - **Expected**: Error message "Invalid code"

- [ ] **Test Case 4.5**: Delete Telegram account
  - Click delete on an account
  - Confirm deletion
  - **Expected**: Account removed from list

---

## 3. Source Management (Telegram Channels/Groups)

### Syncing Dialogs

- [ ] **Test Case 5.1**: Sync available dialogs
  - With verified Telegram account
  - Click "Sync Dialogs" or "Import Sources"
  - **Expected**: List of available channels/groups appears

### Adding Sources

- [ ] **Test Case 6.1**: Add channel as source
  - Select a channel from available dialogs
  - Click "Add Source"
  - **Expected**: Source added with status "Active"

- [ ] **Test Case 6.2**: Add group as source
  - Select a group from available dialogs
  - Click "Add Source"
  - **Expected**: Source added with status "Active"

- [ ] **Test Case 6.3**: View source details
  - Click on a source
  - **Expected**: Shows title, username, type, member count

### Managing Sources

- [ ] **Test Case 7.1**: Deactivate source
  - Toggle "Active" switch to off
  - **Expected**: Source status changed to "Inactive"

- [ ] **Test Case 7.2**: Reactivate source
  - Toggle "Active" switch back on
  - **Expected**: Source status changed to "Active"

- [ ] **Test Case 7.3**: Delete source
  - Click delete on a source
  - Confirm deletion
  - **Expected**: Source removed from list

---

## 4. Rules Management

### Creating Rules

- [ ] **Test Case 8.1**: Create basic rule
  - Navigate to `/dashboard/rules`
  - Click "Create Rule"
  - Fill in: name, description, LLM prompt, threshold (0.7)
  - Select at least one source
  - **Expected**: Rule created successfully

- [ ] **Test Case 8.2**: Create rule without sources
  - Try to create rule without selecting sources
  - **Expected**: Validation error or warning

- [ ] **Test Case 8.3**: Create rule with multiple sources
  - Select 3+ sources
  - **Expected**: Rule applies to all selected sources

- [ ] **Test Case 8.4**: Test different thresholds
  - Create rules with threshold 0.5, 0.7, 0.9
  - **Expected**: Each rule created with specified threshold

### Managing Rules

- [ ] **Test Case 9.1**: View rule details
  - Click on a rule
  - **Expected**: Shows full rule details including associated sources

- [ ] **Test Case 9.2**: Edit rule
  - Click edit on a rule
  - Change name and threshold
  - Save
  - **Expected**: Changes saved successfully

- [ ] **Test Case 9.3**: Deactivate rule
  - Toggle "Active" switch to off
  - **Expected**: Rule stops processing new messages

- [ ] **Test Case 9.4**: Delete rule
  - Click delete on a rule
  - Confirm deletion
  - **Expected**: Rule deleted (leads remain but show "Deleted Rule")

---

## 5. Lead Management

### Viewing Leads

- [ ] **Test Case 10.1**: View all leads
  - Navigate to `/dashboard/leads`
  - **Expected**: List of all leads displayed

- [ ] **Test Case 10.2**: View lead details
  - Click on a lead
  - **Expected**: Shows message text, source, rule, score, reasoning, extracted entities

- [ ] **Test Case 10.3**: Filter by status
  - Select "New" from status filter
  - **Expected**: Only new leads displayed

- [ ] **Test Case 10.4**: Filter by rule
  - Select a specific rule from dropdown
  - **Expected**: Only leads from that rule displayed

- [ ] **Test Case 10.5**: Filter by source
  - Select a specific source from dropdown
  - **Expected**: Only leads from that source displayed

- [ ] **Test Case 10.6**: Filter by date range
  - Select date range
  - **Expected**: Only leads within that range displayed

### Managing Leads

- [ ] **Test Case 11.1**: Update lead status
  - Change status from "New" to "Contacted"
  - **Expected**: Status updated, badge color changes

- [ ] **Test Case 11.2**: Add notes to lead
  - Click edit or add note
  - Enter: "Called, left message"
  - **Expected**: Note saved and displayed

- [ ] **Test Case 11.3**: Assign lead to user
  - Select assignee from dropdown
  - **Expected**: Lead assigned to selected user

- [ ] **Test Case 11.4**: Delete lead
  - Click delete on a lead
  - Confirm deletion
  - **Expected**: Lead removed from list

### Lead Statistics

- [ ] **Test Case 12.1**: View lead stats
  - Check stats card on dashboard or leads page
  - **Expected**: Shows total leads, recent count, breakdown by status

### Export

- [ ] **Test Case 13.1**: Export all leads to CSV
  - Click "Export to CSV"
  - **Expected**: CSV file downloaded with all leads

- [ ] **Test Case 13.2**: Export filtered leads
  - Apply status filter "New"
  - Click "Export to CSV"
  - **Expected**: CSV contains only new leads

- [ ] **Test Case 13.3**: Verify CSV content
  - Open downloaded CSV
  - **Expected**: Contains columns: ID, Created At, Status, Score, Rule, Source, Message Text, Reasoning, Contacts, etc.

---

## 6. Analytics

### Dashboard Analytics

- [ ] **Test Case 14.1**: View dashboard stats
  - Navigate to `/dashboard`
  - **Expected**: Shows Active Sources, Active Rules, Total Leads, Recent Leads (24h)

- [ ] **Test Case 14.2**: View activity trends
  - Check Activity Trends card
  - **Expected**: Shows 3 metrics with trend indicators (↑↓→) and percentages

- [ ] **Test Case 14.3**: View recent leads widget
  - **Expected**: Shows last 5 leads with status badges and scores

- [ ] **Test Case 14.4**: Navigate to full analytics
  - Click "View Analytics" button
  - **Expected**: Redirected to `/dashboard/analytics`

### Analytics Page

- [ ] **Test Case 15.1**: View summary cards
  - Navigate to `/dashboard/analytics`
  - **Expected**: Shows 4 summary cards (Total Leads, Messages, Conversion, Avg Score)

- [ ] **Test Case 15.2**: View activity trends
  - **Expected**: Shows 3 trend metrics with period comparison

- [ ] **Test Case 15.3**: View time series chart
  - **Expected**: Line chart showing leads created over time

- [ ] **Test Case 15.4**: View conversion funnel
  - **Expected**: Horizontal bars showing lead progression through statuses

- [ ] **Test Case 15.5**: View top performers
  - **Expected**: Cards showing top source and top rule

- [ ] **Test Case 15.6**: View source performance table
  - **Expected**: Table with sources, messages, leads, conversion rate, avg score

- [ ] **Test Case 15.7**: View rule performance table
  - **Expected**: Table with rules, total leads, 7d/30d leads, avg score, active status

---

## 7. Notifications

### Notification Settings

- [ ] **Test Case 16.1**: View notification settings
  - Navigate to `/dashboard/settings`
  - **Expected**: Shows email notification toggles and thresholds

- [ ] **Test Case 16.2**: Enable new lead notifications
  - Toggle "Notify on New Lead" to ON
  - Save
  - **Expected**: Setting saved

- [ ] **Test Case 16.3**: Set high score threshold
  - Enable "Notify on High Score"
  - Set threshold to 0.85
  - Save
  - **Expected**: Setting saved

- [ ] **Test Case 16.4**: Update notification email
  - Change email address
  - Save
  - **Expected**: Email updated

### Email Notifications (if enabled)

- [ ] **Test Case 17.1**: Receive new lead notification
  - Create conditions for a new lead
  - Wait for message processing
  - **Expected**: Email received with lead details

- [ ] **Test Case 17.2**: Receive high score notification
  - Create conditions for high-score lead (>0.85)
  - **Expected**: Email received highlighting high score

---

## 8. Message Processing (Background)

### Automatic Message Collection

- [ ] **Test Case 18.1**: Verify messages are collected
  - Post a message in monitored channel
  - Wait 1-2 minutes
  - Check database or logs
  - **Expected**: Message saved to database

- [ ] **Test Case 18.2**: Verify LLM analysis
  - Post message matching a rule
  - Wait for processing
  - **Expected**: Lead created if score > threshold

- [ ] **Test Case 18.3**: Verify extracted entities
  - Post message with email, phone, keywords
  - Check created lead
  - **Expected**: Entities extracted and stored

---

## 9. User Interface & UX

### Navigation

- [ ] **Test Case 19.1**: Main menu navigation
  - Click each menu item
  - **Expected**: Navigates to correct page

- [ ] **Test Case 19.2**: Breadcrumbs
  - Navigate deep into pages
  - **Expected**: Breadcrumbs show current location

### Responsive Design

- [ ] **Test Case 20.1**: Mobile view (375px)
  - Resize browser to mobile width
  - **Expected**: Layout adapts, no horizontal scroll

- [ ] **Test Case 20.2**: Tablet view (768px)
  - Resize to tablet width
  - **Expected**: Layout adapts properly

- [ ] **Test Case 20.3**: Desktop view (1920px)
  - View on large screen
  - **Expected**: Content well-spaced, readable

### Loading States

- [ ] **Test Case 21.1**: Loading indicators
  - Trigger data fetch (refresh page)
  - **Expected**: Spinners or skeleton loaders shown

- [ ] **Test Case 21.2**: Empty states
  - View page with no data (new account)
  - **Expected**: Friendly empty state message

### Error Handling

- [ ] **Test Case 22.1**: Network error
  - Disable internet, try action
  - **Expected**: User-friendly error message

- [ ] **Test Case 22.2**: 404 page
  - Navigate to non-existent route
  - **Expected**: Custom 404 page

---

## 10. Security

### Authentication

- [ ] **Test Case 23.1**: Access protected route without login
  - Log out
  - Try to access `/dashboard`
  - **Expected**: Redirected to login

- [ ] **Test Case 23.2**: Token expiration
  - Wait for token to expire (30 min default)
  - Try to perform action
  - **Expected**: Logged out or prompted to re-authenticate

### Authorization

- [ ] **Test Case 24.1**: User can only see own data
  - Login as User A
  - Check that you can't see User B's data
  - **Expected**: Only tenant-specific data visible

### Input Validation

- [ ] **Test Case 25.1**: SQL injection attempt
  - Try SQL injection in search/filter fields
  - **Expected**: Input sanitized, no error

- [ ] **Test Case 25.2**: XSS attempt
  - Try `<script>alert('xss')</script>` in text fields
  - **Expected**: Escaped, not executed

---

## 11. Performance

- [ ] **Test Case 26.1**: Page load time
  - Measure initial dashboard load
  - **Expected**: < 3 seconds

- [ ] **Test Case 26.2**: Large data set handling
  - Create 100+ leads
  - Navigate to leads page
  - **Expected**: Paginated, loads smoothly

- [ ] **Test Case 26.3**: API response time
  - Check backend API calls in DevTools
  - **Expected**: Most endpoints < 500ms

---

## 12. Data Integrity

- [ ] **Test Case 27.1**: Lead count accuracy
  - Compare dashboard stats with database query
  - **Expected**: Numbers match

- [ ] **Test Case 27.2**: Status distribution accuracy
  - Check analytics funnel vs database
  - **Expected**: Percentages match actual data

---

## Sign-Off

**Tested By**: ___________________
**Date**: ___________________
**Environment**: [ ] Development [ ] Staging [ ] Production
**Overall Status**: [ ] Pass [ ] Fail [ ] Pass with Issues

**Issues Found**:
1.
2.
3.

**Notes**:


---

**Last Updated**: 2024-01-01
