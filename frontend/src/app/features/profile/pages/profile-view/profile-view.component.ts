import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-profile-view',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="profile-view">
      <h1>Profile</h1>
      <p>User profile will be displayed here.</p>
    </div>
  `,
  styles: [`
    .profile-view {
      padding: var(--spacing-xl);
    }
  `]
})
export class ProfileViewComponent {
}
