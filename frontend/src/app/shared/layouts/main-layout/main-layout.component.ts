import { Component, signal, effect } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { TopbarComponent } from '../../components/topbar/topbar.component';
import { SidebarComponent } from '../../components/sidebar/sidebar.component';

/**
 * Layout Principal con TopBar y Sidebar
 * Single Responsibility: Solo estructura el layout
 */
@Component({
  selector: 'app-main-layout',
  standalone: true,
  imports: [CommonModule, RouterOutlet, TopbarComponent, SidebarComponent],
  template: `
    <app-topbar
      [sidebarCollapsed]="sidebarCollapsed()"
      (toggleSidebar)="onToggleSidebar()">
    </app-topbar>

    <app-sidebar
      [isOpen]="sidebarOpen()"
      [isCollapsed]="sidebarCollapsed()">
    </app-sidebar>

    <main class="main-content"
      [class.collapsed]="sidebarCollapsed() && !isMobile()"
      [class.expanded]="!sidebarOpen() && isMobile()">
      <router-outlet></router-outlet>
    </main>
  `,
  styles: [`
    :host {
      display: block;
      min-height: 100vh;
    }

    .main-content {
      margin-left: 260px;
      margin-top: 70px;
      padding: 2rem;
      transition: margin-left 0.3s ease;
      min-height: calc(100vh - 70px);
      background-color: #f9fafb;
    }

    .main-content.collapsed {
      margin-left: 70px;
    }

    .main-content.expanded {
      margin-left: 0;
    }

    @media (max-width: 768px) {
      .main-content {
        margin-left: 0;
        padding: 1rem;
      }
    }

    @media (max-width: 480px) {
      .main-content {
        padding: 0.75rem;
      }
    }
  `]
})
export class MainLayoutComponent {
  // Estado para mobile: abierto/cerrado
  sidebarOpen = signal(this.isMobile() ? false : true);

  // Estado para desktop: expandido/colapsado (solo iconos)
  sidebarCollapsed = signal(this.loadSidebarState());

  constructor() {
    // Persistir estado collapsed en localStorage
    effect(() => {
      localStorage.setItem('sidebarCollapsed', JSON.stringify(this.sidebarCollapsed()));
    });
  }

  onToggleSidebar(): void {
    if (this.isMobile()) {
      // En mobile: abrir/cerrar sidebar
      this.sidebarOpen.update(open => !open);
    } else {
      // En desktop: expandir/colapsar (mostrar/ocultar textos)
      this.sidebarCollapsed.update(collapsed => !collapsed);
    }
  }

  isMobile(): boolean {
    return window.innerWidth <= 768;
  }

  private loadSidebarState(): boolean {
    const saved = localStorage.getItem('sidebarCollapsed');
    return saved ? JSON.parse(saved) : false;
  }
}
