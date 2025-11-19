import { Injectable, inject, signal, computed } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, of } from 'rxjs';
import { MenuItem, UserPermissions } from '../models/menu.model';
import { AuthService } from './auth.service';

/**
 * Servicio de Menú Dinámico basado en Roles y Funciones
 * Single Responsibility: Solo maneja la lógica del menú y permisos
 * Ahora el menú viene dinámicamente desde el backend
 */
@Injectable({
  providedIn: 'root'
})
export class MenuService {
  private readonly http = inject(HttpClient);
  private readonly authService = inject(AuthService);
  private readonly API_URL = 'http://localhost:8000/api';

  // Signal para el menú dinámico desde el backend
  private readonly menuItemsSignal = signal<MenuItem[]>([]);

  // Signals para permisos
  private readonly userPermissionsSignal = signal<UserPermissions | null>(null);

  // Computed signal para el menú (directamente desde el signal)
  readonly menuItems = computed(() => this.menuItemsSignal());

  /**
   * Cargar menú dinámico del usuario desde el backend
   * El menú se construye en base a los roles y funciones asignadas al usuario
   */
  loadUserMenu(): Observable<MenuItem[]> {
    return this.http.get<any[]>(`${this.API_URL}/users/me/menu`).pipe(
      tap(menu => {
        // Transformar la respuesta del backend al formato MenuItem
        const transformedMenu = this.transformBackendMenu(menu);
        this.menuItemsSignal.set(transformedMenu);
      })
    );
  }

  /**
   * Transformar el menú del backend al formato MenuItem de Angular
   */
  private transformBackendMenu(backendMenu: any[]): MenuItem[] {
    return backendMenu.map(item => this.transformMenuItem(item));
  }

  /**
   * Transformar un item individual del menú
   */
  private transformMenuItem(item: any): MenuItem {
    const menuItem: MenuItem = {
      id: item.code || item.id.toString(),
      label: item.name,
      icon: item.icon,
      route: item.url || undefined,
      is_category: item.is_category || false,
      color: item.color || undefined,
      children: item.children && item.children.length > 0
        ? item.children.map((child: any) => this.transformMenuItem(child))
        : undefined
    };
    return menuItem;
  }

  /**
   * Cargar permisos del usuario desde el backend
   */
  loadUserPermissions(): Observable<UserPermissions> {
    const user = this.authService.currentUser();

    // Si es superuser, dar todos los permisos
    if (user?.is_superuser) {
      const superuserPermissions: UserPermissions = {
        user_id: user.id,
        email: user.email,
        is_superuser: true,
        permissions: {
          users: {
            create: true,
            read: true,
            update: true,
            delete: true,
            list: true
          }
        }
      };
      this.userPermissionsSignal.set(superuserPermissions);
      return of(superuserPermissions);
    }

    // Para usuarios regulares, consultar Cerbos
    return this.http.get<UserPermissions>(`${this.API_URL}/users/me/permissions`).pipe(
      tap(permissions => {
        this.userPermissionsSignal.set(permissions);
      })
    );
  }

  /**
   * Verificar si el usuario tiene un permiso específico
   */
  hasPermission(permission: string): boolean {
    const userPerms = this.userPermissionsSignal();

    if (!userPerms) {
      return false;
    }

    // Superuser tiene todos los permisos
    if (userPerms.is_superuser) {
      return true;
    }

    // Parsear el permiso (ej: "users.list")
    const [resource, action] = permission.split('.');

    if (resource === 'users' && userPerms.permissions.users) {
      return userPerms.permissions.users[action as keyof typeof userPerms.permissions.users] || false;
    }

    return false;
  }

  /**
   * Obtener permisos actuales
   */
  getUserPermissions(): UserPermissions | null {
    return this.userPermissionsSignal();
  }
}
