# RedScope – Threat Model & Security Controls

## 1. Security Design & Defense Strategy

Because RedScope performs network assessment tasks, the application itself must be completely resilient against security vulnerabilities such as Command Injection, Path Traversal, XML External Entity (XXE) attacks, Server-Side Request Forgery (SSRF), and Scope Bypasses.

---

## 2. Threat Matrix & Countermeasures

| Threat Category | Potential Attack Vector | RedScope Mitigation & Security Safeguard |
| :--- | :--- | :--- |
| **Command Injection** | Injecting shell metacharacters (`|`, `;`, `&&`, `$()`) into target names or custom Nmap options. | • **Zero Raw Shell Invocations**: Nmap is executed purely via `asyncio.create_subprocess_exec` using standard Python list arrays (`["nmap", "-sV", ...]`).<br>• **`shell=False` Strict Enforcement**: Shell interpretation is completely disabled.<br>• **Predefined Scan Profiles**: Users select from hardcoded scan profile templates rather than entering arbitrary Nmap flags. |
| **Scope Bypass & DNS Rebinding** | User submits a hostname that resolves to an authorized IP during scope check, but re-resolves to an out-of-scope/internal IP during scan. | • **Dual-Phase Resolution Check**: Hostnames are resolved to IP addresses at scope check time AND immediately prior to command generation.<br>• **All IPs Must Pass**: If any resolved IP fails scope matching, the target is instantly denied.<br>• **Exclusion Priority**: Excluded IPs/CIDRs override any inclusion rules. |
| **XML External Entity (XXE)** | Malicious Nmap XML output file containing `<!ENTITY>` references designed to read local files or trigger SSRF. | • **`defusedxml` Parser**: All XML parsing uses `defusedxml.ElementTree`, which explicitly disables DTD evaluation, entity expansion, and external DTD retrieval. |
| **Path Traversal** | Manipulating report export paths or Nmap XML output file paths to overwrite system files (`../../etc/passwd`). | • **UUID-Based Output Paths**: File names for scan output and generated reports use cryptographically secure random UUIDs (`scans_raw/{scan_id}.xml`).<br>• **Path Sanitization**: User input is never used directly in file paths. |
| **SSRF via Safe Validation** | Forcing safe HTTP validator plugins to request internal metadata endpoints (`169.254.169.254` or `localhost`). | • **Scope Validation Hook**: The validator engine re-runs the `ScopeValidator` prior to opening HTTP/TCP connections.<br>• **Special Range Guards**: Unless explicitly in the project's authorized scope, requests to loopback/metadata addresses are rejected. |
| **Data Leakage & Audit Tampering** | Deleting audit trail records to cover unauthorized scans. | • **Append-Only Audit Log**: Database schema enforces append-only audit log records with automated timestamps. |
