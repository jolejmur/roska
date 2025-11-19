import { Routes } from '@angular/router';
import { authGuard } from '../../core/guards/auth.guard';

export const categoriesRoutes: Routes = [
  {
    path: '',
    canActivate: [authGuard],
    children: [
      {
        path: '',
        loadComponent: () =>
          import('./pages/category-list/category-list.component').then(
            (m) => m.CategoryListComponent
          ),
      },
    ],
  },
];
