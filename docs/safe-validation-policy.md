# RedScope – Safe Validation Policy & Rules of Engagement

## 1. Principles of Safe Validation

RedScope enforces strict **non-destructive validation policies**. Unlike generic exploitation frameworks, RedScope's validation modules are strictly designed to **verify configuration state, header responses, and protocol attributes** without disrupting target operations or modifying remote state.

---

## 2. Permitted Check Categories

| Service | Permitted Check | Prohibited Action |
| :--- | :--- | :--- |
| **HTTP / HTTPS** | • Security headers check (`Server`, `Strict-Transport-Security`, `X-Frame-Options`)<br>• TLS redirect check<br>• Status code & server header verification<br>• Known static paths (`robots.txt`, `/favicon.ico`)<br>• Cookie security flags (`Secure`, `HttpOnly`, `SameSite`) | ❌ Brute-force / dictionary attack<br>❌ Path fuzzing / directory brute-force<br>❌ Exploitation payloads (SQLi, XSS, RCE)<br>❌ File upload attempts<br>❌ Authentication bypass attempts |
| **TLS / SSL** | • Certificate chain & expiration verification<br>• Hostname SAN match audit<br>• Protocol version support check (SSLv3, TLS 1.0, TLS 1.1, TLS 1.2, TLS 1.3)<br>• Weak cipher suite enumeration | ❌ Active handshake vulnerability stress tests<br>❌ DoS handshake flooding |
| **SSH** | • Banner string extraction<br>• Host key algorithm enumeration<br>• Key exchange (KEX) algorithm audit<br>• Passive password auth flag check | ❌ Credential guessing / brute-force<br>❌ Username enumeration exploit execution<br>❌ Active login attempts |
| **SMB** | • Protocol dialect detection (SMBv1 flag check)<br>• SMB signing requirement check<br>• Anonymous share list query (read-only metadata) | ❌ File creation, modification, or deletion<br>❌ Credential spraying / pass-the-hash<br>❌ Remote code execution (e.g. PsExec / EternalBlue) |
| **FTP** | • Server banner retrieval<br>• Anonymous login status check (read-only list command) | ❌ File upload / delete<br>❌ Password brute-force |
| **Database** | • Protocol handshake & banner query<br>• TLS requirement check | ❌ SQL query execution against application tables<br>❌ Data dumping or schema modification |

---

## 3. Mandatory Human Approval Workflow

No active validation check can be executed automatically. The system enforces a mandatory human approval workflow:

```text
Finding Identified
        ↓
Validator Available (Status: awaiting_approval)
        ↓
User Presented with Execution Dialog:
  - Target Host & Port
  - Validator Name & Description
  - Exact Network Requests Expected
  - Risk Level (Always Low/Informational)
  - Confirmation Checkbox
        ↓
User Clicks "Approve & Run Safe Validation"
        ↓
Validation Executed & Evidence Logged
```

Every approval event is permanently stored in the `AuditLog` table with the actor name, exact timestamp, target ID, and approval signature.
