import { HttpInterceptorFn, HttpRequest, HttpHandlerFn } from '@angular/common/http';
import { LoginService } from '../../services/login.service';
import { inject } from '@angular/core';

export const authInterceptor: HttpInterceptorFn = (req: HttpRequest<any>, next: HttpHandlerFn) => {
  const loginService = inject(LoginService);
  const token = loginService.obterToken() ?? '';
  const employee = loginService.obterEmployee();

  const authReq = token
    ? req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`),
      })
    : req;

  return next(authReq);
};
