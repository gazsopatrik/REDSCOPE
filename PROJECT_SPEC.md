# REDSCOPE – TELJES FEJLESZTÉSI SPECIFIKÁCIÓ

## 1. Projektutasítás

Hozz létre teljesen a nulláról egy működő, moduláris, dokumentált kiberbiztonsági alkalmazást **RedScope** néven.

A RedScope egy engedélyezett biztonsági felmérésekhez használható vulnerability assessment és attack-surface analysis platform.

A rendszer feladata:

1. ellenőrizni, hogy a vizsgálandó célpont az engedélyezett scope-on belül található-e;
2. Nmap segítségével feltérképezni a célpont elérhető portjait;
3. azonosítani a portokon futó szolgáltatásokat, termékeket és verziókat;
4. a talált szolgáltatásokhoz ismert sebezhetőségeket rendelni;
5. a sebezhetőségeket több forrás alapján rangsorolni;
6. biztonságos, nem destruktív validációs ellenőrzéseket javasolni;
7. kizárólag felhasználói jóváhagyás után futtatni az engedélyezett biztonságos ellenőrzéseket;
8. részletes, visszakövethető riportot készíteni;
9. minden műveletet naplózni;
10. megakadályozni a nem engedélyezett célpontok vizsgálatát.

A szoftver nem lehet általános célú automatikus exploitációs keretrendszer.

A rendszer ne indítson automatikusan sérülékenységet kihasználó támadásokat, ne telepítsen payloadot, ne nyisson shellt, ne módosítson adatot, ne hajtson végre jogosultságkiterjesztést és ne próbáljon tartós hozzáférést létrehozni.

A projekt fő célja egy professzionális, portfólióképes, biztonságos red-team és vulnerability assessment eszköz létrehozása.

---

# 2. Alapvető működési folyamat

A program fő működése:

```text
Projekt létrehozása
        ↓
Scope meghatározása
        ↓
Célpont hozzáadása
        ↓
Scope-validáció
        ↓
Nmap felderítés
        ↓
Nmap XML feldolgozása
        ↓
Hostok, portok és szolgáltatások azonosítása
        ↓
Szolgáltatásadatok normalizálása
        ↓
CVE-k és biztonsági információk keresése
        ↓
Kockázati pontszám kiszámítása
        ↓
Találatok rangsorolása
        ↓
Biztonságos validációs javaslatok
        ↓
Felhasználói jóváhagyás
        ↓
Engedélyezett validációk futtatása
        ↓
Eredmények újraértékelése
        ↓
HTML / JSON / Markdown riport
```

---

# 3. Javasolt technológiai stack

## Backend

- Python 3.12 vagy újabb stabil Python 3 verzió
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- SQLite fejlesztői és tesztkörnyezethez
- Celery vagy RQ a hosszabb háttérfeladatok kezeléséhez
- Redis a feladatsorhoz
- pytest
- httpx
- defusedxml vagy más biztonságos XML-parser
- Jinja2 a HTML-riportokhoz

## Frontend

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- egyszerű, saját komponensrendszer vagy könnyű UI-könyvtár
- reszponzív, sötét témájú kezelőfelület

## Külső eszközök

- Nmap
- opcionálisan Docker
- opcionálisan Docker Compose
- Git
- pre-commit
- Ruff
- mypy

A projekt elsődleges verziója helyileg fusson.

Ne legyen szükség felhőszolgáltatásra az alapfunkciók használatához.

---

# 4. Projektstruktúra

Javasolt monorepo-struktúra:

