import { ChangeDetectionStrategy, Component } from '@angular/core';

import { ChatFacade } from '../data-access/chat.facade';
import { ChatBot } from '../../../core/models/chat-bot';

@Component({
  selector: 'app-chat-page',
  templateUrl: './chat-page.component.html',
  styleUrls: ['./chat-page.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatPageComponent {
  readonly bots = this.facade.bots;
  readonly selectedBot$ = this.facade.selectedBot$;
  readonly messages$ = this.facade.messages$;

  constructor(private readonly facade: ChatFacade) {}

  onBotChange(bot: ChatBot): void {
    this.facade.selectBot(bot);
  }

  onSend(text: string): void {
    this.facade.send(text);
  }
}
