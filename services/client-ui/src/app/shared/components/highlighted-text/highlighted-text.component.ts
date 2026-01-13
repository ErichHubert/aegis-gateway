import {
  ChangeDetectionStrategy,
  Component,
  Input,
  OnChanges,
  SimpleChanges
} from '@angular/core';

import { Finding } from '../../../core/models/finding';
import { buildSegments, TextSegment } from '../../utils/text-segmentation';

@Component({
  selector: 'app-highlighted-text',
  templateUrl: './highlighted-text.component.html',
  styleUrls: ['./highlighted-text.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HighlightedTextComponent implements OnChanges {
  @Input({ required: true }) text = '';
  @Input() findings: Finding[] = [];

  segments: TextSegment[] = [];

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['text'] || changes['findings']) {
      this.segments = buildSegments(this.text, this.findings ?? []);
    }
  }

  tooltipFor(finding: Finding): string {
    return `${finding.label} (${finding.kind}, ${finding.severity}) - ${finding.value}`;
  }
}