```text
redscope/
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Makefile
│
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── logging_config.py
│   │   │
│   │   ├── api/
│   │   │   ├── router.py
│   │   │   ├── projects.py
│   │   │   ├── scopes.py
│   │   │   ├── targets.py
│   │   │   ├── scans.py
│   │   │   ├── findings.py
│   │   │   ├── validations.py
│   │   │   ├── reports.py
│   │   │   └── health.py
│   │   │
│   │   ├── models/
│   │   │   ├── project.py
│   │   │   ├── scope.py
│   │   │   ├── target.py
│   │   │   ├── scan.py
│   │   │   ├── host.py
│   │   │   ├── service.py
│   │   │   ├── vulnerability.py
│   │   │   ├── finding.py
│   │   │   ├── validation.py
│   │   │   ├── report.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── project.py
│   │   │   ├── scope.py
│   │   │   ├── target.py
│   │   │   ├── scan.py
│   │   │   ├── finding.py
│   │   │   ├── validation.py
│   │   │   └── report.py
│   │   │
│   │   ├── scanners/
│   │   │   ├── base.py
│   │   │   ├── nmap_runner.py
│   │   │   ├── nmap_parser.py
│   │   │   └── scan_profiles.py
│   │   │
│   │   ├── scope/
│   │   │   ├── validator.py
│   │   │   ├── resolver.py
│   │   │   └── authorization.py
│   │   │
│   │   ├── intelligence/
│   │   │   ├── cve_provider.py
│   │   │   ├── cpe_matcher.py
│   │   │   ├── epss_provider.py
│   │   │   ├── kev_provider.py
│   │   │   ├── exploit_metadata.py
│   │   │   └── cache.py
│   │   │
│   │   ├── scoring/
│   │   │   ├── risk_engine.py
│   │   │   ├── confidence.py
│   │   │   └── severity.py
│   │   │
│   │   ├── validators/
│   │   │   ├── base.py
│   │   │   ├── registry.py
│   │   │   ├── http/
│   │   │   ├── tls/
│   │   │   ├── ssh/
│   │   │   ├── smb/
│   │   │   ├── ftp/
│   │   │   └── database/
│   │   │
│   │   ├── reporting/
│   │   │   ├── html_report.py
│   │   │   ├── json_report.py
│   │   │   ├── markdown_report.py
│   │   │   └── templates/
│   │   │
│   │   ├── services/
│   │   │   ├── project_service.py
│   │   │   ├── scan_service.py
│   │   │   ├── analysis_service.py
│   │   │   ├── validation_service.py
│   │   │   └── report_service.py
│   │   │
│   │   ├── workers/
│   │   │   ├── tasks.py
│   │   │   └── worker.py
│   │   │
│   │   └── security/
│   │       ├── command_policy.py
│   │       ├── input_validation.py
│   │       ├── rate_limits.py
│   │       └── safe_execution.py
│   │
│   ├── migrations/
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── fixtures/
│
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       ├── components/
│       ├── pages/
│       ├── hooks/
│       ├── types/
│       └── utils/
│
├── docs/
│   ├── architecture.md
│   ├── threat-model.md
│   ├── safe-validation-policy.md
│   ├── api.md
│   └── development.md
│
└── scripts/
    ├── install_nmap.sh
    ├── seed_demo_data.py
    └── run_dev.sh
```

---

# 5. Fő entitások és adatmodellek

## 5.1 Project

Egy biztonsági felméréshez tartozó projekt.

Mezők:

```text
id
name
description
client_name
created_at
updated_at
status
authorization_reference
rules_of_engagement
created_by
```

A `status` értékei:

```text
draft
active
paused
completed
archived
```

## 5.2 Scope

Meghatározza, hogy milyen célpontok vizsgálhatók.

Mezők:

```text
id
project_id
scope_type
value
description
enabled
created_at
```

Támogatott scope-típusok:

```text
single_ip
cidr
hostname
domain
```

Példák:

```text
192.168.56.10
192.168.56.0/24
server.lab.local
lab.local
```

A kizárásokat külön kell kezelni.

Példa:

```text
include: 192.168.56.0/24
exclude: 192.168.56.1
exclude: 192.168.56.254
```

## 5.3 Target

A ténylegesen vizsgálandó célpont.

Mezők:

```text
id
project_id
target_value
resolved_addresses
target_type
scope_status
scope_validation_message
created_at
last_scanned_at
```

A `scope_status` lehetséges értékei:

```text
pending
allowed
denied
resolution_failed
```

Scope-on kívüli célpontra semmilyen scan nem indítható.

## 5.4 Scan

Egy konkrét felderítési művelet.

Mezők:

```text
id
project_id
target_id
profile
status
command_preview
started_at
finished_at
exit_code
error_message
raw_output_path
xml_output_path
created_by
```

Scan státuszok:

```text
queued
running
parsing
analyzing
completed
failed
cancelled
```

## 5.5 Host

Egy scan során észlelt host.

Mezők:

```text
id
scan_id
ip_address
hostname
mac_address
vendor
state
os_name
os_accuracy
latency
```

## 5.6 Service

Egy nyitott porton azonosított szolgáltatás.

Mezők:

```text
id
host_id
protocol
port
state
service_name
product
version
extra_info
tunnel
method
confidence
cpe
banner
```

Példa:

```json
{
  "protocol": "tcp",
  "port": 443,
  "state": "open",
  "service_name": "https",
  "product": "nginx",
  "version": "1.22.1",
  "tunnel": "ssl",
  "confidence": 0.91
}
```

## 5.7 Vulnerability

