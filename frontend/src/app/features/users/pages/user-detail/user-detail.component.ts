import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-user-detail',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="user-detail">
      <h1>User Detail</h1>
      <p>User details will be displayed here.</p>
    </div>
  `,
  styles: [`
    .user-detail {
      padding: var(--spacing-xl);
    }
  `]
})
export class UserDetailComponent {
}
