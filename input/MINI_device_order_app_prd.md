## 1. **Strategic Overview**

**Purpose**:  
Enable employees to request company-approved devices (notebooks and phones) through a self-service Power App, triggering approval workflows and integrating with internal policies.

**Business Value**:  
- Reduces manual processing time  
- Improves transparency in ordering  
- Enforces approval and budget policies  
- Scales across departments and locations

---

## 2. **User Roles**

| Role             | Permissions                             |
|------------------|------------------------------------------|
| Employee         | Submit order requests                    |
| Manager          | Approve/reject requests from reports     |
| IT Administrator | (Post-MVP) Fulfill orders, update stock  |
| Procurement      | (Post-MVP) Track purchasing metrics      |

---

## 3. **Core Features — MVP**

### 📦 Feature: Device Catalog
- Browse available devices (notebooks, phones)
- View specs, photos, availability
- Filter by department-approved models

### 📝 Feature: Order Request Form
- Select device
- Justify business need (textarea)
- Select urgency level (Normal, Urgent)
- Auto-populate employee name/department from Azure AD

### ✅ Feature: Approval Workflow
- Manager receives approval notification
- Manager can approve/reject with comments
- SLA: 2 business days for decision

---

## 4. **Post-MVP Features**

### 📊 Feature: Request Tracking
- Employee can view status (Submitted, Approved, Fulfilled)
- Email notifications at each step
- Optional Power BI dashboard for tracking

### 🧾 Feature: Inventory Management
- Admin updates stock levels
- Mark orders as fulfilled
- Link to procurement system (e.g., SAP)

