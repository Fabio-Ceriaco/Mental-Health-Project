import { Injectable } from '@angular/core';
import { Resolve } from '@angular/router';
import { Observable, of } from 'rxjs';
import { AssessmentService } from '../services/assessment.service';
import { LoginService } from '../services/login.service';
import { catchError, map, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root',
})
export class AssessmentResolver implements Resolve<any[]> {
  constructor(private assessmentService: AssessmentService, private loginService: LoginService) {}

  resolve(): Observable<any[]> {
    const employeeId = this.loginService.employee_Id(); // Get logged in employee ID
    if (!employeeId) {
      console.warn('No logged in employee ID found');
      return of([]);
    }

    return this.assessmentService.getQuestions().pipe(
      tap((questions) => console.log('Assessment questions fetched:', questions)),
      catchError((error) => {
        console.error('Error fetching assessment questions:', error);
        return of([]);
      })
    );
  }
}