Külső forrásból származó sebezhetőségi adat.

Mezők:

```text
id
cve_id
title
description
cvss_score
cvss_vector
severity
published_at
modified_at
cwe_ids
references
known_exploited
epss_score
epss_percentile
public_exploit_metadata
```

A `public_exploit_metadata` nem tartalmazhat automatikusan futtatható támadási kódot.

Csak metaadatot tároljon, például:

```text
public_poc_known
framework_reference_known
exploit_maturity
source_name
source_url
```

## 5.8 Finding

Egy szolgáltatás és egy lehetséges vagy validált biztonsági probléma kapcsolata.

Mezők:

```text
id
service_id
vulnerability_id
title
description
status
severity
risk_score
confidence_score
match_method
evidence
remediation
false_positive_reason
created_at
updated_at
```

Finding státuszok:

```text
suspected
candidate
validation_available
validation_pending
validated
not_vulnerable
false_positive
accepted_risk
remediated
```

## 5.9 Validation

Egy biztonságos ellenőrzési művelet.

Mezők:

```text
id
finding_id
validator_id
validator_name
risk_level
status
requires_approval
approved_by
approved_at
started_at
finished_at
result
evidence
error_message
```

Validation státuszok:

```text
available
awaiting_approval
approved
running
passed
failed
inconclusive
blocked
cancelled
```

## 5.10 AuditLog

Minden fontos eseményt naplózni kell.

Mezők:

```text
id
timestamp
actor
action
entity_type
entity_id
project_id
details
source_ip
```

Naplózandó események:

- projekt létrehozása;
- scope módosítása;
- célpont hozzáadása;
- scope-validáció;
- scan indítása;
- scan leállítása;
- validation jóváhagyása;
- validation futtatása;
- finding státuszának módosítása;
- riport generálása;
- hibák és tiltott műveletek.

---

# 6. Scope-kezelés

A scope-kezelés kritikus biztonsági komponens.

Minden scan és validation előtt újra ellenőrizni kell a scope-ot.

A scope-validátor feladata:

1. IP-cím validálása;
2. CIDR-tartomány kezelése;
3. hostname feloldása;
4. domain és subdomain szabályok kezelése;
5. kizárt IP-k és hostnevek kezelése;
6. IPv4 és IPv6 támogatása;
7. DNS-rebinding és feloldási változások figyelembevétele;
8. privát, lokális és publikus címek megkülönböztetése;
9. localhost és speciális címek kezelése;
10. minden döntés naplózása.

Hostname használatakor a rendszer:

- oldja fel a hostname-et;
- tárolja az összes kapott IP-címet;
- ellenőrizze mindegyik címet;
- ne engedje a műveletet, ha bármelyik feloldott cím scope-on kívül van;
- a művelet előtt ismételje meg a DNS-feloldást.

A felhasználói felületen egyértelműen jelenjen meg:

```text
SCOPE VALIDÁLVA
vagy
SCOPE ELUTASÍTVA
```

Scope elutasítása esetén az indoklás is jelenjen meg.

---

# 7. Scan-profilok

Ne engedj tetszőleges, nyers Nmap-parancsot megadni a webes felületen.

Előre definiált scan-profilok legyenek.

## 7.1 Quick Discovery

Cél:

- host elérhetőségének gyors ellenőrzése;
- leggyakoribb portok vizsgálata;
- alap szolgáltatásdetektálás.

## 7.2 Standard Service Scan

Cél:

- TCP-portok szélesebb vizsgálata;
- szolgáltatás- és verziódetektálás;
- biztonságos alapértelmezett időzítés.

## 7.3 Full TCP Scan

Cél:

- mind a 65 535 TCP-port vizsgálata;
- szolgáltatásdetektálás;
- hosszabb futási idő;
- külön megerősítést igényeljen.

## 7.4 Selected Ports

A felhasználó portlistát adhat meg, például:

```text
22,80,443,445,3389
```

A bemenetet szigorúan validálni kell.

## 7.5 UDP Common Services

Csak a leggyakoribb UDP-portok vizsgálata.

A felületen jelenjen meg, hogy az UDP-scan lassú és bizonytalanabb lehet.

---

# 8. Nmap futtatása

Az Nmap-et kizárólag biztonságos subprocess-hívással szabad futtatni.

Tilos:

- `shell=True`;
- nyers felhasználói string parancsként történő továbbítása;
- felhasználó által megadott önkényes Nmap-argumentumok használata;
- parancsösszefűzés;
- shell metakarakterek elfogadása.

A parancs argumentumlistából épüljön fel.

