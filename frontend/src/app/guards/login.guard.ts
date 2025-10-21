import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';
import { AuthService } from '../services/auth';

@Injectable({
  providedIn: 'root'
})
export class LoginGuard implements CanActivate {
  
  constructor(private authService: AuthService, private router: Router) {}
  
  canActivate(): boolean | UrlTree {
    if (this.authService.inAuthenticated()) {
      // Si ya está autenticado, redirigir al dashboard
      return this.router.createUrlTree(['/dashboard']);
    }
    
    // Permitir acceso al login si no está autenticado
    return true;
  }
}
