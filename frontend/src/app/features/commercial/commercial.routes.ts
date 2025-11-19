import { Routes } from '@angular/router';

export const COMMERCIAL_ROUTES: Routes = [
  {
    path: 'quotation',
    loadComponent: () => import('./pages/quotation-form/quotation-form.component')
      .then(m => m.QuotationFormComponent)
  }
];