Példa:

```python
command = [
    "nmap",
    "-sV",
    "--version-light",
    "--open",
    "-T3",
    "-oX",
    xml_output_path,
    target,
]
```

Minden scan előtt:

1. scope-ellenőrzés;
2. target normalizálása;
3. profil validálása;
4. parancs előnézetének generálása;
5. auditnapló létrehozása.

A futtatás kapjon:

- timeoutot;
- CPU- és memóriahasználati korlátot, ahol lehetséges;
- leállítási lehetőséget;
- biztonságos munkakönyvtárat;
- egyedi kimeneti fájlnevet.

---

# 9. Nmap XML feldolgozás

Az XML-parser olvassa ki:

- host állapot;
- IP-cím;
- hostname;
- port;
- protokoll;
- port állapot;
- szolgáltatásnév;
- termék;
- verzió;
- extra információ;
- CPE;
- SSL/TLS tunnel;
- operációsrendszer-becslés;
- Nmap confidence adatok;
- script output kizárólag engedélyezett scriptek esetén.

A parser legyen robusztus:

- hiányzó mezők;
- hibás XML;
- félbeszakadt scan;
- ismeretlen attribútumok;
- több host;
- IPv4 és IPv6;
- ismétlődő szolgáltatások;
- eltérő Nmap-verziók.

A parserhez részletes unit teszteket kell írni.

---

# 10. Szolgáltatás-normalizálás

Az Nmap eredménye gyakran nem egységes.

Példák:

```text
Apache httpd 2.4.57
Apache/2.4.57
apache http server 2.4.57
```

Ezeket egységes modellre kell alakítani.

Normalizált mezők:

```text
vendor
product
version
edition
platform
cpe
confidence
```

A normalizálás szabályalapú legyen.

Ne használjon találomra generált CPE-t magas bizonyossággal.

A CPE-match kapjon confidence score-t:

```text
exact
high
medium
low
unknown
```

---

# 11. Vulnerability intelligence

A rendszer a szolgáltatáshoz kapcsolható sebezhetőségeket keressen.

A keresési sorrend:

1. pontos CPE-egyezés;
2. vendor + product + version;
3. product + version;
4. product alapú, alacsonyabb bizonyosságú találatok.

A rendszer külön kezelje:

- pontos verzióegyezés;
- verziótartomány-egyezés;
- bizonytalan verzió;
- ismeretlen verzió;
- backportolt biztonsági javítások lehetősége.

Fontos:

Egy szolgáltatás bannerében látható verzió önmagában nem bizonyítja, hogy a célpont sebezhető.

Minden CVE-kapcsolat findingként először csak:

```text
candidate
vagy
suspected
```

állapotot kapjon.

---

# 12. Kockázati pontozás

Minden finding kapjon:

- technikai súlyossági pontszámot;
- kihasználási valószínűséget;
- találati bizonyosságot;
- kitettségi pontszámot;
- végső prioritási pontszámot.

A végső pontszám 0 és 100 közötti érték legyen.

Javasolt képlet:

```text
risk_score =
    cvss_component
  + epss_component
  + kev_component
  + match_confidence_component
  + exposure_component
  + exploit_maturity_component
  + validation_component
```

Javasolt súlyok:

```text
CVSS:                 25 pont
EPSS:                 20 pont
KEV státusz:          15 pont
Match confidence:     15 pont
Kitettség:            10 pont
Exploit maturity:      5 pont
Validation evidence:  10 pont
```

Prioritási kategóriák:

```text
0–19   Informational
20–39  Low
40–59  Medium
60–79  High
80–100 Critical
```

A pontszám mellett minden esetben jelenjen meg szöveges indoklás.

---

# 13. Confidence score

A risk score és confidence score két külön érték legyen.

Példa:

```text
Risk: 91/100
Confidence: 42/100
```

Confidence növelő tényezők:

- pontos CPE;
- pontos verzió;
- több független azonosítási módszer;
- biztonságos validáció pozitív eredménye;
- hitelesített scan;
- megbízható banner.

Confidence csökkentő tényezők:

- hiányzó verzió;
- generikus service name;
- reverse proxy;
- load balancer;
- backport lehetősége;
- csak portszám alapján történt becslés;
- ellentmondó fingerprint.

---

# 14. Biztonságos validációs rendszer

A rendszer támogasson plugin-alapú validatorokat.

Minden validator rendelkezzen a következő metaadatokkal:

```text
id
name
description
supported_services
risk_level
requires_approval
timeout
network_requests
destructive
authentication_required
```

