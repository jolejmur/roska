import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="dashboard">
      <h1>Dashboard</h1>
      <p>Welcome to Roska Radiadores!</p>
    </div>
  `,
  styles: [`
    .dashboard {
      padding: var(--spacing-xl);
    }
  `]
})
export class DashboardComponent {
}
