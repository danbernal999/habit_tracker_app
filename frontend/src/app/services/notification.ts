import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface NotificationItem {
  id: number;
  user_id: number;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  getNotifications(userId: number, includeRead: boolean = true): Observable<NotificationItem[]> {
    return this.http.get<NotificationItem[]>(`${this.apiUrl}/notifications/`, {
      params: {
        user_id: userId,
        include_read: includeRead
      }
    });
  }

  getUnreadCount(userId: number): Observable<{ unread_count: number }> {
    return this.http.get<{ unread_count: number }>(`${this.apiUrl}/notifications/unread/count`, {
      params: { user_id: userId }
    });
  }

  markAsRead(notificationId: number): Observable<NotificationItem> {
    return this.http.put<NotificationItem>(`${this.apiUrl}/notifications/${notificationId}/read`, {});
  }

  markAllAsRead(userId: number): Observable<{ updated: number }> {
    return this.http.put<{ updated: number }>(`${this.apiUrl}/notifications/mark-all/read`, {}, {
      params: { user_id: userId }
    });
  }

  createNotification(payload: { user_id: number; title: string; message: string }): Observable<NotificationItem> {
    return this.http.post<NotificationItem>(`${this.apiUrl}/notifications/`, payload);
  }
}
