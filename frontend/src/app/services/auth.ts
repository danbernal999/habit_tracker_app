import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000'; 

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
    localStorage.setItem('auth_token', token);
  }

  // Obtener Token
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  // Verificar si el usuario está autenticado
  inAuthenticated(): boolean {
    return !!this.getToken();
  }

  // Logout Usuario
  logout(): void {
    localStorage.removeItem('auth_token');
  }
}


export class Auth {
  
}
