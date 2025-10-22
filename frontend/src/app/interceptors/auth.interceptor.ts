import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth';

export const AuthInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  
  // Solo añadir el token si el usuario está autenticado
  if (authService.inAuthenticated()) {
    const token = authService.getToken();
    if (token) {
      const authReq = req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`)
      });
      return next(authReq);
    }
  }
  
  // Si no hay token o el usuario no está autenticado, continuar sin modificar
  return next(req);
};

