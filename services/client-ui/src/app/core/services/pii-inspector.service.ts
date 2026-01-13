import { Injectable } from '@angular/core';

import { Finding, Severity } from '../models/finding';

interface PatternRule {
  label: string;
  kind: 'pii' | 'secret' | 'injection';
  severity: Severity;
  regex: RegExp;
  description: string;
}

@Injectable({
  providedIn: 'root'
})
export class PiiInspectorService {
  private readonly rules: PatternRule[] = [
    {
      label: 'Email',
      kind: 'pii',
      severity: 'medium',
      regex: /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g,
      description: 'Email address'
    },
    {
      label: 'US Phone',
      kind: 'pii',
      severity: 'low',
      regex: /\b(?:\+1\s?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g,
      description: 'Phone number'
    },
    {
      label: 'SSN',
      kind: 'pii',
      severity: 'high',
      regex: /\b\d{3}-\d{2}-\d{4}\b/g,
      description: 'US Social Security number'
    },
    {
      label: 'Access Key',
      kind: 'secret',
      severity: 'high',
      regex: /\bAKIA[0-9A-Z]{16}\b/g,
      description: 'AWS access key'
    },
    {
      label: 'Token',
      kind: 'secret',
      severity: 'medium',
      regex: /\b(?:sk-|tok_)[A-Za-z0-9]{16,}\b/g,
      description: 'API token'
    }
  ];

  inspect(text: string): Finding[] {
    if (!text) {
      return [];
    }

    const findings: Finding[] = [];

    for (const rule of this.rules) {
      const matcher = new RegExp(rule.regex.source, rule.regex.flags);
      for (const match of text.matchAll(matcher)) {
        if (match.index === undefined) {
          continue;
        }

        findings.push({
          start: match.index,
          end: match.index + match[0].length,
          severity: rule.severity,
          kind: rule.kind,
          label: rule.label,
          value: match[0],
          description: rule.description
        });
      }
    }

    return findings.sort((a, b) => a.start - b.start);
  }
}
