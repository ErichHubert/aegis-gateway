import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

import { ChatBot, ChatBotOption } from '../../../core/models/chat-bot';
import { ChatMessage, ChatSender } from '../../../core/models/chat-message';
import { ChatGatewayService } from './chat-gateway.service';

@Injectable({
  providedIn: 'root'
})
export class ChatFacade {
  readonly bots: ChatBotOption[] = [
    {
      id: 'echo',
      label: 'Echo',
      description: 'Lightweight echo service for quick validation.'
    },
    {
      id: 'ollama',
      label: 'Ollama',
      description: 'Local LLM for richer responses.'
    }
  ];

  private readonly selectedBotSubject = new BehaviorSubject<ChatBot>('echo');
  private readonly messagesSubject = new BehaviorSubject<ChatMessage[]>([]);
  private messageId = 0;

  readonly selectedBot$ = this.selectedBotSubject.asObservable();
  readonly messages$ = this.messagesSubject.asObservable();

  constructor(private readonly gateway: ChatGatewayService) {
    this.seedConversation();
  }

  selectBot(bot: ChatBot): void {
    this.selectedBotSubject.next(bot);
  }

  send(text: string): void {
    const trimmed = text.trim();
    if (!trimmed) {
      return;
    }

    const userMessage = this.buildMessage('user', trimmed);
    this.appendMessage(userMessage);

    const bot = this.selectedBotSubject.value;
    this.gateway.sendPrompt(bot, trimmed).subscribe((result) => {
      if (result.findings.length > 0) {
        this.updateFindings(userMessage.id, result.findings);
      }

      const responseText = this.formatResponse(result.responseText, result.decision);
      this.appendMessage(this.buildMessage('bot', responseText, bot));
    });
  }

  private seedConversation(): void {
    const seed: ChatMessage[] = [
      this.buildMessage('bot', 'Welcome. Send a prompt and the gateway will decide to allow, confirm, or block.'),
      this.buildMessage('user', 'Summarize the Q3 roadmap in three bullets.'),
      this.buildMessage('bot', 'Echo: Ready when you are.')
    ];

    this.messagesSubject.next(seed);
  }

  private appendMessage(message: ChatMessage): void {
    const updated = [...this.messagesSubject.value, message];
    this.messagesSubject.next(updated);
  }

  private buildMessage(sender: ChatSender, text: string, bot?: ChatBot): ChatMessage {
    return {
      id: `msg-${++this.messageId}`,
      sender,
      text,
      bot,
      createdAt: new Date().toISOString(),
      findings: []
    };
  }

  private updateFindings(messageId: string, findings: ChatMessage['findings']): void {
    const updated = this.messagesSubject.value.map((message) =>
      message.id === messageId ? { ...message, findings } : message
    );
    this.messagesSubject.next(updated);
  }

  private formatResponse(responseText: string, decision: string): string {
    if (decision === 'allow') {
      return responseText;
    }

    return `${responseText}\n\nDecision: ${decision.toUpperCase()}`;
  }
}
