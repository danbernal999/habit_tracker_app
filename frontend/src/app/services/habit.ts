import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class HabitService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  // Obtener todos los hábitos
  getHabits(): Observable<any> {
    return this.http.get(`${this.apiUrl}/habits/`);
  }

  // Obtener un hábito específico
  getHabit(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/habits/${id}`);
  }

  // Crear hábito
  createHabit(habit: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/habits/`, habit);
  }

  // Actualizar hábito
  updateHabit(id: number, habit: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/habits/${id}`, habit);
  }

  // Eliminar hábito
  deleteHabit(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/habits/${id}`);
  }
}