A `destructive` mező minden MVP-validator esetén legyen `false`.

Validator interface:

```python
class BaseValidator:
    id: str
    name: str
    description: str
    risk_level: str
    requires_approval: bool
    destructive: bool = False

    def supports(self, service, finding) -> bool:
        ...

    async def validate(self, context) -> ValidationResult:
        ...
```

A `ValidationResult` tartalmazza:

```text
status
summary
evidence
confidence_delta
risk_delta
raw_metadata
started_at
finished_at
```

---

# 15. Engedélyezett validációs kategóriák

## HTTP és HTTPS

Engedélyezett:

- HTTP status code lekérése;
- response headerek elemzése;
- `Server` header vizsgálata;
- biztonsági headerek ellenőrzése;
- TLS használat ellenőrzése;
- redirect chain vizsgálata;
- robots.txt lekérése;
- favicon és title lekérése;
- OPTIONS kérés, ha biztonságos;
- alapértelmezett oldalak felismerése;
- publikus, autentikáció nélküli health endpoint észlelése;
- directory listing felismerése, kizárólag ismert útvonal közvetlen lekérésével;
- cookie security attribútumok ellenőrzése.

Nem engedélyezett:

- jelszópróba;
- fuzzing;
- tömeges útvonalbejárás;
- SQL injection payloadok;
- XSS payloadok;
- file upload teszt;
- SSRF teszt;
- RCE payload;
- hitelesítés megkerülése;
- aktív exploitáció.

## TLS

Engedélyezett:

- tanúsítványadatok;
- lejárati idő;
- hostname-egyezés;
- támogatott protokollok;
- gyenge protokollok;
- alap cipher információ;
- self-signed certificate észlelése;
- certificate chain vizsgálata.

## SSH

Engedélyezett:

- banner lekérése;
- verzió azonosítása;
- host key algoritmusok lekérdezése;
- támogatott kulcscsere-algoritmusok lekérdezése;
- gyenge algoritmusok jelzése;
- jelszavas autentikáció engedélyezettségének passzív megállapítása, ha lehetséges.

Nem engedélyezett:

- jelszópróba;
- brute force;
- felhasználónév-enumeráció aktív kihasználása;
- hitelesítési kísérletek.

## SMB

Engedélyezett:

- SMB dialect azonosítása;
- SMBv1 támogatás ellenőrzése;
- signing állapot ellenőrzése;
- guest vagy anonymous kapcsolat biztonságos ellenőrzése;
- publikus megosztások listázása, ha anonim hozzáférés engedélyezett;
- szerverazonosító információk lekérése.

Nem engedélyezett:

- fájl létrehozása;
- fájl módosítása;
- fájl törlése;
- credential guessing;
- relay támadás;
- exploit futtatása;
- távoli parancsvégrehajtás.

## FTP

Engedélyezett:

- banner lekérése;
- anonymous login biztonságos ellenőrzése;
- könyvtárlista lekérése anonymous hozzáféréssel;
- TLS támogatás ellenőrzése.

Nem engedélyezett:

- fájlfeltöltés;
- fájltörlés;
- brute force;
- exploitáció.

## Adatbázisok

Engedélyezett:

- banner;
- protokollazonosítás;
- TLS támogatás;
- anonymous vagy üres hitelesítés nélküli kapcsolódás kizárólag akkor, ha a protokoll ezt alapból biztonságosan jelzi.

Nem engedélyezett:

- lekérdezések futtatása érzékeny táblák ellen;
- adatdump;
- jelszópróba;
- adatváltoztatás;
- parancsvégrehajtás.

---

# 16. Jóváhagyási folyamat

Minden aktív validation előtt jelenjen meg:

```text
Validator neve
Célpont
Port
Protokoll
Művelet pontos leírása
Várható hálózati kérések száma
Kockázati szint
Timeout
Adatváltoztatás történik-e
Hitelesítést próbál-e
```

A felhasználónak külön jóvá kell hagynia.

A jóváhagyási gomb szövege:

```text
Jóváhagyom a biztonságos validáció futtatását
```

Lehetőség legyen több alacsony kockázatú validation csoportos jóváhagyására, de:

- a célpontok láthatók legyenek;
- a validatorok láthatók legyenek;
- a kockázati szint látható legyen;
- a jóváhagyás naplózásra kerüljön.

---

# 17. Felhasználói felület

A UI legyen modern, sötét témájú, technikai, de jól olvasható.

Ne legyen túlzott hackerfilm-hatás.

Fő navigáció:

```text
Dashboard
Projects
Targets
Scans
Findings
Validations
Reports
Audit Log
Settings
```

