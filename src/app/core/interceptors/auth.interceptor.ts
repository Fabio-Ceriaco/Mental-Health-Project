import { HttpInterceptorFn, HttpRequest, HttpHandlerFn } from '@angular/common/http';
import { LoginService } from '../../services/login.service';
import { inject } from '@angular/core';

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<any>, next: HttpHandlerFn) => {
  const loginService = inject(LoginService);
  const token = loginService.obterToken() ?? '';
  const employee = loginService.obterEmployee();

  console.log(`[AuthInterceptor] Intercepting request to: ${req.url}`, {
    hasToken: !!token,
    tokenPreview: token ? token.substring(0, 20) + '...' : 'NO TOKEN',
    employee: employee ? `${employee.id} - ${employee.email}` : 'NO EMPLOYEE',
    method: req.method,
  });

  const authReq = token
    ? req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`),
      })
    : req;

  if (!token) {
    console.warn(
      '[AuthInterceptor] ⚠️  NO TOKEN FOUND - Request will be sent without authentication!'
    );
  } else {
    console.log('[AuthInterceptor] ✓ Authorization header added');
  }

  return next(authReq);
};
