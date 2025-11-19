import { Routes } from '@angular/router';

export const FUNCTIONS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/function-list/function-list.component').then(
        (m) => m.FunctionListComponent
      ),
  },
];
