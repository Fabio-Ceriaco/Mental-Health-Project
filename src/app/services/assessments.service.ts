import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, map, throwError } from 'rxjs';
import { environment } from '../../environments/environment';

export interface AssessmentItem {
  id: number;
  employee_id: number;
  employee_name: string;
  score_total: number;
  score_percent: number;
  risk_level: string;
  risk_level_id: number;
  created_at: string;
  per_dimension: { [key: string]: { score: number; max: number; percent: number } };
  score_max: number;
}

export interface AssessmentsListResponse {
  items: AssessmentItem[];
  total: number;
}

@Injectable({ providedIn: 'root' })
export class AssessmentsService {
  constructor(private http: HttpClient) {}

  private buildUrl(path: string): string {
    return environment.apiUrl ? `${environment.apiUrl}${path}` : path;
  }

  getAll(): Observable<AssessmentsListResponse> {
    const url = this.buildUrl('/rh/assessments');
    console.log('[AssessmentsService] Fetching from URL:', url);
    return this.http.get<AssessmentsListResponse>(url).pipe(
      map((res: any) => {
        console.log('[AssessmentsService] Response received:', res);
        const result = {
          items: Array.isArray(res?.items) ? res.items : [],
          total: Number(res?.total ?? (Array.isArray(res?.items) ? res.items.length : 0)),
        };
        console.log('[AssessmentsService] Mapped result items:', result.items.length);
        return result;
      }),
      catchError((err: HttpErrorResponse) => {
        console.error('[AssessmentsService] HTTP Error:', err.status, err.message);
        return throwError(() => new Error(err.message || 'Erro a carregar avaliações'));
      })
    );
  }
}
