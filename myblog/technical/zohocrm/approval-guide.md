Perfect! Let me simplify this to just 2 approval flows. This will be much easier to implement and follow.

---

# **Simple Quote Approval - Complete Implementation Guide**

## **Simplified Business Logic**

- **< 10% discount**: Auto-approve (no approval needed)
- **10-20% discount**: Requires **Sales Manager** approval
- **> 20% discount**: Requires **VP Sales** approval

---

## **PART 1: Create Custom Fields**

### **Add Fields to Quotes Module**

**Navigate to:** Setup > Customization > Modules > Quotes > Fields

**Create these 3 fields:**

| Field Label | Field Name (API) | Field Type | Properties |
|-------------|------------------|------------|------------|
| Discount % | Discount_Percentage | Percent | Read-only |
| Approval Status | Approval_Status | Picklist | Options below |
| Approval Level | Approval_Level | Single Line | Read-only |

**Picklist Values for Approval Status:**
- Auto Approved
- Pending Manager Approval
- Pending VP Approval
- Approved
- Rejected

**Screenshot of what fields should look like:**
- Discount %: Calculated field, shows percentage
- Approval Status: Shows current status
- Approval Level: Shows who needs to approve (Manager/VP/None)

---

## **PART 2: Create the Function**

### **Step 2.1: Navigate to Functions**

1. Go to **Setup > Automation > Actions > Functions**
2. Click **+ Configure Function**
3. Click **Write your own**

### **Step 2.2: Configure Function**

- **Function Name**: `Set_Quote_Approval_Level`
- **Display Name**: Set Quote Approval Level
- **Description**: Determines approval level based on discount percentage
- **Module**: Quotes

### **Step 2.3: Complete Deluge Script (Simplified)**

```javascript
// ========================================
// SIMPLE QUOTE APPROVAL FUNCTION
// Determines approval level based on discount
// ========================================

try 
{
    // Get Quote ID
    quoteId = quote.get("id");
    info "Processing Quote ID: " + quoteId;
    
    // Fetch quote details
    quoteDetails = zoho.crm.getRecordById("Quotes", quoteId.toLong());
    
    if(quoteDetails == null)
    {
        return "Error: Quote not found";
    }
    
    // ========================================
    // STEP 1: Get Quote Values
    // ========================================
    
    quoteName = ifnull(quoteDetails.get("Subject"), "");
    subTotal = ifnull(quoteDetails.get("Sub_Total"), 0).toDecimal();
    discount = ifnull(quoteDetails.get("Discount"), 0).toDecimal();
    
    info "Quote: " + quoteName;
    info "Sub Total: " + subTotal;
    info "Discount: " + discount;
    
    // ========================================
    // STEP 2: Calculate Discount Percentage
    // ========================================
    
    discountPercentage = 0.0;
    
    if(subTotal > 0)
    {
        discountPercentage = (discount / subTotal) * 100;
    }
    
    info "Discount Percentage: " + discountPercentage;
    
    // ========================================
    // STEP 3: Determine Approval Level
    // ========================================
    
    approvalStatus = "";
    approvalLevel = "";
    
    // Simple 3-tier approval logic
    if(discountPercentage < 10)
    {
        // Auto approve - low discount
        approvalStatus = "Auto Approved";
        approvalLevel = "None - Auto Approved";
        info "Auto approved - discount below 10%";
    }
    else if(discountPercentage >= 10 && discountPercentage <= 20)
    {
        // Manager approval needed
        approvalStatus = "Pending Manager Approval";
        approvalLevel = "Sales Manager";
        info "Manager approval required - discount between 10-20%";
    }
    else if(discountPercentage > 20)
    {
        // VP approval needed
        approvalStatus = "Pending VP Approval";
        approvalLevel = "VP Sales";
        info "VP approval required - discount above 20%";
    }
    
    // ========================================
    // STEP 4: Update Quote
    // ========================================
    
    updateMap = Map();
    updateMap.put("Discount_Percentage", discountPercentage.round(2));
    updateMap.put("Approval_Status", approvalStatus);
    updateMap.put("Approval_Level", approvalLevel);
    
    // Update the quote
    updateResponse = zoho.crm.updateRecord("Quotes", quoteId.toString(), updateMap);
    
    if(updateResponse.get("code") == "SUCCESS")
    {
        info "Quote updated successfully";
        return "Success: Discount = " + discountPercentage.round(2) + "%, Approval Level = " + approvalLevel;
    }
    else
    {
        info "Error updating quote: " + updateResponse;
        return "Error updating quote";
    }
}
catch (e)
{
    info "Exception: " + e;
    return "Error: " + e;
}
```

### **Step 2.4: Save Function**

1. Click **Save & Execute Script**
2. Fix any errors if shown
3. Click **Save**

---

