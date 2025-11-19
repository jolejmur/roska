import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../core/services/auth.service';
import { ButtonComponent } from '../../shared/components/button/button.component';

/**
 * Componente de Profile standalone
 * Single Responsibility: Solo muestra información del usuario
 */
@Component({
  selector: 'app-profile',
  standalone: true,
  imports: [CommonModule, ButtonComponent],
  template: `
    <div class="profile-wrapper">
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar-container">
            <div class="avatar">
              {{ getInitials() }}
            </div>
          </div>

          <h1 class="profile-name">{{ currentUser()?.full_name }}</h1>
          <p class="profile-email">{{ currentUser()?.email }}</p>

          <div class="badges">
            <span *ngIf="currentUser()?.is_superuser" class="badge badge-primary">
              <i class="fas fa-crown"></i> Superadmin
            </span>
            <span *ngIf="currentUser()?.is_staff" class="badge badge-secondary">
              <i class="fas fa-user-tie"></i> Staff
            </span>
            <span *ngIf="currentUser()?.is_active" class="badge badge-success">
              <i class="fas fa-check-circle"></i> Activo
            </span>
          </div>
        </div>

        <div class="profile-body">
          <div class="info-section">
            <h3 class="section-title">Información Personal</h3>

            <div class="info-row">
              <span class="info-label">
                <i class="fas fa-user"></i> Nombre de usuario
              </span>
              <span class="info-value">{{ currentUser()?.username }}</span>
            </div>

            <div class="info-row">
              <span class="info-label">
                <i class="fas fa-envelope"></i> Email
              </span>
              <span class="info-value">{{ currentUser()?.email }}</span>
            </div>

            <div class="info-row">
              <span class="info-label">
                <i class="fas fa-user-circle"></i> Nombre completo
              </span>
              <span class="info-value">{{ currentUser()?.full_name }}</span>
            </div>

            <div class="info-row">
              <span class="info-label">
                <i class="fas fa-id-badge"></i> ID de usuario
              </span>
              <span class="info-value">#{{ currentUser()?.id }}</span>
            </div>
          </div>

          <div class="info-section">
            <h3 class="section-title">Roles y Permisos</h3>

            <div class="permissions-grid">
              <div class="permission-card" [class.active]="currentUser()?.is_superuser">
                <i class="fas fa-user-shield"></i>
                <span>Superusuario</span>
              </div>

              <div class="permission-card" [class.active]="currentUser()?.is_staff">
                <i class="fas fa-users-cog"></i>
                <span>Personal</span>
              </div>

              <div class="permission-card" [class.active]="currentUser()?.is_active">
                <i class="fas fa-check-circle"></i>
                <span>Cuenta Activa</span>
              </div>
            </div>
          </div>

          <div class="actions">
            <app-button
              variant="secondary"
              [fullWidth]="false"
              (clicked)="onEditProfile()"
            >
              <i class="fas fa-edit"></i>
              Editar Perfil
            </app-button>

            <app-button
              variant="secondary"
              [fullWidth]="false"
              (clicked)="onLogout()"
            >
              <i class="fas fa-sign-out-alt"></i>
              Cerrar Sesión
            </app-button>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .profile-wrapper {
      display: flex;
      align-items: flex-start;
      justify-content: center;
      padding: 0;
      min-height: 100%;
    }

    .profile-card {
      background: white;
      border-radius: 20px;
      max-width: 800px;
      width: 100%;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      overflow: hidden;
    }

    .profile-header {
      background: linear-gradient(135deg, #a855f7 0%, #9333ea 100%);
      padding: 3rem 2rem;
      text-align: center;
      color: white;
    }

    .avatar-container {
      display: flex;
      justify-content: center;
      margin-bottom: 1.5rem;
    }

    .avatar {
      width: 120px;
      height: 120px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      border: 4px solid white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 3rem;
      font-weight: 700;
      color: white;
    }

    .profile-name {
      font-size: 2rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
    }

    .profile-email {
      font-size: 1.1rem;
      opacity: 0.9;
      margin-bottom: 1rem;
    }

    .badges {
      display: flex;
      gap: 0.75rem;
      justify-content: center;
      flex-wrap: wrap;
    }

    .badge {
      padding: 0.5rem 1rem;
      border-radius: 20px;
      font-size: 0.875rem;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
    }

    .badge-primary {
      background: rgba(255, 215, 0, 0.2);
      color: #ffd700;
    }

    .badge-secondary {
      background: rgba(255, 255, 255, 0.2);
      color: white;
    }

    .badge-success {
      background: rgba(34, 197, 94, 0.2);
      color: #22c55e;
    }

    .profile-body {
      padding: 2rem;
    }

    .info-section {
      margin-bottom: 2rem;
    }

    .section-title {
      font-size: 1.25rem;
      font-weight: 600;
      color: #1f2937;
      margin-bottom: 1.5rem;
      padding-bottom: 0.75rem;
      border-bottom: 2px solid #e5e7eb;
    }

    .info-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem;
      background: #f9fafb;
      border-radius: 10px;
      margin-bottom: 0.75rem;
    }

    .info-label {
      color: #6b7280;
      font-size: 0.9rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .info-value {
      color: #1f2937;
      font-weight: 600;
    }

    .permissions-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 1rem;
    }

    .permission-card {
      padding: 1.5rem;
      border: 2px solid #e5e7eb;
      border-radius: 10px;
      text-align: center;
      transition: all 0.3s;
      color: #9ca3af;
    }

    .permission-card.active {
      border-color: #a855f7;
      background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(147, 51, 234, 0.1));
      color: #a855f7;
    }

    .permission-card i {
      font-size: 2rem;
      margin-bottom: 0.5rem;
      display: block;
    }

    .actions {
      display: flex;
      gap: 1rem;
      justify-content: center;
      margin-top: 2rem;
      flex-wrap: wrap;
    }

    @media (max-width: 576px) {
      .profile-container {
        padding: 1rem;
      }

      .profile-header {
        padding: 2rem 1rem;
      }

      .profile-name {
        font-size: 1.5rem;
      }

      .info-row {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
      }
    }
  `]
})
export class ProfileComponent implements OnInit {
  private readonly authService = inject(AuthService);

  currentUser = this.authService.currentUser;

  ngOnInit(): void {
    // Refrescar datos del usuario desde el backend
    this.authService.getCurrentUser().subscribe();
  }

  getInitials(): string {
    const user = this.currentUser();
    if (!user) return '?';

    if (user.first_name && user.last_name) {
      return `${user.first_name[0]}${user.last_name[0]}`.toUpperCase();
    }

    return user.username[0].toUpperCase();
  }

  onEditProfile(): void {
    // TODO: Implementar edición de perfil
    alert('Función de edición de perfil próximamente');
  }

  onLogout(): void {
    if (confirm('¿Estás seguro de que deseas cerrar sesión?')) {
      this.authService.logout();
    }
  }
}
