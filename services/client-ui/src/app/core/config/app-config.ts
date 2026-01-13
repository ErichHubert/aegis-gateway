import { InjectionToken } from '@angular/core';

export interface AppConfig {
  gatewayBaseUrl: string;
  ollamaModel: string;
}

export const APP_CONFIG = new InjectionToken<AppConfig>('app.config');
