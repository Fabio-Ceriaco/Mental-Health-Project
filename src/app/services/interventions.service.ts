import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, map, throwError } from 'rxjs';
import { environment } from '../../environments/environment';

export interface InterventionCase {
  id: number;
  employee_id: number;
  employee_name: string;
  intervention_action_name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface InterventionsListResponse {
  items: InterventionCase[];
  total: number;
}

export interface InterventionCreateInput {
  employee_id: number;
  description: string;
  intervention_action_id?: number | null;
}

@Injectable({ providedIn: 'root' })
export class InterventionsService {
  constructor(private http: HttpClient) {}

  private buildUrl(path: string): string {
    return environment.apiUrl ? `${environment.apiUrl}${path}` : path;
  }

  getAll(): Observable<InterventionsListResponse> {
    const url = this.buildUrl('/psychologist/interventions');
    return this.http.get<InterventionsListResponse>(url).pipe(
      map((res: any) => {
        const result = {
          items: Array.isArray(res?.items) ? res.items : [],
          total: Number(res?.total ?? (Array.isArray(res?.items) ? res.items.length : 0)),
        };
        return result;
      }),
      catchError((err: HttpErrorResponse) => {
        console.error('[InterventionsService] HTTP Error:', err.status, err.message);
        return throwError(() => new Error(err.message || 'Erro a carregar intervenções'));
      })
    );
  }

  create(payload: InterventionCreateInput): Observable<InterventionCase> {
    const url = this.buildUrl('/psychologist/interventions');
    return this.http.post<InterventionCase>(url, payload).pipe(
      map((res: any) => res as InterventionCase),
      catchError((err: HttpErrorResponse) => {
        console.error('[InterventionsService] Create HTTP Error:', err.status, err.message);
        return throwError(() => new Error(err.message || 'Erro ao registar intervenção'));
      })
    );
  }

  delete(interventionId: number): Observable<{ success: boolean; id?: number }> {
    const url = this.buildUrl(`/psychologist/interventions/${interventionId}`);
    return this.http.delete<{ success: boolean; id?: number }>(url).pipe(
      catchError((err: HttpErrorResponse) => {
        console.error('[InterventionsService] Delete HTTP Error:', err.status, err.message);
        return throwError(() => new Error(err.message || 'Erro ao apagar intervenção'));
      })
    );
  }

  update(interventionId: number, payload: { description: string }): Observable<InterventionCase> {
    const url = this.buildUrl(`/psychologist/interventions/${interventionId}`);
    return this.http.patch<InterventionCase>(url, payload).pipe(
      map((res: any) => res as InterventionCase),
      catchError((err: HttpErrorResponse) => {
        console.error('[InterventionsService] Update HTTP Error:', err.status, err.message);
        return throwError(() => new Error(err.message || 'Erro ao atualizar intervenção'));
      })
    );
  }
}
