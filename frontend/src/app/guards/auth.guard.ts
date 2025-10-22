import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree } from '@angular/router';
import { AuthService } from '../services/auth';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  
  constructor(private authService: AuthService, private router: Router) {}
  
  canActivate(): boolean | UrlTree {
    if (this.authService.inAuthenticated()) {
      return true;
    }
    
    // Redirigir al login si no está autenticado
    return this.router.createUrlTree(['/login']);
  }
}
