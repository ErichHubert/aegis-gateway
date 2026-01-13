import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { ChatPageComponent } from './chat-page/chat-page.component';
import { ChatThreadComponent } from './components/chat-thread/chat-thread.component';
import { ChatMessageComponent } from './components/chat-message/chat-message.component';
import { ChatComposerComponent } from './components/chat-composer/chat-composer.component';
import { ChatBotSelectorComponent } from './components/chat-bot-selector/chat-bot-selector.component';
import { HighlightedTextComponent } from '../../shared/components/highlighted-text/highlighted-text.component';

@NgModule({
  declarations: [
    ChatPageComponent,
    ChatThreadComponent,
    ChatMessageComponent,
    ChatComposerComponent,
    ChatBotSelectorComponent,
    HighlightedTextComponent
  ],
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  exports: [ChatPageComponent]
})
export class ChatModule {}