---

# 18. Dashboard

A dashboard mutassa:

- aktív projektek száma;
- targetek száma;
- befejezett scanek száma;
- futó scanek száma;
- critical findingok;
- high findingok;
- validált findingok;
- bizonytalan találatok;
- legutóbbi események;
- prioritási megoszlás;
- leginkább kitett szolgáltatások.

Grafikonok:

- findingok severity szerint;
- findingok státusz szerint;
- portok gyakorisága;
- szolgáltatások gyakorisága;
- scanek időbeli alakulása.

---

# 19. Projektoldal

A projektoldal tartalmazza:

- projekt neve;
- ügyfél vagy labor neve;
- státusz;
- rules of engagement;
- authorization reference;
- létrehozás dátuma;
- utolsó scan;
- összes target;
- összes finding;
- scope;
- targetek;
- scanek;
- findingok.

---

# 20. Új scan indítása

Az új scan képernyő tartalmazza:

```text
Projekt
Target
Scanprofil
Portbeállítás
Időkorlát
Megjegyzés
```

Indítás előtt jelenjen meg:

```text
Target: 192.168.56.20
Scope: engedélyezett
Profil: Standard Service Scan
Várható művelet: TCP szolgáltatásfelderítés
Adatváltoztatás: nem
```

---

# 21. Scan részletező oldal

Mutassa:

- státusz;
- progress;
- indítás ideje;
- eltelt idő;
- célpont;
- scanprofil;
- parancs biztonságos előnézete;
- aktuális feldolgozási fázis;
- felfedezett hostok;
- nyitott portok;
- logok;
- hibák.

Fázisok:

```text
Scope validation
Preparing scan
Running Nmap
Parsing results
Normalizing services
Matching vulnerabilities
Calculating risk
Completed
```

---

# 22. Finding lista

Oszlopok:

```text
Priority
Severity
Confidence
Target
Port
Service
Finding
CVE
KEV
EPSS
Status
Validation
```

Szűrés és rendezés legyen elérhető projekt, target, severity, confidence, státusz, port, szolgáltatás, CVE, KEV, validation, risk score, CVSS és EPSS szerint.

---

# 23. Finding részletező oldal

Tartalmazza:

- címet;
- targetet;
- portot;
- szolgáltatást;
- risk score-t;
- confidence score-t;
- severity-t;
- státuszt;
- emberileg olvasható indoklást;
- bizonyítékot;
- CVE-, CVSS-, EPSS-, KEV- és CWE-adatokat;
- biztonságos validációs lehetőségeket;
- konkrét remediation javaslatot.

---

# 24. Riportok

Támogatott formátumok:

- HTML;
- JSON;
- Markdown.

A riport tartalmazza:

1. címlap;
2. projektadatok;
3. scope;
4. módszertan;
5. korlátozások;
6. vezetői összefoglaló;
7. technikai összefoglaló;
8. targetlista;
9. szolgáltatások;
10. findingok prioritási sorrendben;
11. bizonyítékok;
12. validációs eredmények;
13. remediation javaslatok;
14. false positive és elfogadott kockázatok;
15. auditálható scaninformációk.

---

# 25. API-végpontok

```text
GET    /api/health
GET    /api/projects
POST   /api/projects
GET    /api/projects/{id}
PATCH  /api/projects/{id}
DELETE /api/projects/{id}
GET    /api/projects/{id}/scopes
POST   /api/projects/{id}/scopes
PATCH  /api/scopes/{id}
DELETE /api/scopes/{id}
GET    /api/projects/{id}/targets
POST   /api/projects/{id}/targets
GET    /api/targets/{id}
POST   /api/targets/{id}/validate-scope
GET    /api/projects/{id}/scans
POST   /api/projects/{id}/scans
GET    /api/scans/{id}
POST   /api/scans/{id}/cancel
GET    /api/projects/{id}/findings
GET    /api/findings/{id}
PATCH  /api/findings/{id}
GET    /api/findings/{id}/validations
POST   /api/findings/{id}/validations
POST   /api/validations/{id}/approve
POST   /api/validations/{id}/run
POST   /api/validations/{id}/cancel
POST   /api/projects/{id}/reports
GET    /api/reports/{id}
GET    /api/reports/{id}/download
GET    /api/projects/{id}/audit-logs
```

---

# 26. Biztonsági követelmények

Kötelező:

