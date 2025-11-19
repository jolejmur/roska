import { Routes } from '@angular/router';
import { authGuard, publicGuard } from './core/guards/auth.guard';
import { MainLayoutComponent } from './shared/layouts/main-layout/main-layout.component';

/**
 * Configuración de rutas standalone
 * Lazy loading para optimizar carga inicial
 */
export const routes: Routes = [
  {
    path: 'login',
    canActivate: [publicGuard],
    loadComponent: () =>
      import('./features/auth/login/login.component').then(m => m.LoginComponent)
  },
  {
    path: '',
    component: MainLayoutComponent,
    canActivate: [authGuard],
    children: [
      {
        path: '',
        redirectTo: 'profile',
        pathMatch: 'full'
      },
      {
        path: 'profile',
        loadComponent: () =>
          import('./features/profile/profile.component').then(m => m.ProfileComponent)
      },
      {
        path: 'users',
        loadChildren: () =>
          import('./features/users/users.routes').then(m => m.USERS_ROUTES)
      },
      {
        path: 'customers',
        loadChildren: () =>
          import('./features/customers/customers.routes').then(m => m.CUSTOMERS_ROUTES)
      },
      {
        path: 'functions',
        loadChildren: () =>
          import('./features/functions/functions.routes').then(m => m.FUNCTIONS_ROUTES)
      },
      {
        path: 'roles',
        loadChildren: () =>
          import('./features/roles/roles.routes').then(m => m.ROLES_ROUTES)
      },
      {
        path: 'categories',
        loadChildren: () =>
          import('./features/categories/categories.routes').then(m => m.categoriesRoutes)
      },
      {
        path: 'commercial',
        loadChildren: () => import('./features/commercial/commercial.routes').then(m => m.COMMERCIAL_ROUTES)
      }
      // Las demas rutas se crean dinamicamente desde el backend via el menu
    ]
  },
  {
    path: '**',
    redirectTo: ''
  }
];
