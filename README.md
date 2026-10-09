# Anonymous Complaint Management System (ACMS)

> **“Speak Freely. Stay Anonymous. Get Heard.”**

A modern, professional, fully responsive web application that empowers students, employees, citizens, and organizational members to submit complaints anonymously without revealing their personal identity. Designated administrators and compliance officers can securely inspect, manage, update, and resolve grievances through an interactive administrative dashboard.

---

## 🌟 Key Features

### 1. 100% Anonymous Reporting
- **Zero Personally Identifiable Information (PII):** Name, email address, phone number, and physical identity are never requested or stored.
- **No IP Logging:** Rate-limiting uses ephemeral, one-way cryptographic hashing that automatically expires every few minutes.
- **Metadata Sanitization:** Uploaded file attachments (documents, images) are assigned random cryptographic filenames to eliminate operating system file paths or camera EXIF metadata.

### 2. Streamlined Complaint Submission
- **Categorization:** Academic, Harassment, Infrastructure, Corruption, Safety, Workplace/College Issue, and Other.
- **Priority Indicator:** Low, Medium, High.
- **Optional Details:** Incident date and physical location or department.
- **Supporting Evidence:** Optional file upload (Images, PDF, Word, TXT up to 5MB).
- **Spam Defense:** Self-contained, privacy-preserving arithmetic CAPTCHA challenges.
- **Immediate Confirmation:** Generates a unique Complaint Tracking ID (e.g., `ACMS-4B9X-7L2M`) with one-click clipboard copying and downloadable official receipt slip.

### 3. Public Complaint Tracking
- Enter your unique Complaint ID to view live progress anytime.
- **Visual Status Stepper:**
  `Submitted` &rarr; `Under Review` &rarr; `Investigation` &rarr; `Action Taken` &rarr; `Resolved` (or `Rejected`).
- Read official responses from administrative compliance officers.
- Chronological timeline history of status updates and investigation milestones.

### 4. Comprehensive Admin Portal
- **Secure Authentication:** Role-based access with bcrypt password hashing and JSON Web Tokens (JWT).
- **Analytics KPI Cards:** Total Complaints, New Complaints, Under Review, Resolved, High Priority, and Resolution Rate %.
- **Complaint Management Table:** Paginated table with real-time search, category filters, status filters, and priority filters.
- **Action Modal:** View full complaint details, download attachments, update status, record public response, add private internal notes, and delete spam complaints.
- **Data Export:** Instant one-click CSV export of filtered complaints.

---

## 🏗️ Project Architecture

```
anonymous-complaint-system/
├── .env                         # Environment variables
├── .env.example                 # Example environment template
├── package.json                 # Node.js project manifest & dependencies
├── server.js                    # Express application entry point
├── config/
│   └── db.js                    # MongoDB / Mongoose connection with resilient fallback
├── models/
│   ├── Admin.js                 # Admin Mongoose model with bcrypt hashing
│   ├── Complaint.js             # Complaint Mongoose model & public serializer
│   └── memoryStore.js           # Resilient local JSON / memory store fallback
├── controllers/
│   ├── authController.js        # Admin login, token issuance, session verification
│   └── complaintController.js   # Submit, track, list, update, and delete complaints
├── middleware/
│   ├── auth.js                  # JWT token verification & role enforcement
│   ├── rateLimiter.js           # Privacy-preserving ephemeral rate limiter
│   ├── security.js              # Security headers, XSS & NoSQL sanitization
│   └── upload.js                # Secure Multer file upload whitelist & rename
├── utils/
│   ├── captcha.js               # Challenge-response arithmetic CAPTCHA
│   ├── idGenerator.js           # Cryptographic unambiguous Tracking ID generator
│   └── seedData.js              # Auto-seeds default admin and sample complaints
└── public/                      # Responsive frontend web application
    ├── index.html               # Single Page Application shell
    ├── css/
    │   └── style.css            # Modern professional blue/white design system
    ├── js/
    │   ├── api.js               # Centralized API client with offline auto-fallback
    │   ├── app.js               # Core router, modals, toasts, and navigation
    │   ├── submit.js            # Complaint submission & receipt generation
    │   ├── track.js             # Live tracking & visual status stepper
    │   └── admin.js             # Admin dashboard, analytics, and action modal
    └── uploads/                 # Storage for sanitized attachments
```

