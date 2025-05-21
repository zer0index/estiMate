## 1. Strategic Overview

**Purpose**:  
Allow external customers to log technical issues or service requests, view ticket status, and receive resolution updates from support teams.

**Business Value**:  
- Improves customer satisfaction through transparency  
- Reduces inbound email requests to support teams  
- Enables SLA compliance through structured workflows  

---

## 2. User Roles

| Role            | Permissions                                     |
|------------------|--------------------------------------------------|
| Customer         | Submit and track own issues                     |
| Support Agent    | Update ticket status, add resolution steps       |
| Account Manager  | View ticket history of assigned customers        |

---

## 3. Core Features — MVP

### 📦 Feature: Frontend **PowerPages**
- Public issue submission form  
- View ticket status (Open, In Progress, Resolved)
- Upload relevant documents or screenshots  

### 📦 Feature: Automation **PowerAutomate**
- Receive email updates on progress  

---

## 4. Post-MVP Features **PowerPages**

- SLA timers & escalation rules  
- Customer satisfaction survey after resolution  
- Exportable ticket logs  

---

## 5. Constraints & Requirements

- Customer login must not require corporate credentials  
- Each user can only see their own organization’s tickets  
- Ticket data must be stored for 24 months