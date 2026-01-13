export type ChatBot = 'echo' | 'ollama';

export interface ChatBotOption {
  id: ChatBot;
  label: string;
  description: string;
}
