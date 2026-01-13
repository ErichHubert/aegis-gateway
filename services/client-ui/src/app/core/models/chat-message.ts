import { ChatBot } from './chat-bot';
import { Finding } from './finding';

export type ChatSender = 'user' | 'bot';

export interface ChatMessage {
  id: string;
  sender: ChatSender;
  text: string;
  createdAt: string;
  bot?: ChatBot;
  findings: Finding[];
}