- scope-on kívüli scan tiltása;
- minden validation előtt scope újraellenőrzése;
- shell command injection megakadályozása;
- biztonságos subprocess;
- fix scanprofilok;
- timeout;
- request rate limit;
- célpontonkénti concurrency limit;
- globális concurrency limit;
- maximális targetszám;
- maximális CIDR-méret;
- auditnapló;
- titkok `.env` fájlban;
- érzékeny adatok maszkolása;
- biztonságos fájlnevek;
- path traversal elleni védelem;
- XML entity támadások elleni védelem;
- SSRF-védelem;
- inputvalidáció;
- szigorú CORS;
- production módban debug kikapcsolása.

Tiltott funkciók:

- automatikus exploit futtatás;
- Metasploit modul automatikus indítása;
- payload generálás;
- reverse shell;
- bind shell;
- credential dumping;
- brute force;
- password spraying;
- phishing;
- malware;
- persistence;
- privilege escalation;
- lateral movement;
- adatlopás;
- fájlmódosítás;
- destruktív teszt;
- denial-of-service;
- WAF megkerülés;
- exploit chain automatikus összeállítása.

---

# 27. Lab mode

Később létrehozható külön `Lab Mode`, amely csak előre konfigurált helyi laborhálózaton működik.

Az MVP-ben a Lab Mode is csak további biztonságos validációkat engedjen, ne automatikus exploitációt.

---

# 28. Hibakezelés

A rendszer kezelje:

- nincs telepítve az Nmap;
- nincs jogosultság;
- target nem oldható fel;
- target scope-on kívül van;
- Nmap timeout;
- megszakított scan;
- hibás XML;
- külső CVE-forrás nem elérhető;
- rate limit;
- adatbázishiba;
- validator timeout;
- hálózati kapcsolat megszakad;
- target scan közben elérhetetlenné válik.

A frontend ne jelenítsen meg teljes stack trace-t.

---

# 29. Tesztelési követelmények

Unit tesztek:

- IP- és CIDR-validálás;
- exclusion kezelés;
- hostname feloldás;
- scope-döntés;
- portlista parser;
- scanprofil generálás;
- Nmap command builder;
- XML-parser;
- service normalizer;
- CPE matcher;
- risk score;
- confidence score;
- validation registry;
- riportgenerálás.

Integrációs tesztek:

- projekt létrehozása;
- scope hozzáadása;
- target hozzáadása;
- engedélyezett és tiltott scan;
- mock Nmap output feldolgozása;
- finding generálás;
- validation jóváhagyása és futtatása;
- riport export.

Biztonsági tesztek:

- command injection;
- path traversal;
- XML entity attack;
- túl nagy CIDR;
- tiltott target;
- DNS-feloldás változása;
- hibás portlista;
- túl hosszú input;
- párhuzamos scan limit;
- approval megkerülési kísérlet.

---

# 30. Demo-adatok

Készüljön demo seed script `Demo Lab` projekttel, helyi scope-pal, két targettel, mock scanekkel, HTTP/SSH/SMB szolgáltatásokkal és példafindingokkal.

Minden demo-adat legyen megjelölve:

```text
DEMO DATA – NOT A REAL SECURITY ASSESSMENT
```

---

# 31. README követelmények

A README tartalmazza:

1. projekt bemutatása;
2. funkciólista;
3. biztonsági modell;
4. telepítés;
5. fejlesztői indítás;
6. Docker-indítás;
7. Nmap telepítése;
8. adatbázis-migráció;
9. tesztek futtatása;
10. korlátozások;
11. jogi és etikai figyelmeztetés;
12. roadmap.

Jogi figyelmeztetés:

```text
A RedScope kizárólag olyan rendszerek vizsgálatára használható,
amelyek tesztelésére a felhasználó kifejezett engedéllyel rendelkezik.
A felhasználó felelőssége a szükséges felhatalmazás és scope biztosítása.
```

---

# 32. Fejlesztési fázisok

## 1. fázis – Alap projekt

- backend és frontend létrehozása;
- konfiguráció;
- adatbázis;
- migráció;
- health endpoint;
- Docker Compose;
- alap README.

## 2. fázis – Projektek és scope

- Project CRUD;
- Scope CRUD;
- target hozzáadása;
- scope-validátor;
- auditlog.

## 3. fázis – Nmap integráció

- scanprofilok;
- biztonságos command builder;
- Nmap runner;
- scan státusz;
- XML mentése;
- XML-parser.

## 4. fázis – Hostok és szolgáltatások

- host modellek;
- service modellek;
- normalizálás;
- szolgáltatáslista UI;
- scan részletező oldal.

## 5. fázis – Vulnerability intelligence

