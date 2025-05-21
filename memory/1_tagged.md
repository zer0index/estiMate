<!-- CHUNK_H2_1 -->
## 1. **Strategic Overview**

**Purpose**:  
Enable employees to request company-approved devices (notebooks and phones) through a self-service Power App, triggering approval workflows and integrating with internal policies.

**Business Value**:  
- Reduces manual processing time  
- Improves transparency in ordering  
- Enforces approval and budget policies  
- Scales across departments and locations

---

<!-- CHUNK_H2_2 -->
## 2. **User Roles**

| Role             | Permissions                             |
|------------------|------------------------------------------|
| Employee         | Submit order requests                    |
| Manager          | Approve/reject requests from reports     |
| IT Administrator | (Post-MVP) Fulfill orders, update stock  |
| Procurement      | (Post-MVP) Track purchasing metrics      |

---

<!-- CHUNK_H2_3 -->
## 3. **Core Features — MVP**

### 📦 Feature: Device Catalog **CanvasApp**
- Browse available devices (notebooks, phones)
- View specs, photos, availability
- Filter by department-approved models

### 📝 Feature: Order Request Form **CanvasApp**
- Select device
- Justify business need (textarea)
- Select urgency level (Normal, Urgent)
- Auto-populate employee name/department from Azure AD

### ✅ Feature: Approval Workflow **PowerAutomate**
- Manager receives approval notification
- Manager can approve/reject with comments
- SLA: 2 business days for decision

---

<!-- CHUNK_H2_4 -->
## 4. **Post-MVP Features**

### 📊 Feature: Request Tracking **CanvasApp**
- Employee can view status (Submitted, Approved, Fulfilled)
- Email notifications at each step
- Optional Power BI dashboard for tracking

### 🧾 Feature: Inventory Management **CanvasApp**
- Admin updates stock levels
- Mark orders as fulfilled
- Link to procurement system (e.g., SAP)

---

<!-- CHUNK_H2_5 -->
## 5. **Constraints & Requirements**

- ✅ Must use Power Apps Canvas App  
- ✅ Data must be stored in Dataverse  
- ✅ Approval process must use Power Automate  
- ✅ Device models filtered by department policy  
- ✅ App must support desktop + mobile usage  
- ❌ No external users (internal only via Azure AD)

---

<!-- CHUNK_H2_6 -->
## 6. **UX & Design Notes**

- Clean, corporate design with device images  
- Responsive layout for phone and desktop  
- Use dropdowns, cards, and status icons  
- Confirm order screen before submission  
- Accessible design (WCAG AA)

---

<!-- CHUNK_H2_7 -->
## 7. **Integration Points**

- **Dataverse** for orders, devices, users  
- **Power Automate** for approvals and notifications  
- **Azure AD** for user authentication  
- (Post-MVP) Procurement system (e.g., SAP)

---

<!-- CHUNK_H2_8 -->
## 8. **Security & Compliance**

- Role-based access via Dataverse security roles  
- Audit trail of approvals  
- Retain order data for 2 years per IT policy  
- No PII beyond employee ID and email

---

<!-- CHUNK_H2_9 -->
## 9. **User Stories, User Journeys**

- to be defined!

---

<!-- CHUNK_H2_10 -->
## 10. **Success Criteria**

- >90% of orders submitted via the app within 3 months  
- <2 day average approval time  
- Full traceability of device requests (Post-MVP)  
- Minimal support requests after go-live
