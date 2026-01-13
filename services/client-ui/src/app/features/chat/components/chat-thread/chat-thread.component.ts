import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

import { ChatMessage } from '../../../../core/models/chat-message';

@Component({
  selector: 'app-chat-thread',
  templateUrl: './chat-thread.component.html',
  styleUrls: ['./chat-thread.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatThreadComponent {
  @Input() messages: ChatMessage[] = [];

  trackById(_index: number, message: ChatMessage): string {
    return message.id;
  }
}