## **PART 3: Create Workflow Rule**

### **Step 3.1: Create Workflow**

**Navigate to:** Setup > Automation > Workflow Rules

1. Click **+ Create Rule**

**Fill in:**
- **Module**: Quotes
- **Rule Name**: Set Approval Level on Quote Save
- **Description**: Calculates discount and sets approval level
- **When**: Record action is **Created or Edited**
- **Condition**: None (execute always)

### **Step 3.2: Add Instant Action**

1. Under **Instant Actions**, click **Functions**
2. Select **Set_Quote_Approval_Level**
3. Click **Associate**
4. Click **Save**

---

## **PART 4: Set Up Approval Process**

### **Step 4.1: Create Approval Process**

**Navigate to:** Setup > Process Management > Approval Process

1. Click **+ Add Approval Process**

**Fill in:**
- **Module**: Quotes
- **Name**: Quote Approval
- **Description**: Two-tier quote approval based on discount
- **When to Execute**: Record Edit

2. Click **Next**

---

### **Step 4.2: Add Rule 1 - Manager Approval**

Click **+ Add Rule to this Process**

#### **Rule Configuration:**

**Rule Name**: Manager Approval (10-20%)

**Rule Description**: Quotes with 10-20% discount need manager approval

**Criteria:**
```
Approval_Status equals "Pending Manager Approval"
```

**Who Should Approve:**
- Option 1: Select **User** → Choose a specific Sales Manager
- Option 2: Select **Role** → Choose "Sales Manager" role
- Option 3: Select **Levels** → Choose "1st Level" (direct manager)

**Approval Order**: Anyone

**On Approval - Actions:**
1. **Field Update**:
   - Field: Approval_Status
   - Value: "Approved"

**On Rejection - Actions:**
1. **Field Update**:
   - Field: Approval_Status
   - Value: "Rejected"

Click **Save**

---

### **Step 4.3: Add Rule 2 - VP Approval**

Click **+ Add Rule to this Process** again

#### **Rule Configuration:**

**Rule Name**: VP Approval (>20%)

**Rule Description**: Quotes with discount above 20% need VP approval

**Criteria:**
```
Approval_Status equals "Pending VP Approval"
```

