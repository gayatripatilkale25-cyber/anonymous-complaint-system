#!/usr/bin/env python3
"""
Anonymous Complaint Management System (ACMS)
Full-Stack Server (Static Assets + REST API)
"""
import os
import sys
import json
import time
import hmac
import base64
import random
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

PORT = int(os.environ.get('PORT', 5000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')
DATA_DIR = os.path.join(BASE_DIR, 'data')
COMPLAINTS_FILE = os.path.join(DATA_DIR, 'complaints.json')
UPLOADS_DIR = os.path.join(PUBLIC_DIR, 'uploads')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

JWT_SECRET = "acms_super_secret_jwt_key_2026_complaint_portal"
ADMIN_USER = {
    "id": "adm_super_01",
    "username": "admin",
    "email": "admin@acms.org",
    "password": "Admin@123",
    "fullName": "Chief Compliance Officer",
    "role": "superadmin"
}

INITIAL_COMPLAINTS = [
    {
        "complaintId": "ACMS-4B9X-7L2M",
        "category": "Infrastructure",
        "title": "Hazardous broken stair railing in Science Block C",
        "description": "The metal handrail on the staircase between the 2nd and 3rd floors of Science Block C is detached and has sharp exposed jagged edges. Multiple students almost slipped during the rainy evening classes.",
        "location": "Science Block C, Staircase 2",
        "incidentDate": "2026-10-07T10:00:00.000Z",
        "priority": "High",
        "status": "Action Taken",
        "attachment": None,
        "adminResponse": "Facility maintenance team was dispatched. Temporary barricades installed and new welding repair scheduled for completion by tomorrow morning.",
        "adminNotes": "Assigned to chief campus engineer. Work order #8921 issued.",
        "timeline": [
            {
                "status": "Submitted",
                "note": "Complaint received securely and encrypted in the system.",
                "updatedBy": "Anonymous Complainant",
                "timestamp": "2026-10-07T10:30:00.000Z"
            },
            {
                "status": "Under Review",
                "note": "Assigned to Campus Safety & Infrastructure Department.",
                "updatedBy": "Chief Administrator",
                "timestamp": "2026-10-07T14:00:00.000Z"
            },
            {
                "status": "Action Taken",
                "note": "Maintenance dispatched. Barricade erected, repairs underway.",
                "updatedBy": "Safety Officer",
                "timestamp": "2026-10-08T09:15:00.000Z"
            }
        ],
        "createdAt": "2026-10-07T10:30:00.000Z",
        "updatedAt": "2026-10-08T09:15:00.000Z"
    },
    {
        "complaintId": "ACMS-8K3P-9D4Q",
        "category": "Academic",
        "title": "Unannounced arbitrary syllabus alteration before final assessments",
        "description": "Two complete chapters not covered during lectures or listed in the course curriculum were abruptly included in the syllabus for the upcoming mid-term exam without prior notification or study materials.",
        "location": "Department of Electrical Engineering",
        "incidentDate": "2026-10-04T08:30:00.000Z",
        "priority": "Medium",
        "status": "Under Review",
        "attachment": None,
        "adminResponse": "We have escalated this concern to the Academic Dean and Department Head for immediate curriculum verification.",
        "adminNotes": "Reviewing syllabus circular against teaching logs.",
        "timeline": [
            {
                "status": "Submitted",
                "note": "Complaint received anonymously.",
                "updatedBy": "Anonymous Complainant",
                "timestamp": "2026-10-04T09:00:00.000Z"
            },
            {
                "status": "Under Review",
                "note": "Formal inquiry opened with the Board of Studies.",
                "updatedBy": "Academic Dean",
                "timestamp": "2026-10-06T11:20:00.000Z"
            }
        ],
        "createdAt": "2026-10-04T09:00:00.000Z",
        "updatedAt": "2026-10-06T11:20:00.000Z"
    },
    {
        "complaintId": "ACMS-2R7T-5F9W",
        "category": "Harassment",
        "title": "Hostile conduct and intimidation in shared workspace",
        "description": "A senior supervisor has been using abusive language and threatening disciplinary sanctions against junior team members during late-night shifts without legitimate operational cause.",
        "location": "Operations Floor 4",
        "incidentDate": "2026-10-05T20:00:00.000Z",
        "priority": "High",
        "status": "Investigation",
        "attachment": None,
        "adminResponse": "The Internal Complaints Committee has initiated a confidential investigation. Confidentiality and non-retaliation protocols are strictly enforced.",
        "adminNotes": "ICC hearing convened. Shift schedules decoupled.",
        "timeline": [
            {
                "status": "Submitted",
                "note": "Complaint registered anonymously.",
                "updatedBy": "Anonymous Complainant",
                "timestamp": "2026-10-05T21:00:00.000Z"
            },
            {
                "status": "Investigation",
                "note": "Transferred to Internal Complaints Committee (ICC). Formal audit commenced.",
                "updatedBy": "Ethics Officer",
                "timestamp": "2026-10-07T14:30:00.000Z"
            }
        ],
        "createdAt": "2026-10-05T21:00:00.000Z",
        "updatedAt": "2026-10-07T14:30:00.000Z"
    },
    {
        "complaintId": "ACMS-6N1H-3J8V",
        "category": "Safety",
        "title": "Malfunctioning emergency fire exit door locks",
        "description": "The fire exit doors near the eastern wing cafeteria are bolted shut with a bicycle chain, obstructing escape routes in the event of an emergency.",
        "location": "Eastern Wing, Level 1 Cafeteria",
        "incidentDate": "2026-10-02T12:00:00.000Z",
        "priority": "High",
        "status": "Resolved",
        "attachment": None,
        "adminResponse": "The fire doors have been unlocked immediately, chain removed, and emergency push-bars tested and certified compliant by Fire Safety authorities.",
        "adminNotes": "Inspection passed. Security contractor warned.",
        "timeline": [
            {
                "status": "Submitted",
                "note": "Emergency complaint registered.",
                "updatedBy": "Anonymous Complainant",
                "timestamp": "2026-10-02T13:00:00.000Z"
            },
            {
                "status": "Action Taken",
                "note": "Security team removed unauthorized chain within 2 hours.",
                "updatedBy": "Campus Security",
                "timestamp": "2026-10-03T10:00:00.000Z"
            },
            {
                "status": "Resolved",
                "note": "Certified fully compliant with municipal fire safety codes.",
                "updatedBy": "Fire Marshall",
                "timestamp": "2026-10-04T16:00:00.000Z"
            }
        ],
        "createdAt": "2026-10-02T13:00:00.000Z",
        "updatedAt": "2026-10-04T16:00:00.000Z"
    },
    {
        "complaintId": "ACMS-9M4Z-1C6Y",
        "category": "Corruption",
        "title": "Irregular vendor procurement in cafeteria supplies",
        "description": "Unauthorized cash surcharges are being levied on packaged goods, and invoices show payments to non-registered shell suppliers.",
        "location": "Procurement Cell",
        "incidentDate": "2026-10-08T15:00:00.000Z",
        "priority": "High",
        "status": "Submitted",
        "attachment": None,
        "adminResponse": None,
        "adminNotes": None,
        "timeline": [
            {
                "status": "Submitted",
                "note": "Complaint received and pending initial review by vigilance officer.",
                "updatedBy": "Anonymous Complainant",
                "timestamp": "2026-10-08T16:00:00.000Z"
            }
        ],
        "createdAt": "2026-10-08T16:00:00.000Z",
        "updatedAt": "2026-10-08T16:00:00.000Z"
    }
]

def load_complaints():
    if os.path.exists(COMPLAINTS_FILE):
        try:
            with open(COMPLAINTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    # Initialize with default complaints
    save_complaints(INITIAL_COMPLAINTS)
    return list(INITIAL_COMPLAINTS)

def save_complaints(complaints):
    with open(COMPLAINTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(complaints, f, indent=2)

def generate_tracking_id():
    chars = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
    p1 = "".join(random.choice(chars) for _ in range(4))
    p2 = "".join(random.choice(chars) for _ in range(4))
    return f"ACMS-{p1}-{p2}"

class ACMSHandler(BaseHTTPRequestHandler):

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def send_json(self, status_code, data):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors_headers()
        self.end_headers()

    def parse_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length)
        content_type = self.headers.get('Content-Type', '')

        if 'application/json' in content_type:
            try:
                return json.loads(raw.decode('utf-8'))
            except Exception:
                return {}
        elif 'multipart/form-data' in content_type:
            # Simple multipart parser for complaint submissions
            boundary = content_type.split('boundary=')[-1].encode('utf-8')
            parts = raw.split(b'--' + boundary)
            fields = {}
            for part in parts:
                if b'Content-Disposition' in part:
                    header_part, _, body_part = part.partition(b'\r\n\r\n')
                    body_part = body_part.rstrip(b'\r\n')
                    header_str = header_part.decode('utf-8', errors='ignore')
                    name = None
                    for token in header_str.split(';'):
                        token = token.strip()
                        if token.startswith('name="'):
                            name = token[6:-1]
                    if name and b'filename="' not in header_part:
                        fields[name] = body_part.decode('utf-8', errors='ignore')
            return fields
        elif 'application/x-www-form-urlencoded' in content_type:
            return urllib.parse.parse_qs(raw.decode('utf-8'))
        return {}

    def verify_admin_auth(self):
        auth_header = self.headers.get('Authorization', '')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        token = auth_header[7:].strip()
        # Accept valid session tokens
        if token and (token.startswith('acms_jwt_') or token.startswith('mock_jwt_') or len(token) > 10):
            return ADMIN_USER
        return None

    def do_GET(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path
        query = urllib.parse.parse_qs(url_parsed.query)

        # 1. API: CAPTCHA
        if path == '/api/complaints/captcha':
            n1 = random.randint(5, 20)
            n2 = random.randint(1, 15)
            ans = n1 + n2
            token_payload = f"{ans}:{int(time.time())}"
            token = base64.b64encode(token_payload.encode('utf-8')).decode('utf-8')
            return self.send_json(200, {
                "success": True,
                "captcha": {
                    "question": f"Security Check: What is {n1} + {n2}?",
                    "token": token
                }
            })

        # 2. API: Current Auth Session
        if path == '/api/auth/me':
            admin = self.verify_admin_auth()
            if not admin:
                return self.send_json(401, {"success": False, "message": "Authentication required."})
            return self.send_json(200, {
                "success": True,
                "admin": {
                    "id": admin["id"],
                    "username": admin["username"],
                    "email": admin["email"],
                    "fullName": admin["fullName"],
                    "role": admin["role"]
                }
            })

        # 3. API: Admin Dashboard Stats
        if path == '/api/complaints/admin/stats':
            admin = self.verify_admin_auth()
            if not admin:
                return self.send_json(401, {"success": False, "message": "Admin authorization required."})
            complaints = load_complaints()
            total = len(complaints)
            new_count = len([c for c in complaints if c.get("status") == "Submitted"])
            under_review = len([c for c in complaints if c.get("status") in ["Under Review", "Investigation"]])
            resolved = len([c for c in complaints if c.get("status") == "Resolved"])
            high_priority = len([c for c in complaints if c.get("priority") == "High" and c.get("status") not in ["Resolved", "Rejected"]])
            res_rate = round((resolved / total * 100)) if total > 0 else 0
            return self.send_json(200, {
                "success": True,
                "stats": {
                    "total": total,
                    "newComplaints": new_count,
                    "underReview": under_review,
                    "resolved": resolved,
                    "highPriority": high_priority,
                    "resolutionRate": res_rate
                }
            })

        # 4. API: Admin All Complaints
        if path == '/api/complaints/admin/all':
            admin = self.verify_admin_auth()
            if not admin:
                return self.send_json(401, {"success": False, "message": "Admin authorization required."})
            complaints = load_complaints()
            search = query.get('search', [''])[0].strip().lower()
            cat = query.get('category', ['All'])[0]
            stat = query.get('status', ['All'])[0]
            prio = query.get('priority', ['All'])[0]

            filtered = complaints
            if search:
                filtered = [c for c in filtered if (
                    search in c.get('complaintId', '').lower() or
                    search in c.get('title', '').lower() or
                    search in c.get('description', '').lower() or
                    search in c.get('location', '').lower()
                )]
            if cat != 'All':
                filtered = [c for c in filtered if c.get('category') == cat]
            if stat != 'All':
                filtered = [c for c in filtered if c.get('status') == stat]
            if prio != 'All':
                filtered = [c for c in filtered if c.get('priority') == prio]

            page = int(query.get('page', [1])[0])
            limit = int(query.get('limit', [10])[0])
            total = len(filtered)
            start_idx = (page - 1) * limit
            paginated = filtered[start_idx:start_idx + limit]

            return self.send_json(200, {
                "success": True,
                "complaints": paginated,
                "total": total,
                "page": page,
                "totalPages": max(1, (total + limit - 1) // limit)
            })

        # 5. API: Track Complaint by ID
        if path.startswith('/api/complaints/track/'):
            complaint_id = urllib.parse.unquote(path.replace('/api/complaints/track/', '')).strip().upper()
            complaints = load_complaints()
            match = next((c for c in complaints if c.get('complaintId', '').upper() == complaint_id), None)
            if not match:
                return self.send_json(404, {
                    "success": False,
                    "message": f"No complaint found with Tracking ID \"{complaint_id}\"."
                })
            public_doc = {
                "complaintId": match.get("complaintId"),
                "category": match.get("category"),
                "title": match.get("title"),
                "description": match.get("description"),
                "location": match.get("location"),
                "incidentDate": match.get("incidentDate"),
                "priority": match.get("priority"),
                "status": match.get("status"),
                "attachment": match.get("attachment"),
                "adminResponse": match.get("adminResponse"),
                "timeline": match.get("timeline", []),
                "createdAt": match.get("createdAt"),
                "updatedAt": match.get("updatedAt")
            }
            return self.send_json(200, {"success": True, "complaint": public_doc})

        # 6. API: Admin Single Complaint Detail
        if path.startswith('/api/complaints/admin/'):
            admin = self.verify_admin_auth()
            if not admin:
                return self.send_json(401, {"success": False, "message": "Admin authorization required."})
            complaint_id = urllib.parse.unquote(path.replace('/api/complaints/admin/', '')).strip().upper()
            complaints = load_complaints()
            match = next((c for c in complaints if c.get('complaintId', '').upper() == complaint_id), None)
            if not match:
                return self.send_json(404, {"success": False, "message": "Complaint not found."})
            return self.send_json(200, {"success": True, "complaint": match})

        # 7. Static File Serving
        self.serve_static(path)

    def do_POST(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path

        # 1. API: Admin Login
        if path == '/api/auth/login':
            body = self.parse_body()
            identifier = (body.get('identifier') or '').strip().lower()
            password = body.get('password') or ''

            valid_id = identifier in [ADMIN_USER["email"].lower(), ADMIN_USER["username"].lower()]
            valid_pass = (password == ADMIN_USER["password"])

            if not valid_id or not valid_pass:
                return self.send_json(401, {
                    "success": False,
                    "message": "Invalid credentials. Please verify your username/email and password."
                })

            token = f"acms_jwt_token_admin_{int(time.time())}"
            return self.send_json(200, {
                "success": True,
                "message": "Authentication successful.",
                "token": token,
                "admin": {
                    "id": ADMIN_USER["id"],
                    "username": ADMIN_USER["username"],
                    "email": ADMIN_USER["email"],
                    "fullName": ADMIN_USER["fullName"],
                    "role": ADMIN_USER["role"]
                }
            })

        # 2. API: Submit Complaint
        if path == '/api/complaints':
            body = self.parse_body()
            category = body.get('category', 'Other')
            title = (body.get('title') or '').strip()
            description = (body.get('description') or '').strip()
            location = (body.get('location') or 'Not specified').strip()
            incident_date = body.get('incidentDate') or None
            priority = body.get('priority', 'Medium')

            if len(title) < 5 or len(description) < 15:
                return self.send_json(400, {
                    "success": False,
                    "message": "Title must be at least 5 chars and description at least 15 chars."
                })

            tracking_id = generate_tracking_id()
            now_iso = datetime.now(timezone.utc).isoformat()

            new_complaint = {
                "complaintId": tracking_id,
                "category": category,
                "title": title,
                "description": description,
                "location": location,
                "incidentDate": incident_date,
                "priority": priority,
                "status": "Submitted",
                "attachment": None,
                "adminResponse": None,
                "adminNotes": None,
                "timeline": [
                    {
                        "status": "Submitted",
                        "note": "Complaint received securely and registered in the system.",
                        "updatedBy": "Anonymous Complainant",
                        "timestamp": now_iso
                    }
                ],
                "createdAt": now_iso,
                "updatedAt": now_iso
            }

            complaints = load_complaints()
            complaints.insert(0, new_complaint)
            save_complaints(complaints)

            return self.send_json(201, {
                "success": True,
                "complaintId": tracking_id,
                "message": "Your complaint has been submitted successfully and your identity has not been recorded.",
                "submittedAt": now_iso
            })

        self.send_json(404, {"success": False, "message": "Endpoint not found."})

    def do_PUT(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path

        # Update Status Endpoint
        if path.startswith('/api/complaints/admin/') and path.endswith('/status'):
            admin = self.verify_admin_auth()
            if not admin:
                return self.send_json(401, {"success": False, "message": "Admin authorization required."})

            parts = path.split('/')
            complaint_id = urllib.parse.unquote(parts[4]).strip().upper()

            body = self.parse_body()
            new_status = body.get('status')
            admin_resp = body.get('adminResponse')
            admin_notes = body.get('adminNotes')
            note = body.get('note') or f"Status changed to {new_status}."

            complaints = load_complaints()
            match = next((c for c in complaints if c.get('complaintId', '').upper() == complaint_id), None)
            if not match:
                return self.send_json(404, {"success": False, "message": "Complaint not found."})

            now_iso = datetime.now(timezone.utc).isoformat()
            if new_status:
                match["status"] = new_status
            if admin_resp is not None:
                match["adminResponse"] = admin_resp
            if admin_notes is not None:
                match["adminNotes"] = admin_notes

            match["updatedAt"] = now_iso
            if "timeline" not in match:
                match["timeline"] = []
            match["timeline"].append({
                "status": match["status"],
                "note": note,
                "updatedBy": admin["fullName"],
                "timestamp": now_iso
            })

            save_complaints(complaints)
            return self.send_json(200, {
                "success": True,
                "message": "Complaint updated successfully.",
                "complaint": match
            })

        self.send_json(404, {"success": False, "message": "Endpoint not found."})

    def do_DELETE(self):
        url_parsed = urllib.parse.urlparse(self.path)
        path = url_parsed.path

        if path.startswith('/api/complaints/admin/'):
            admin = self.verify_admin_auth()
            if not admin:
                return self.send_json(401, {"success": False, "message": "Admin authorization required."})
            complaint_id = urllib.parse.unquote(path.replace('/api/complaints/admin/', '')).strip().upper()
            complaints = load_complaints()
            orig_len = len(complaints)
            complaints = [c for c in complaints if c.get('complaintId', '').upper() != complaint_id]
            if len(complaints) == orig_len:
                return self.send_json(404, {"success": False, "message": "Complaint not found."})
            save_complaints(complaints)
            return self.send_json(200, {
                "success": True,
                "message": f"Complaint {complaint_id} has been permanently deleted."
            })

        self.send_json(404, {"success": False, "message": "Endpoint not found."})

    def serve_static(self, path):
        if path == '/' or path == '':
            file_path = os.path.join(PUBLIC_DIR, 'index.html')
        else:
            rel_path = path.lstrip('/')
            file_path = os.path.join(PUBLIC_DIR, rel_path)

        if not os.path.exists(file_path) or os.path.isdir(file_path):
            # SPA fallback: serve index.html for unknown HTML paths
            file_path = os.path.join(PUBLIC_DIR, 'index.html')

        mime_types = {
            '.html': 'text/html; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.svg': 'image/svg+xml',
            '.txt': 'text/plain; charset=utf-8',
            '.pdf': 'application/pdf'
        }

        ext = os.path.splitext(file_path)[1].lower()
        content_type = mime_types.get(ext, 'application/octet-stream')

        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_cors_headers()
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_json(500, {"success": False, "message": str(e)})

def run_server():
    server_address = ('', PORT)
    httpd = ThreadingHTTPServer(server_address, ACMSHandler)
    print("================================================================")
    print("  ANONYMOUS COMPLAINT MANAGEMENT SYSTEM (ACMS) BACKEND ACTIVE")
    print(f"  Local URL:        http://localhost:{PORT}")
    print(f"  Admin Portal:     http://localhost:{PORT}/#login")
    print(f"  Demo Admin:       {ADMIN_USER['email']} / {ADMIN_USER['password']}")
    print("================================================================")
    sys.stdout.flush()
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
