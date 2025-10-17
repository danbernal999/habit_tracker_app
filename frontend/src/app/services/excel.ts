import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ExcelService {
  private apiUrl = 'http://localhost:8000';
  private progressSubject = new Subject<number>();
  public progress$ = this.progressSubject.asObservable();
  private websocket: WebSocket | null = null;

  constructor(private http: HttpClient) { }

  /**
   * Subir archivo Excel
   */
  uploadExcel(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/excel/upload_excel`, formData);
  }

  /**
   * Conectar al WebSocket para monitorear progreso en tiempo real
   */
  connectProgressWebSocket(): void {
    const wsUrl = `ws://localhost:8000/excel/ws/progress`;
    
    this.websocket = new WebSocket(wsUrl);

    this.websocket.onopen = () => {
      console.log('WebSocket conectado');
    };

    this.websocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.progressSubject.next(data.progress);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.websocket.onclose = () => {
      console.log('WebSocket desconectado');
    };
  }

  /**
   * Desconectar WebSocket
   */
  disconnectProgressWebSocket(): void {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
  }

  /**
   * Obtener datos cargados
   */
  getExcelData(limit: number = 100, offset: number = 0): Observable<any> {
    return this.http.get(`${this.apiUrl}/excel/data`, {
      params: { limit, offset }
    });
  }

  /**
   * Listar archivos subidos
   */
  listUploadedFiles(): Observable<any> {
    return this.http.get(`${this.apiUrl}/excel/list-files`);
  }

  /**
   * Eliminar archivo específico
   */
  deleteFile(filename: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/excel/file/${filename}`);
  }

  /**
   * Eliminar todos los datos
   */
  deleteAllData(): Observable<any> {
    return this.http.delete(`${this.apiUrl}/excel/data`);
  }

  /**
   * Descargar archivo
   */
  downloadFile(filename: string): void {
    const fileUrl = `${this.apiUrl}/uploads/${filename}`;
    window.location.href = fileUrl;
  }
}