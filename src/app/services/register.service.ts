import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class RegisterService {
  private registerStatusSubject = new BehaviorSubject<boolean>(false);
  registerStatus$ = this.registerStatusSubject.asObservable();

  constructor(private http: HttpClient) {}

  private buildUrl(path: string): string {
    if (environment.apiUrl) {
      return `${environment.apiUrl}${path}`;
    }
    return path;
  }

  // Method to register a new user
  register(userData: { email: string; password: string }): Observable<any> {
    const url = this.buildUrl('/register/');
    console.log('Registering user with data:', userData);
    return this.http.post<any>(url, userData).pipe(
      catchError((error) => {
        console.error('Registration error:', error);
        return throwError(
          () => new Error(error.error?.detail || 'Registration failed. Please try again.')
        );
      })
    );
  }
}
