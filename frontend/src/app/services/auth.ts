import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000'; 
  private tokenKey = 'auth_token';
  private userKey = 'auth_user';

  constructor(private http: HttpClient) { }

  // Registrar Usuario
  register(username: string, email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/users/`, { 
      username, 
      email, 
      password 
    });
  }

  // Login Usuario
  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/users/login`, { 
      email, 
      password 
    });
  }

  // Manejo de Token
  saveToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  // Obtener Token
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  // Verificar si el usuario está autenticado
  inAuthenticated(): boolean {
    return !!this.getToken();
  }

  // Guardar información del usuario
  saveUser(user: { id: number; username: string; email: string }): void {
    localStorage.setItem(this.userKey, JSON.stringify(user));
  }

  // Obtener información del usuario
  getUser(): { id: number; username: string; email: string } | null {
    const serialized = localStorage.getItem(this.userKey);
    return serialized ? JSON.parse(serialized) : null;
  }

  getUserId(): number | null {
    return this.getUser()?.id ?? null;
  }

  // Limpiar datos del usuario
  clearUser(): void {
    localStorage.removeItem(this.userKey);
  }

  // Logout Usuario
  logout(): void {
    localStorage.removeItem(this.tokenKey);
    this.clearUser();
  }
}
