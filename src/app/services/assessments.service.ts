import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, map, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { LoginService } from './login.service';

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
  constructor(private http: HttpClient, private loginService: LoginService) {}

  private buildUrl(path: string): string {
    return environment.apiUrl ? `${environment.apiUrl}${path}` : path;
  }

  private resolvePath(): string {
    const employee = this.loginService.obterEmployee();
    const role = employee?.role_name || employee?.role?.name || '';
    if (role === 'Psychologist') return '/psychologist/assessments';
    return '/rh/assessments';
  }

  getAll(): Observable<AssessmentsListResponse> {
    const path = this.resolvePath();
    const url = this.buildUrl(path);
    return this.http.get<AssessmentsListResponse>(url).pipe(
      map((res: any) => {
        const result = {
          items: Array.isArray(res?.items) ? res.items : [],
          total: Number(res?.total ?? (Array.isArray(res?.items) ? res.items.length : 0)),
        };
        return result;
      }),
      catchError((err: HttpErrorResponse) => {
        console.error('[AssessmentsService] HTTP Error:', err.status, err.message);
        return throwError(() => new Error(err.message || 'Erro a carregar avaliações'));
      })
    );
  }
}
