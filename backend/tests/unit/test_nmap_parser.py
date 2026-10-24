import tempfile
from pathlib import Path
from app.scanners.nmap_parser import NmapXMLParser

SAMPLE_NMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE nmaprun>
<nmaprun scanner="nmap" args="nmap -sV -oX sample.xml 192.168.1.50" version="7.94">
  <host starttime="1700000000" endtime="1700000010">
    <status state="up" reason="echo-reply" reason_ttl="64"/>
    <address addr="192.168.1.50" addrtype="ipv4"/>
    <address addr="00:11:22:33:44:55" addrtype="mac" vendor="Acme Corp"/>
    <hostnames>
      <hostname name="server.lab.local" type="user"/>
    </hostnames>
    <ports>
      <port protocol="tcp" portid="80">
        <state state="open" reason="syn-ack" reason_ttl="64"/>
        <service name="http" product="nginx" version="1.22.1" extrainfo="Ubuntu" conf="10">
          <cpe>cpe:/a:nginx:nginx:1.22.1</cpe>
        </service>
      </port>
      <port protocol="tcp" portid="443">
        <state state="open" reason="syn-ack" reason_ttl="64"/>
        <service name="https" product="nginx" version="1.22.1" tunnel="ssl" conf="10">
          <cpe>cpe:/a:nginx:nginx:1.22.1</cpe>
        </service>
      </port>
    </ports>
    <os>
      <osmatch name="Linux 5.15" accuracy="98"/>
    </os>
  </host>
</nmaprun>
"""


def parse_temp_xml(content: str):
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        return NmapXMLParser.parse_xml_file(temp_path)
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_parse_sample_nmap_xml() -> None:
    parsed = parse_temp_xml(SAMPLE_NMAP_XML)
    assert len(parsed.hosts) == 1

    host = parsed.hosts[0]
    assert host.ip_address == "192.168.1.50"
    assert host.hostname == "server.lab.local"
    assert host.mac_address == "00:11:22:33:44:55"
    assert host.os_name == "Linux 5.15"
    assert len(host.services) == 2

    s80 = [s for s in host.services if s.port == 80][0]
    assert s80.protocol == "tcp"
    assert s80.service_name == "http"
    assert s80.product == "nginx"
    assert s80.version == "1.22.1"
    assert s80.cpe == "cpe:/a:nginx:nginx:1.22.1"

    s443 = [s for s in host.services if s.port == 443][0]
    assert s443.tunnel == "ssl"


def test_malformed_service_metadata_does_not_abort_host_parsing() -> None:
    malformed_xml = """<nmaprun>
      <host>
        <status state="up"/>
        <address addr="192.168.1.50" addrtype="ipv4"/>
        <ports>
          <port protocol="tcp" portid="invalid">
            <state state="open"/>
            <service name="broken"/>
          </port>
          <port protocol="tcp" portid="70000">
            <state state="open"/>
            <service name="out-of-range"/>
          </port>
          <port protocol="tcp" portid="443">
            <state state="open"/>
            <service name="https" conf="NaN"/>
          </port>
          <port protocol="tcp" portid="8443">
            <state state="open"/>
            <service name="https-alt" conf="15"/>
          </port>
        </ports>
      </host>
    </nmaprun>"""

    parsed = parse_temp_xml(malformed_xml)
    services = parsed.hosts[0].services

    assert [service.port for service in services] == [443, 8443]
    assert services[0].confidence == 0.0
    assert services[1].confidence == 1.0
