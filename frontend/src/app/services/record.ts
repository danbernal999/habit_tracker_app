import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class RecordService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  // Obtener registros de un hábito
  getRecords(habitId: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/habits/${habitId}/records`);
  }

  // Crear registro
  createRecord(habitId: number, record: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/habits/${habitId}/records`, record);
  }

  // Eliminar registro
  deleteRecord(habitId: number, recordId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/habits/${habitId}/records/${recordId}`);
  }
}
