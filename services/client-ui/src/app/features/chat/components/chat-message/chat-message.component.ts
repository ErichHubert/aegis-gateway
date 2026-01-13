import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

import { ChatMessage } from '../../../../core/models/chat-message';

@Component({
  selector: 'app-chat-message',
  templateUrl: './chat-message.component.html',
  styleUrls: ['./chat-message.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatMessageComponent {
  @Input({ required: true }) message!: ChatMessage;

  get isUser(): boolean {
    return this.message.sender === 'user';
  }

  get senderLabel(): string {
    if (this.message.sender === 'user') {
      return 'You';
    }

    return this.message.bot === 'ollama' ? 'Ollama' : 'Echo';
  }
}