- provider interface;
- CVE-cache;
- CPE matching;
- EPSS;
- KEV;
- finding generálás.

## 6. fázis – Scoring

- risk engine;
- confidence engine;
- prioritási lista;
- emberileg olvasható indoklás.

## 7. fázis – Safe validation

- validator interface;
- registry;
- approval workflow;
- HTTP validator;
- TLS validator;
- SSH validator;
- SMB validator;
- auditálás.

## 8. fázis – Riport

- HTML;
- JSON;
- Markdown;
- finding evidence;
- remediation.

## 9. fázis – Minőségbiztosítás

- unit tesztek;
- integrációs tesztek;
- security tesztek;
- dokumentáció;
- kódminőség;
- hibakezelés.

---

# 33. Első MVP elfogadási feltételei

Az MVP akkor tekinthető késznek, ha:

1. új projekt létrehozható;
2. CIDR és IP scope megadható;
3. target hozzáadható;
4. scope-on kívüli target blokkolva van;
5. engedélyezett target ellen Nmap scan indítható;
6. a scan XML-formátumban mentésre kerül;
7. a nyitott portok megjelennek;
8. a szolgáltatások és verziók megjelennek;
9. a szolgáltatásokhoz mock vagy valós CVE-adatok kapcsolhatók;
10. minden finding kap risk és confidence score-t;
11. a findingok prioritási sorrendben jelennek meg;
12. legalább HTTP- és TLS-validáció működik;
13. a validation felhasználói jóváhagyást igényel;
14. minden fontos művelet auditálva van;
15. HTML-riport generálható;
16. a rendszer semmilyen automatikus exploitációt nem hajt végre;
17. a backend tesztjei sikeresen lefutnak;
18. a projekt Docker Compose segítségével elindítható;
19. a README alapján egy új fejlesztő telepíteni tudja;
20. a felület használható desktop méretben.

---

# 34. Kódminőségi elvárások

- teljes type hinting;
- Pydantic modellek;
- kis, jól tesztelhető függvények;
- dependency injection;
- ne legyen üzleti logika az API route-okban;
- ne legyen duplikált kód;
- jól elnevezett osztályok és függvények;
- strukturált logging;
- egységes error response;
- konfiguráció környezeti változókból;
- fejlesztői és production konfiguráció külön;
- linting;
- formatting;
- type checking;
- tesztlefedettség mérése.

---

# 35. Fontos fejlesztési szabályok a Codex számára

A fejlesztést teljesen új projektként kezeld.

Ne feltételezd, hogy létezik korábbi kódbázis.

Ne próbáld egyszerre elkészíteni az összes funkciót egyetlen hatalmas fájlban.

Először készíts stabil architektúrát és működő MVP-t.

Minden fejlesztési fázis után:

1. futtasd a lintet;
2. futtasd a type checket;
3. futtasd a teszteket;
4. javítsd ki a hibákat;
5. frissítsd a dokumentációt.

Ne hagyj üres vagy félkész placeholder funkciókat magyarázat nélkül.

Ha egy külső adatforrás még nincs bekötve, készíts tiszta provider interface-t és dokumentált mock providert.

Ne adj hozzá támadó vagy destruktív funkciót arra hivatkozva, hogy az később hasznos lehet.

A rendszer központi alapelve:

```text
Discover → Understand → Prioritize → Safely Validate → Report
```

Nem:

```text
Discover → Automatically Exploit
```

---

# 36. Az első konkrét fejlesztési feladat

Első lépésként:

1. hozd létre a teljes projektkönyvtár-struktúrát;
2. inicializáld a Python FastAPI backendet;
3. inicializáld a React TypeScript frontendet;
4. készíts Docker Compose konfigurációt PostgreSQL és Redis szolgáltatással;
5. készíts `.env.example` fájlt;
6. hozd létre az alap SQLAlchemy konfigurációt;
7. állítsd be az Alembic migrációt;
8. készíts `/api/health` endpointot;
9. készíts egyszerű dashboard oldalt;
10. írd meg a README első változatát;
11. állítsd be a Ruff, mypy és pytest eszközöket;
12. készíts alap CI-kompatibilis tesztparancsokat;
13. futtasd a teszteket;
14. dokumentáld, hogyan indítható el a projekt.

Ezután kezdd el a Project, Scope és Target modellek implementációját.

A munka során mindig mutasd meg:

- milyen fájlokat hoztál létre;
- milyen döntéseket hoztál;
- milyen teszteket futtattál;
- mi működik;
- mi maradt hátra;
- mi a következő fejlesztési lépés.
