import { HttpClient, HttpErrorResponse, HttpResponse } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable, catchError, map, of } from 'rxjs';

import { APP_CONFIG, AppConfig } from '../../../core/config/app-config';
import { ChatBot } from '../../../core/models/chat-bot';
import { Finding, Severity } from '../../../core/models/finding';

type GatewayDecision = 'allow' | 'confirm' | 'block' | 'error';

interface GatewayFinding {
  type: string;
  start: number;
  end: number;
  snippet?: string;
  message?: string;
  severity?: string;
}

interface GatewayProblemDetails {
  title?: string;
  detail?: string;
  status?: number;
  decision?: GatewayDecision;
  policyId?: string;
  confirmTtlSeconds?: number;
  findings?: GatewayFinding[];
}

export interface ChatGatewayResult {
  decision: GatewayDecision;
  responseText: string;
  findings: Finding[];
  confirmToken?: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatGatewayService {
  constructor(
    private readonly http: HttpClient,
    @Inject(APP_CONFIG) private readonly config: AppConfig
  ) {}

  sendPrompt(bot: ChatBot, prompt: string): Observable<ChatGatewayResult> {
    const requestBody =
      bot === 'ollama'
        ? { model: this.config.ollamaModel, prompt, stream: false }
        : { model: 'echo', prompt };

    return this.http
      .post(this.resolveEndpoint(bot), requestBody, {
        observe: 'response'
      })
      .pipe(
        map((response) => this.mapSuccess(response, bot)),
        catchError((error: HttpErrorResponse) => of(this.mapError(error)))
      );
  }

  private resolveEndpoint(bot: ChatBot): string {
    const baseUrl = this.config.gatewayBaseUrl.replace(/\/+$/, '');
    return bot === 'ollama' ? `${baseUrl}/api/generate` : `${baseUrl}/api/echo`;
  }

  private mapSuccess(response: HttpResponse<unknown>, bot: ChatBot): ChatGatewayResult {
    const responseText = this.extractResponseText(response.body, bot);
    return {
      decision: 'allow',
      responseText,
      findings: []
    };
  }

  private mapError(error: HttpErrorResponse): ChatGatewayResult {
    const body = this.normalizeProblemDetails(error.error);
    const decision = this.resolveDecision(body, error.status);
    const findings = this.mapFindings(body.findings ?? []);
    const confirmToken = error.headers.get('X-Aegis-Confirm-Token') ?? undefined;
    const responseText = this.buildDecisionMessage(decision, body, confirmToken);

    return {
      decision,
      responseText,
      findings,
      confirmToken
    };
  }

  private normalizeProblemDetails(payload: unknown): GatewayProblemDetails {
    if (!payload) {
      return {};
    }

    if (typeof payload === 'string') {
      return { title: payload };
    }

    if (typeof payload === 'object') {
      return payload as GatewayProblemDetails;
    }

    return { title: String(payload) };
  }

  private resolveDecision(details: GatewayProblemDetails, status: number): GatewayDecision {
    if (details.decision === 'block' || details.decision === 'confirm') {
      return details.decision;
    }

    if (status === 403) {
      return 'block';
    }

    if (status === 428) {
      return 'confirm';
    }

    return 'error';
  }

  private buildDecisionMessage(
    decision: GatewayDecision,
    details: GatewayProblemDetails,
    confirmToken?: string
  ): string {
    if (decision === 'confirm') {
      const ttl = details.confirmTtlSeconds ? `${details.confirmTtlSeconds}s` : 'soon';
      const tokenNote = confirmToken ? `Confirm token: ${confirmToken}.` : 'No confirm token returned.';
      return `${details.title ?? 'Confirmation required'}. ${details.detail ?? ''} Token expires ${ttl}. ${tokenNote}`.trim();
    }

    if (decision === 'block') {
      return `${details.title ?? 'Blocked by policy'}. ${details.detail ?? ''}`.trim();
    }

    return details.title ?? 'Gateway rejected the request.';
  }

  private extractResponseText(payload: unknown, bot: ChatBot): string {
    if (!payload) {
      return bot === 'ollama' ? 'Ollama returned an empty response.' : 'Echo returned an empty response.';
    }

    if (typeof payload === 'string') {
      return payload;
    }

    if (typeof payload === 'object') {
      const record = payload as Record<string, unknown>;
      if (typeof record['response'] === 'string') {
        return record['response'] as string;
      }

      if (typeof record['message'] === 'string') {
        return record['message'] as string;
      }

      if (typeof record['body'] === 'string') {
        return record['body'] as string;
      }

      return JSON.stringify(record, null, 2);
    }

    return String(payload);
  }

  private mapFindings(findings: GatewayFinding[]): Finding[] {
    return findings
      .filter((finding) => this.isPiiOrSecret(finding.type))
      .map((finding) => {
        const severity = this.toSeverity(finding.severity);
        if (!severity) {
          return null;
        }

        return {
          start: finding.start,
          end: finding.end,
          severity,
          kind: finding.type.startsWith('secret_') ? 'secret' : 'pii',
          label: this.toLabel(finding.type),
          value: finding.snippet ?? '',
          description: finding.message ?? finding.type
        };
      })
      .filter((finding): finding is Finding => Boolean(finding));
  }

  private isPiiOrSecret(type: string): boolean {
    return type.startsWith('pii_') || type.startsWith('secret_');
  }

  private toSeverity(value?: string): Severity | null {
    if (value === 'low' || value === 'medium' || value === 'high') {
      return value;
    }

    return null;
  }

  private toLabel(type: string): string {
    return type
      .replace(/^pii_/, '')
      .replace(/^secret_/, '')
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }
}
