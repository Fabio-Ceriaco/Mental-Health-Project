import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable, tap, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { AssessmentTemplate } from '../interfaces/api-responses';

@Injectable({ providedIn: 'root' })
export class AssessmentService {
  constructor(private http: HttpClient) {}

  private buildUrl(path: string): string {
    if (environment.apiUrl) {
      return `${environment.apiUrl}${path}`;
    }
    return path;
  }

  getQuestions(): Observable<AssessmentTemplate[]> {
    const url = this.buildUrl('/employee/assessments/templates');
    return this.http.get<{ questions: AssessmentTemplate[] }>(url).pipe(
      map((res) => res.questions),
      catchError((error) => {
        console.error('Error fetching assessment questions:', error);
        return throwError(
          () => new Error('Failed to load assessment questions. Please try again.')
        );
      })
    );
  }

  submitAnswers(answers: any): Observable<any> {
    const url = this.buildUrl('/employee/assessments/submit');
    return this.http.post(url, answers).pipe(
      catchError((error) => {
        console.error('Error submitting assessment:', error);
        return throwError(() => new Error('Failed to submit assessment. Please try again.'));
      })
    );
  }
}