**Who Should Approve:**
- Option 1: Select **User** → Choose a specific VP
- Option 2: Select **Role** → Choose "VP Sales" role
- Option 3: Select **Levels** → Choose "2nd Level" (manager's manager)

**Approval Order**: Anyone

**On Approval - Actions:**
1. **Field Update**:
   - Field: Approval_Status
   - Value: "Approved"

**On Rejection - Actions:**
1. **Field Update**:
   - Field: Approval_Status
   - Value: "Rejected"

Click **Save**

---

### **Step 4.4: Save & Activate**

Click **Save** to activate the entire approval process.

---

## **PART 5: Testing Guide**

### **Test Case 1: Auto Approve (<10% discount)**

**Steps:**
1. Go to **Quotes** module
2. Click **+ Create Quote**
3. Fill in:
   - Subject: "Test Quote - Low Discount"
   - Contact/Account: Select any
4. Add Products (or manually enter amounts):
   - Sub Total: $10,000
   - Discount: $500
5. Click **Save**

**Expected Results:**
- Discount %: **5%**
- Approval Status: **Auto Approved**
- Approval Level: **None - Auto Approved**
- No approval request sent
- Record is NOT locked

**Verification:**
Open the quote and check the three custom fields show correct values.

---

### **Test Case 2: Manager Approval (10-20% discount)**

**Steps:**
1. Create new Quote
2. Fill in:
   - Subject: "Test Quote - Medium Discount"
3. Add Products:
   - Sub Total: $10,000
   - Discount: $1,500 (15%)
4. Click **Save**

**Expected Results:**
- Discount %: **15%**
- Approval Status: **Pending Manager Approval**
- Approval Level: **Sales Manager**
- Approval request sent to Sales Manager
- Record is LOCKED (cannot edit while pending)

**Manager's View:**
1. Manager logs into Zoho CRM
2. Clicks **Approvals** tab (or Bell icon for notifications)
3. Sees quote in pending list
4. Can click **Approve** or **Reject**

**After Manager Approves:**
- Approval Status: **Approved**
- Record unlocks
- Quote owner gets notification

---

### **Test Case 3: VP Approval (>20% discount)**

**Steps:**
1. Create new Quote
2. Fill in:
   - Subject: "Test Quote - High Discount"
3. Add Products:
   - Sub Total: $10,000
   - Discount: $2,500 (25%)
4. Click **Save**

**Expected Results:**
- Discount %: **25%**
- Approval Status: **Pending VP Approval**
- Approval Level: **VP Sales**
- Approval request sent to VP
- Record is LOCKED

**VP's View:**
1. VP logs into Zoho CRM
2. Goes to **Approvals** tab
3. Sees quote pending approval
4. Reviews discount amount and reason
5. Clicks **Approve** or **Reject**

**After VP Rejects:**
- Approval Status: **Rejected**
- Record unlocks
- Quote owner gets rejection notification
- Can edit and resubmit

---

## **PART 6: How Users Interact**

### **For Sales Reps:**

**Creating Quotes:**
1. Create quote normally
2. Add products and discount
3. Save
4. System automatically determines if approval needed
5. If approval needed:
   - Quote locks
   - Notification sent to approver
   - Rep waits for approval
6. If auto-approved:
   - Quote ready to send
   - No waiting

**Checking Status:**
- Open quote
- Look at "Approval Status" field
- See who needs to approve in "Approval Level" field

---

### **For Approvers:**

**Receiving Requests:**
1. Get email notification
2. Bell icon shows pending approvals
3. Click notification

**Approving:**
1. Go to **Approvals** tab
2. See list of pending quotes
3. Click on quote to review
4. See discount amount and details
5. Click **Approve** or **Reject**
6. Add comments (optional)
7. Submit decision

**Mobile App:**
- Same process works on mobile
- Get push notifications
- Approve on-the-go

---

## **PART 7: Troubleshooting**

### **Issue: Function not executing**

**Check:**
1. Go to **Setup > Automation > Workflow Rules**
2. Find "Set Approval Level on Quote Save"
3. Verify it's **Active** (toggle should be ON)
4. Check execution history

**Fix:**
- Edit workflow rule
- Re-associate the function
- Save again

---

### **Issue: Discount % not calculating**

**Check:**
1. Quote has Sub Total > 0
2. Discount field has a value
3. Open quote and manually trigger by editing and saving

**Debug:**
1. Go to **Setup > Automation > Actions > Functions**
2. Click on function name
3. Click **Execution Log**
4. Look for errors or info messages
5. Check what values are being calculated

---

### **Issue: Approval not triggering**

**Check:**
1. Approval Status field exactly matches: "Pending Manager Approval" or "Pending VP Approval"
2. Approval Process is **Active**
3. Approver user exists and has correct role

**Fix:**
1. Edit the quote
2. Manually change Approval Status to trigger approval
3. Save
4. Check if approval request appears

---

### **Issue: Fields not showing**

**Check:**
1. Go to **Setup > Customization > Modules > Quotes > Layouts**
2. Edit the layout
3. Drag the three custom fields to the page
4. Save layout
5. Refresh quote page

---

## **PART 8: Optional Enhancements**

### **Add Email Notification to Quote Owner**

**In Approval Process > On Approval:**
1. Click **+ Email Notification**
2. Select **To**: Quote Owner
3. Subject: "Your quote has been approved"
4. Body: "Quote {!Quotes.Subject} has been approved by {!Quotes.Approval_Level}"

---

### **Add Approval History Section**

Zoho CRM automatically tracks:
- Who approved/rejected
- When
- Comments

**To view:**
1. Open any quote
2. Scroll to **Approval History** section
3. See complete audit trail

---

### **Set Approval Deadline**

**In Approval Process:**
1. Enable "Send reminder after"
2. Set to 24 hours
3. Approver gets reminder email if not actioned

---

## **PART 9: Summary**

### **What You've Built:**

✅ **Automatic discount calculation** when quote is saved  
✅ **3-tier approval system**: Auto / Manager / VP  
✅ **Automatic routing** to correct approver  
✅ **Record locking** during approval  
✅ **Complete audit trail** of approvals  
✅ **Email notifications** to approvers  

### **Key Components:**

1. **Custom Fields** (3 fields on Quotes)
2. **Function**: Set_Quote_Approval_Level
3. **Workflow**: Triggers function on save
4. **Approval Process**: 2 rules (Manager & VP)

### **Testing Checklist:**

- [ ] Test <10% discount → Auto approve
- [ ] Test 10-20% discount → Manager approval
- [ ] Test >20% discount → VP approval
- [ ] Test manager approving quote
- [ ] Test manager rejecting quote
- [ ] Test VP approving quote
- [ ] Verify email notifications work
- [ ] Verify record locking during approval

---

## **Quick Reference Card**

**Discount Ranges:**
- 0-9.99% → Auto Approved
- 10-20% → Manager Approval
- 20%+ → VP Approval

**Field Names (for reference):**
- Discount_Percentage
- Approval_Status
- Approval_Level

**Function Name:**
- Set_Quote_Approval_Level

**Workflow Name:**
- Set Approval Level on Quote Save

**Approval Process Name:**
- Quote Approval

---

This simplified version is much easier to implement and maintain while still providing robust approval functionality. You now have just 2 approval paths instead of 4, making it straightforward for your team to understand and use!
