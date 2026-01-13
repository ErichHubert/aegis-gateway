import {
  ChangeDetectionStrategy,
  Component,
  EventEmitter,
  Input,
  OnChanges,
  Output,
  SimpleChanges
} from '@angular/core';

import { ChatBot, ChatBotOption } from '../../../../core/models/chat-bot';

@Component({
  selector: 'app-chat-bot-selector',
  templateUrl: './chat-bot-selector.component.html',
  styleUrls: ['./chat-bot-selector.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ChatBotSelectorComponent implements OnChanges {
  @Input({ required: true }) bots: ChatBotOption[] = [];
  @Input({ required: true }) selected: ChatBot = 'echo';
  @Output() selectedChange = new EventEmitter<ChatBot>();

  selectedOption?: ChatBotOption;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['bots'] || changes['selected']) {
      this.selectedOption = this.bots.find((bot) => bot.id === this.selected);
    }
  }

  onSelect(bot: ChatBot): void {
    this.selectedChange.emit(bot);
  }
}
