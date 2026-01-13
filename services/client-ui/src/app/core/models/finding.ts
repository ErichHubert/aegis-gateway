export type Severity = 'low' | 'medium' | 'high';

export type FindingKind = 'pii' | 'secret' | 'injection';

export interface Finding {
  start: number;
  end: number;
  severity: Severity;
  kind: FindingKind;
  label: string;
  value: string;
  description: string;
}
