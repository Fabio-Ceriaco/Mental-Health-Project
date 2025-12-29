import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject, catchError } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthResponse } from '../interfaces/api-responses';

@Injectable({
  providedIn: 'root',
})
export class LoginService {
  private buildUrl(path: string): string {
    if (environment.apiUrl) {
      return `${environment.apiUrl}${path}`;
    }
    return path;
  }

  // In-memory storage for token, user, and employee
  private inMemoryToken: string | null = null;

  // User and Employee can be of any type; adjust as needed
  private employeeSubject = new BehaviorSubject<any | null>(null);
  private userSubject = new BehaviorSubject<any | null>(null);

  // Observables to subscribe to changes
  employee$ = this.employeeSubject.asObservable();
  user$ = this.userSubject.asObservable();

  constructor(private http: HttpClient) {}

  //----------Login User----------//

  login(email: string, password: string): Observable<AuthResponse> {
    const url = this.buildUrl('/auth/login');
    const body = new URLSearchParams(); // Using URLSearchParams for x-www-form-urlencoded
    body.set('username', email); // Note: 'username' is used as per typical OAuth2 conventions
    body.set('password', password); // Set password

    return this.http
      .post<AuthResponse>(url, body.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      .pipe(
        catchError((error: HttpErrorResponse) => {
          console.error('Login error:', error);
          return throwError(
            () => new Error(error.error?.detail || 'Login failed. Please check your credentials.')
          );
        })
      ); // Return the observable directly
  }

  // ----------Token Management----------//

  // Save token to localStorage and in-memory
  salvarToken(token: string) {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('access_token', token); // Save token to localStorage
    }
    return (this.inMemoryToken = token); // Also save to in-memory variable
  }

  // Retrieve token from localStorage or in-memory
  obterToken(): string | null {
    if (typeof window !== 'undefined' && window.localStorage) {
      const token = localStorage.getItem('access_token'); // Get token from localStorage
      return token ?? this.inMemoryToken; // Fallback to in-memory if not found
    }
    return this.inMemoryToken; // Fallback to in-memory if localStorage is not available
  }
  // Remove token from localStorage and in-memory
  removeToken(): void {
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.removeItem('access_token'); // Remove token from localStorage
    }
    this.inMemoryToken = null; // Clear in-memory token
  }

  //----------User Logged In----------//

  // Save user to localStorage and update BehaviorSubject
  salvarUser(user: any) {
    if (!user) return null; // Guard clause for null/undefined user
    if (typeof window !== 'undefined' && window.localStorage) {
      // Check for localStorage availability
      localStorage.setItem('user', JSON.stringify(user)); // Save user to localStorage
    }
    this.userSubject.next(user); // Update BehaviorSubject
    return user; // Return the user
  }

  // Retrieve user from localStorage or in-memory
  obterUser(): any | null {
    const userData =
      (typeof window !== 'undefined' && window.localStorage
        ? localStorage.getItem('user')
        : null) ?? null; // Get user data from localStorage if available
    if (userData && userData !== 'undefined') {
      // Guard against 'undefined' string
      try {
        const user = JSON.parse(userData);
        this.userSubject.next(user); // Update BehaviorSubject
        return user; // Return parsed user
      } catch (err) {
        console.error('Erro ao fazer parse do user:', err); // Log parsing error
        return null;
      }
    }
    return this.userSubject.value; // Return current value from BehaviorSubject
  }

  // ---------Employee Logged In----------//

  // Save employee to localStorage and update BehaviorSubject
  salvarEmployee(employee: any) {
    if (!employee) return null; // Guard clause for null/undefined employee
    if (typeof window !== 'undefined' && window.localStorage) {
      localStorage.setItem('employee', JSON.stringify(employee)); // Save employee to localStorage
    }
    this.employeeSubject.next(employee); // Update BehaviorSubject
    return employee; // Return the employee
  }

  // Retrieve employee from localStorage or in-memory
  obterEmployee() {
    const employeeData =
      (typeof window !== 'undefined' && window.localStorage
        ? localStorage.getItem('employee')
        : null) ?? null; // Get employee data from localStorage if available
    if (employeeData && employeeData !== 'undefined') {
      {
        try {
          return JSON.parse(employeeData); // Return parsed employee
        } catch (err) {
          console.error('Erro ao fazer parse do employee:', err); // Log parsing error
          return null;
        }
      }
    }
    return this.employeeSubject.value; // Return current value from BehaviorSubject
  }

  // Convenience method to get employee ID
  employee_Id(): number | null {
    if (typeof window === 'undefined') return null; // Ensure window is defined
    const storedEmployee = localStorage.getItem('employee'); // Get employee from localStorage
    if (!storedEmployee) return null; // Return null if not found
    try {
      const employee = JSON.parse(storedEmployee); // Parse the stored JSON
      return employee.id ?? null; // Return the ID or null if not present
    } catch (err) {
      console.error('Erro ao fazer parse do employee para obter ID:', err); // Log parsing error
      return null;
    }
  }
  // ----------Logout User----------//

  // Logout user by clearing token, user, and employee data
  logout() {
    this.removeToken(); // Remove token
    localStorage.removeItem('user'); // Remove user data
    localStorage.removeItem('employee'); // Remove employee data
    this.userSubject.next(null); // Clear user BehaviorSubject
    this.employeeSubject.next(null); // Clear employee BehaviorSubject
  }

  // ----------Error Handling----------//
  // Handle HTTP errors
  private handleError(error: HttpErrorResponse): Observable<any> {
    let msg = 'Ocorreu um erro inesperado.';
    if (error.error instanceof ErrorEvent) {
      msg = `Erro de cliente: ${error.error.message}`;
    } else if (error.error?.detail) {
      msg = error.error.detail;
    }
    return throwError(() => new Error(msg));
  }
}
