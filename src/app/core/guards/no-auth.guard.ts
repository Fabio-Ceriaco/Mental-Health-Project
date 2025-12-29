import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { LoginService } from '../../services/login.service';

@Injectable({
  providedIn: 'root',
})
export class NoAuthGuard implements CanActivate {
  constructor(private loginService: LoginService, private router: Router) {}

  // If the user is authenticated, redirect to appropriate dashboard based on role
  canActivate(): boolean {
    const token = this.loginService.obterToken();
    if (token) {
      const employee = this.loginService.obterEmployee();
      const role = employee?.role_name || employee?.role?.name || '';

      // Redirect based on role
      if (role === 'RH') {
        this.router.navigate(['/rh-dashboard']);
      } else if (role === 'Psychologist') {
        this.router.navigate(['/patient']);
      } else {
        this.router.navigate(['/employee-dashboard']);
      }
      return false;
    }
    return true;
  }
}
