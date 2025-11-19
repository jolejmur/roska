import { Component, inject, Output, EventEmitter, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../../core/services/auth.service';

/**
 * Componente TopBar standalone
 * Single Responsibility: Solo renderiza la barra superior
 */
@Component({
  selector: 'app-topbar',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <nav class="topbar">
      <button class="sidebar-toggle" (click)="onToggleSidebar()" [class.active]="!sidebarCollapsed">
        <i class="fas fa-bars"></i>
      </button>

      <a routerLink="/profile" class="logo">
        <div class="logo-icon">
          <i class="fas fa-cube"></i>
        </div>
        <span>Roska Radiadores</span>
      </a>

      <div class="search-box">
        <i class="fas fa-search"></i>
        <input type="text" placeholder="Buscar...">
      </div>

      <div class="topbar-actions">
        <div class="topbar-icon" title="Notificaciones">
          <i class="fas fa-bell"></i>
          <span *ngIf="notificationCount() > 0" class="badge-notify">{{ notificationCount() }}</span>
        </div>

        <div class="topbar-icon" title="Pantalla completa">
          <i class="fas fa-expand"></i>
        </div>

        <div class="user-profile" [routerLink]="['/profile']" title="Mi perfil">
          <div class="user-avatar">
            {{ getInitials() }}
          </div>
          <span class="user-name">{{ currentUser()?.full_name || currentUser()?.username }}</span>
        </div>

        <div class="topbar-icon" (click)="onLogout()" title="Cerrar sesión">
          <i class="fas fa-sign-out-alt"></i>
        </div>
      </div>
    </nav>
  `,
  styles: [`
    /* ... */
    .logo-icon {
      width: 40px;
      height: 40px;
      /* Cambiar a Verde */
      background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }
    
    /* ... */

    .sidebar-toggle.active {
      background-color: #f0fdf4;
      color: var(--color-primary);
      border: 2px solid var(--color-primary);
    }
    
    .search-box input:focus {
      outline: none;
      border-color: var(--color-primary);
      box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1);
    }

    /* ... */

    .badge-notify {
      position: absolute;
      top: 8px;
      right: 8px;
      background-color: var(--color-primary); /* Cambiar a variable */
      color: white;
      border-radius: 10px;
      padding: 2px 6px;
      font-size: 10px;
      font-weight: 600;
    }

    .user-profile:hover {
      background-color: #f0fdf4;
    }
    
    .topbar {
      background-color: #ffffff;
      border-bottom: 1px solid #e5e7eb;
      padding: 0.75rem 1.5rem;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 1030;
      display: flex;
      align-items: center;
      gap: 1rem;
      height: 70px;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 1.5rem;
      font-weight: 700;
      color: #1f2937;
      text-decoration: none;
      transition: opacity 0.2s;
    }

    .logo:hover {
      opacity: 0.8;
    }

    .sidebar-toggle {
      border: none;
      background: none;
      font-size: 1.5rem;
      color: #6b7280;
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 8px;
      transition: all 0.2s;
    }

    .sidebar-toggle:hover {
      background-color: #f3f4f6;
    }

    .search-box {
      flex: 0 0 250px;
      position: relative;
    }

    .search-box input {
      width: 100%;
      padding: 0.5rem 1rem 0.5rem 2.5rem;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      font-size: 0.875rem;
    }

    .search-box i {
      position: absolute;
      left: 0.75rem;
      top: 50%;
      transform: translateY(-50%);
      color: #6b7280;
    }

    .topbar-actions {
      margin-left: auto;
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .topbar-icon {
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
      color: #6b7280;
      cursor: pointer;
      transition: background-color 0.2s;
      position: relative;
    }

    .topbar-icon:hover {
      background-color: #f3f4f6;
    }

    .user-profile {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      cursor: pointer;
      padding: 0.25rem 0.5rem;
      border-radius: 8px;
      transition: background-color 0.2s;
    }

    .user-avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: linear-gradient(135deg, #ef4444, #dc2626);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 600;
      font-size: 0.875rem;
    }

    .user-name {
      font-size: 0.875rem;
      font-weight: 500;
      color: #1f2937;
    }

    @media (max-width: 768px) {
      .topbar {
        padding: 0.75rem 1rem;
      }

      .logo span {
        display: none;
      }

      .search-box {
        display: none;
      }

      .user-name {
        display: none;
      }
    }
  `]
})
export class TopbarComponent {
  private readonly authService = inject(AuthService);

  @Input() sidebarCollapsed = false;
  @Output() toggleSidebar = new EventEmitter<void>();

  currentUser = this.authService.currentUser;
  notificationCount = () => 3; // Placeholder

  onToggleSidebar(): void {
    this.toggleSidebar.emit();
  }

  getInitials(): string {
    const user = this.currentUser();
    if (!user) return '?';

    if (user.first_name && user.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }

    return user.username[0].toUpperCase();
  }

  onLogout(): void {
    if (confirm('¿Estás seguro de que deseas cerrar sesión?')) {
      this.authService.logout();
    }
  }
}
