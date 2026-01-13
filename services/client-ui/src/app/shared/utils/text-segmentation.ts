import { Finding } from '../../core/models/finding';

export interface TextSegment {
  text: string;
  finding?: Finding;
}

export function buildSegments(text: string, findings: Finding[]): TextSegment[] {
  if (!text) {
    return [];
  }

  if (!findings || findings.length === 0) {
    return [{ text }];
  }

  const ordered = [...findings].sort((a, b) => a.start - b.start);
  const segments: TextSegment[] = [];
  let cursor = 0;

  for (const finding of ordered) {
    const start = Math.max(0, Math.min(finding.start, text.length));
    const end = Math.max(start, Math.min(finding.end, text.length));

    if (start < cursor) {
      continue;
    }

    if (start > cursor) {
      segments.push({ text: text.slice(cursor, start) });
    }

    if (end > start) {
      segments.push({ text: text.slice(start, end), finding });
      cursor = end;
    }
  }

  if (cursor < text.length) {
    segments.push({ text: text.slice(cursor) });
  }

  return segments;
}
