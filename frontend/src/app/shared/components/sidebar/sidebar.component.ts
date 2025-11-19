import { Component, inject, Input, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { MenuService } from '../../../core/services/menu.service';
import { MenuItem } from '../../../core/models/menu.model';

/**
 * Componente Sidebar standalone con permisos dinámicos
 * Single Responsibility: Solo renderiza el sidebar
 * Open/Closed: Extensible via MenuService
 */
@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  template: `
    <div class="sidebar-overlay" [class.show]="isOpen && isMobile()" (click)="closeSidebar()"></div>

    <aside class="sidebar" [class.show]="isOpen" [class.collapsed]="isCollapsed">
      <div class="sidebar-header-mobile">
        <a [routerLink]="['/profile']" class="logo">
          <div class="logo-icon">
            <i class="fas fa-cube"></i>
          </div>
          <span>Roska Radiadores</span>
        </a>
      </div>

      <div class="sidebar-menu">
        <ng-container *ngFor="let item of menuItems()">
          <!-- Item sin hijos (función regular) -->
          <a
            *ngIf="!item.children || item.children.length === 0"
            [routerLink]="item.route"
            routerLinkActive="active"
            class="menu-item"
            [title]="item.label"
            (click)="onMenuItemClick()"
          >
            <i [class]="item.icon"></i>
            <span class="menu-text">{{ item.label }}</span>
          </a>

          <!-- Categoría con funciones (colapsable) -->
          <div *ngIf="item.children && item.children.length > 0">
            <a
              href="javascript:void(0)"
              [class]="item.is_category ? 'category-item' : 'menu-item'"
              [class.expanded]="isExpanded(item.id)"
              [title]="item.label"
              (click)="toggleSubmenu(item.id)"
            >
              <div class="category-icon" *ngIf="item.is_category" [style.background-color]="item.color + '20'">
                <i [class]="item.icon" [style.color]="item.color"></i>
              </div>
              <i *ngIf="!item.is_category" [class]="item.icon"></i>
              <span class="menu-text">{{ item.label }}</span>
              <i class="fas fa-chevron-right arrow"></i>
            </a>

            <div class="submenu" [class.show]="isExpanded(item.id)">
              <a
                *ngFor="let child of item.children"
                [routerLink]="child.route"
                routerLinkActive="active"
                class="submenu-item"
                (click)="onMenuItemClick()"
              >
                <i [class]="child.icon"></i>
                <span>{{ child.label }}</span>
              </a>
            </div>
          </div>
        </ng-container>
      </div>
    </aside>
  `,
  styles: [`
    .sidebar-overlay {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: rgba(0, 0, 0, 0.6);
      z-index: 1015;
      opacity: 0;
      transition: opacity 0.3s ease;
    }

    .sidebar-overlay.show {
      display: block;
      opacity: 1;
    }

    .sidebar {
      position: fixed;
      left: 0;
      top: 70px;
      bottom: 0;
      width: 260px;
      background-color: #ffffff;
      border-right: 1px solid #e5e7eb;
      overflow-y: auto;
      overflow-x: hidden;
      transition: transform 0.3s ease;
      z-index: 1020;
      padding-top: 1rem;
    }

    .sidebar::-webkit-scrollbar {
      width: 6px;
    }

    .sidebar::-webkit-scrollbar-track {
      background: transparent;
    }

    .sidebar::-webkit-scrollbar-thumb {
      background: #d1d5db;
      border-radius: 3px;
    }

    .sidebar::-webkit-scrollbar-thumb:hover {
      background: #9ca3af;
    }

    /* Desktop: collapsed = mostrar solo iconos */
    @media (min-width: 769px) {
      .sidebar.collapsed {
        width: 70px;
      }

      .sidebar.collapsed .menu-text {
        display: none;
      }

      .sidebar.collapsed .arrow {
        display: none;
      }

      .sidebar.collapsed .menu-item {
        justify-content: center;
        padding: 0.75rem;
      }

      .sidebar.collapsed .menu-item i:first-child {
        margin-right: 0;
      }

      .sidebar.collapsed .submenu {
        display: none;
      }
    }

    /* Mobile: collapsed = ocultar completamente */
    @media (max-width: 768px) {
      .sidebar.collapsed {
        transform: translateX(-100%);
      }
    }

    .sidebar-header-mobile {
      display: none;
      padding: 1.25rem 1.5rem;
      border-bottom: 1px solid #e5e7eb;
      margin-bottom: 0.5rem;
      background-color: white;
    }

    .sidebar-header-mobile .logo {
      font-size: 1.5rem;
      display: flex;
      align-items: center;
      text-decoration: none;
      color: #1f2937;
      gap: 0.5rem;
    }

    .logo-icon {
      width: 40px;
      height: 40px;
      background: linear-gradient(135deg, #8b5cf6, #a78bfa);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
    }

    .sidebar-menu {
      padding: 0;
    }

    .menu-item {
      display: flex;
      align-items: center;
      padding: 0.75rem 1.5rem;
      color: #6b7280;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 0.875rem;
      border-left: 3px solid transparent;
    }

    .menu-item:hover {
      background-color: #f3f4f6;
      color: #8b5cf6;
    }

    .menu-item.active {
      background-color: #f3f4f6;
      color: #8b5cf6;
      border-left-color: #8b5cf6;
    }

    .category-item {
      display: flex;
      align-items: center;
      padding: 0.875rem 1.5rem;
      color: #374151;
      text-decoration: none;
      cursor: pointer;
      transition: all 0.2s;
      font-size: 0.875rem;
      font-weight: 600;
      border-left: 3px solid transparent;
      background-color: #f9fafb;
      margin-bottom: 0.25rem;
    }

    .category-item:hover {
      background-color: #f3f4f6;
    }

    .category-item.expanded {
      background-color: #f3f4f6;
    }

    .category-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      margin-right: 0.75rem;
      font-size: 1rem;
    }

    .menu-item i:first-child {
      width: 20px;
      margin-right: 0.75rem;
      font-size: 1rem;
    }

    .menu-item .arrow {
      margin-left: auto;
      transition: transform 0.3s;
      font-size: 0.75rem;
    }

    .menu-item.expanded .arrow {
      transform: rotate(90deg);
    }

    .submenu {
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.3s ease;
    }

    .submenu.show {
      max-height: 500px;
    }

    .submenu-item {
      display: flex;
      align-items: center;
      padding: 0.625rem 1.5rem 0.625rem 3.5rem;
      color: #6b7280;
      text-decoration: none;
      font-size: 0.875rem;
      transition: all 0.2s;
      position: relative;
    }

    .submenu-item::before {
      content: '';
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background-color: #6b7280;
      margin-right: 0.75rem;
      position: absolute;
      left: 2.5rem;
    }

    .submenu-item:hover {
      background-color: #f3f4f6;
      color: #8b5cf6;
    }

    .submenu-item.active {
      color: #8b5cf6;
      font-weight: 500;
    }

    .submenu-item.active::before {
      background-color: #8b5cf6;
    }

    @media (max-width: 768px) {
      .sidebar {
        width: 280px;
        max-width: 80%;
        transform: translateX(-100%);
        top: 0;
        padding-top: 0;
        box-shadow: 4px 0 15px rgba(0, 0, 0, 0.15);
        z-index: 1025;
      }

      .sidebar-header-mobile {
        display: block;
      }

      .sidebar.show {
        transform: translateX(0);
      }

      .menu-item {
        padding: 0.875rem 1.5rem;
        font-size: 0.9rem;
      }

      .submenu-item {
        padding: 0.75rem 1.5rem 0.75rem 3.5rem;
        font-size: 0.875rem;
      }
    }

    @media (max-width: 480px) {
      .sidebar {
        width: 85%;
        max-width: none;
      }
    }
  `]
})
export class SidebarComponent implements OnInit {
  private readonly menuService = inject(MenuService);

  @Input() isOpen = true; // Desktop: sidebar abierto por defecto
  @Input() isCollapsed = false; // Desktop: sidebar colapsado (solo iconos)

  // Signal para items expandidos
  private expandedItems = signal<Set<string>>(new Set());

  // Computed del servicio
  menuItems = this.menuService.menuItems;

  ngOnInit(): void {
    // Cargar permisos y menú dinámico del usuario al iniciar
    this.menuService.loadUserPermissions().subscribe();
    this.menuService.loadUserMenu().subscribe();
  }

  toggleSubmenu(itemId: string): void {
    const expanded = new Set(this.expandedItems());

    if (expanded.has(itemId)) {
      expanded.delete(itemId);
    } else {
      expanded.add(itemId);
    }

    this.expandedItems.set(expanded);
  }

  isExpanded(itemId: string): boolean {
    return this.expandedItems().has(itemId);
  }

  onMenuItemClick(): void {
    // En móvil, cerrar sidebar al hacer click
    if (window.innerWidth <= 768) {
      this.closeSidebar();
    }
  }

  closeSidebar(): void {
    this.isOpen = false;
  }

  isMobile(): boolean {
    return window.innerWidth <= 768;
  }
}
