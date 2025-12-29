import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, map, throwError } from 'rxjs';
import { environment } from '../../environments/environment';

export interface AlertsSummary {
  harassment: { label: string; count: number }[];
  statuses: { [k: string]: number };
}

export interface AlertItem {
  id: number;
  type: string;
  severity_level: number;
  department?: string;
  employee?: string;
  employee_id?: number;
  message: string;
  created_at: string;
  is_resolved: boolean;
}

export interface AlertsListResponse {
  items: AlertItem[];
  total: number;
}

export interface SeedAlertsResponse {
  alert_types: { created_or_existing: { id: number; name: string; severity_level: number }[] };
  alerts: { generated: number; skipped?: number; employees_processed: number; reason?: string };
}

@Injectable({ providedIn: 'root' })
export class AlertsService {
  constructor(private http: HttpClient) {}

  private buildUrl(path: string): string {
    return environment.apiUrl ? `${environment.apiUrl}${path}` : path;
  }

  getSummary(): Observable<AlertsSummary> {
    const url = this.buildUrl('/rh/alerts/summary');
    return this.http.get<AlertsSummary>(url).pipe(
      map((res: any) => ({
        harassment: Array.isArray(res?.harassment) ? res.harassment : [],
        statuses: typeof res?.statuses === 'object' && res?.statuses ? res.statuses : {},
      })),
      catchError((err: HttpErrorResponse) => {
        // Graceful fallback to empty summary
        return throwError(() => new Error(err.message || 'Erro a carregar alertas'));
      })
    );
  }

  getRecent(limit = 20): Observable<AlertsListResponse> {
    const url = this.buildUrl(`/rh/alerts?limit=${limit}`);
    return this.http.get<AlertsListResponse>(url).pipe(
      map((res: any) => ({
        items: Array.isArray(res?.items) ? res.items : [],
        total: Number(res?.total ?? (Array.isArray(res?.items) ? res.items.length : 0)),
      })),
      catchError((err: HttpErrorResponse) => {
        return throwError(() => new Error(err.message || 'Erro a carregar alertas recentes'));
      })
    );
  }

  seedFromAssessments(): Observable<SeedAlertsResponse> {
    const url = this.buildUrl('/rh/alerts/seed');
    return this.http.post<SeedAlertsResponse>(url, {}).pipe(
      map((res: any) => ({
        alert_types: res?.alert_types || { created_or_existing: [] },
        alerts: res?.alerts || {
          generated: 0,
          skipped: 0,
          employees_processed: 0,
          reason: 'Sem dados',
        },
      })),
      catchError((err: HttpErrorResponse) => {
        return throwError(
          () => new Error(err.message || 'Erro ao gerar alertas a partir das avaliações')
        );
      })
    );
  }
}
