import type { Finding } from '../types';

export function filterFindings(findings: Finding[], severity: string, query: string): Finding[] {
  const term = query.trim().toLowerCase();
  return findings.filter((finding) =>
    (severity === 'all' || finding.severity.toLowerCase() === severity.toLowerCase()) &&
    (!term || [finding.title, finding.description, finding.remediation]
      .some((value) => value?.toLowerCase().includes(term)))
  );
}