---

## 🚀 Quick Start Guide

### Prerequisites
- [Node.js](https://nodejs.org/) (v16 or higher)
- [MongoDB](https://www.mongodb.com/) (Optional: if MongoDB is not running locally, the system automatically activates its built-in in-memory/JSON store so you can evaluate the entire system immediately with zero setup blockers!)

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Configuration
The `.env` file is pre-configured with default settings:
```env
PORT=5000
MONGODB_URI=mongodb://127.0.0.1:27017/anonymous_complaints
JWT_SECRET=acms_super_secret_jwt_key_2026_complaint_portal
JWT_EXPIRES_IN=7d
ADMIN_DEFAULT_EMAIL=admin@acms.org
ADMIN_DEFAULT_PASSWORD=Admin@123
MAX_FILE_SIZE_MB=5
NODE_ENV=development
```

### 3. Start the Server
```bash
npm start
```

Open your browser at:
```
http://localhost:5000
```

---

## 🔑 Default Administrator Credentials

For evaluation and testing:
- **Portal URL:** `http://localhost:5000/#login`
- **Username / Email:** `admin@acms.org`
- **Password:** `Admin@123`

*(A handy "Auto Fill" button is also provided directly on the login page for one-click testing.)*

---

## 🔍 Pre-Loaded Sample Tracking IDs for Testing

You can instantly test tracking on `http://localhost:5000/#track` using any of the following seeded IDs:
- `ACMS-4B9X-7L2M` &mdash; Infrastructure complaint (`Action Taken`)
- `ACMS-8K3P-9D4Q` &mdash; Academic grievance (`Under Review`)
- `ACMS-6N1H-3J8V` &mdash; Safety hazard report (`Resolved`)

---

## 📡 API Reference

### Public Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/complaints/captcha` | Generates a new privacy-preserving arithmetic challenge token |
| `POST` | `/api/complaints` | Submits a new anonymous complaint (multipart/form-data) |
| `GET` | `/api/complaints/track/:complaintId` | Returns public complaint timeline and status (zero PII) |
| `GET` | `/api/health` | System health check and database status |

### Administrator Endpoints (Requires `Authorization: Bearer <token>`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Authenticates admin credentials and returns JWT token |
| `GET` | `/api/auth/me` | Returns current admin profile |
| `GET` | `/api/complaints/admin/stats` | Returns KPI cards summary (totals, review, resolved, etc.) |
| `GET` | `/api/complaints/admin/all` | Paginated search, category, status, and priority query |
| `GET` | `/api/complaints/admin/:complaintId` | Full complaint details including internal notes |
| `PUT` | `/api/complaints/admin/:complaintId/status` | Updates status, adds timeline entry, and posts official response |
| `DELETE` | `/api/complaints/admin/:complaintId` | Permanently deletes inappropriate or spam complaints |

---

## 🛡️ Security & Privacy Engineering

1. **No PII Schema:** The database schema has no fields for complainant name, email, phone, IP address, or user agent.
2. **Password Hashing:** Salted `bcryptjs` hashing (10 salt rounds) protects administrative passwords.
3. **JWT Session Protection:** Protected routes verify token signatures and expiration.
4. **Input Sanitization:** HTML tag stripping and NoSQL query injection blocking (`$where`, `$gt` stripping) on all endpoints.
5. **Security Headers:** Enforces `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, and strict referrer policy.
6. **Upload Whitelist:** Strictly filters file extensions (`.jpg`, `.png`, `.webp`, `.pdf`, `.txt`, `.docx`) and limits payload to 5MB.
7. **Ephemeral Rate Limiter:** Protects submission and login forms against automated spam floods without persisting user IPs.

---

## 📄 License
MIT License. Built for privacy, safety, and organizational transparency.
