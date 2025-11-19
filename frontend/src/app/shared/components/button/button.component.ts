import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * Componente reutilizable de Button
 * Single Responsibility: Solo renderiza botones
 * Open/Closed: Extensible via @Input properties
 */
@Component({
  selector: 'app-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      [type]="type"
      [class]="getButtonClasses()"
      [disabled]="disabled || loading"
      (click)="handleClick($event)"
    >
      <i *ngIf="loading" class="fas fa-spinner fa-spin me-2"></i>
      <i *ngIf="icon && !loading" [class]="icon + ' me-2'"></i>
      <ng-content></ng-content>
    </button>
  `,
  styles: [`
    .btn-primary {
      width: 100%;
      padding: 0.875rem;
      /* Cambiar gradiente morado a verde */
      background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
      border: none;
      border-radius: 10px;
      color: white;
      font-size: 1rem;
      font-weight: 600;
      transition: all 0.3s;
      cursor: pointer;
    }

    .btn-primary:hover:not(:disabled) {
      /* Cambiar hover a un verde más oscuro */
      background: linear-gradient(135deg, var(--color-primary-dark), #14532d);
      transform: translateY(-2px);
      /* Sombra verde */
      box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
    }

    .btn-primary:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .btn-secondary {
      width: 100%;
      padding: 0.75rem;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      background-color: white;
      color: #1f2937;
      font-size: 0.9rem;
      font-weight: 500;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.75rem;
      cursor: pointer;
      transition: all 0.3s;
    }

    .btn-secondary:hover:not(:disabled) {
      background-color: #f9fafb;
      border-color: #6b7280;
    }

    .btn-secondary:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .btn-full-width {
      width: 100%;
    }

    .btn-auto-width {
      width: auto;
    }
  `]
})
export class ButtonComponent {
  @Input() type: 'button' | 'submit' = 'button';
  @Input() variant: 'primary' | 'secondary' = 'primary';
  @Input() disabled = false;
  @Input() loading = false;
  @Input() icon = '';
  @Input() fullWidth = true;

  @Output() clicked = new EventEmitter<Event>();

  getButtonClasses(): string {
    const classes = [`btn-${this.variant}`];

    if (this.fullWidth) {
      classes.push('btn-full-width');
    } else {
      classes.push('btn-auto-width');
    }

    return classes.join(' ');
  }

  handleClick(event: Event): void {
    if (!this.disabled && !this.loading) {
      this.clicked.emit(event);
    }
  }
}
