import { Component, ElementRef, HostListener, OnDestroy, OnInit } from '@angular/core';
import { RouterLink, RouterLinkActive, Router } from '@angular/router';
import { AuthService } from 'src/app/services/auth';
import { CommonModule } from '@angular/common';
import { NotificationService, NotificationItem } from 'src/app/services/notification';
import { Subject } from 'rxjs';
import { takeUntil, finalize } from 'rxjs/operators';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.css']
})
export class NavbarComponent implements OnInit, OnDestroy {
  notifications: NotificationItem[] = [];
  unreadCount = 0;
  showNotifications = false;
  loadingNotifications = false;

  private destroy$ = new Subject<void>();

  constructor(
    public authService: AuthService,
    private router: Router,
    private notificationService: NotificationService,
    private elementRef: ElementRef
  ) {}

  ngOnInit(): void {
    this.loadNotifications();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private loadNotifications(): void {
    const userId = this.authService.getUserId();
    if (!userId) {
      this.notifications = [];
      this.unreadCount = 0;
      return;
    }

    this.loadingNotifications = true;
    this.notificationService
      .getNotifications(userId)
      .pipe(
        takeUntil(this.destroy$),
        finalize(() => {
          this.loadingNotifications = false;
          this.updateUnreadCount();
        })
      )
      .subscribe({
        next: (notifications) => {
          this.notifications = notifications;
        },
        error: (error) => {
          console.error('Error al cargar notificaciones:', error);
        }
      });
  }

  private updateUnreadCount(): void {
    this.unreadCount = this.notifications.filter((notification) => !notification.is_read).length;
  }

  toggleNotifications(): void {
    if (!this.authService.inAuthenticated()) {
      this.router.navigate(['/login']);
      return;
    }

    this.showNotifications = !this.showNotifications;
    if (this.showNotifications) {
      this.loadNotifications();
    }
  }

  markAsRead(notification: NotificationItem): void {
    if (notification.is_read) {
      return;
    }

    this.notificationService
      .markAsRead(notification.id)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (updated) => {
          const index = this.notifications.findIndex((item) => item.id === updated.id);
          if (index !== -1) {
            this.notifications[index] = updated;
            this.updateUnreadCount();
          }
        },
        error: (error) => console.error('No se pudo marcar como leída:', error)
      });
  }

  markAllAsRead(): void {
    const userId = this.authService.getUserId();
    if (!userId) {
      return;
    }

    this.notificationService
      .markAllAsRead(userId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.notifications = this.notifications.map((notification) => ({
            ...notification,
            is_read: true
          }));
          this.updateUnreadCount();
        },
        error: (error) => console.error('No se pudo marcar todas como leídas:', error)
      });
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
    this.showNotifications = false;
    this.notifications = [];
    this.unreadCount = 0;
  }

  get userInitial(): string {
    const user = this.authService.getUser();
    return user?.username?.charAt(0).toUpperCase() ?? 'U';
  }

  @HostListener('document:click', ['$event'])
  handleClickOutside(event: Event): void {
    if (this.showNotifications && !this.elementRef.nativeElement.contains(event.target)) {
      this.showNotifications = false;
    }
  }
}
