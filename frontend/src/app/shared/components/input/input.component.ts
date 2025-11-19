import { Component, Input, forwardRef, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, ReactiveFormsModule } from '@angular/forms';

/**
 * Componente reutilizable de Input
 * Interface Segregation: Implementa solo ControlValueAccessor
 * Open/Closed: Extensible via @Input sin modificar el componente
 */
@Component({
  selector: 'app-input',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => InputComponent),
      multi: true
    }
  ],
  template: `
    <div class="mb-3">
      <label *ngIf="label" [for]="id" class="form-label">{{ label }}</label>
      <a *ngIf="linkText && linkHref" [href]="linkHref" class="forgot-password">{{ linkText }}</a>

      <div [class.password-field]="type === 'password'">
        <input
          [type]="currentType()"
          [id]="id"
          [placeholder]="placeholder"
          [value]="value()"
          (input)="onInput($event)"
          (blur)="onTouched()"
          [disabled]="disabled()"
          class="form-control"
          [class.is-invalid]="showError()"
        />

        <button
          *ngIf="type === 'password'"
          type="button"
          class="password-toggle"
          (click)="togglePasswordVisibility()"
        >
          <i [class]="currentType() === 'password' ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
        </button>
      </div>

      <div *ngIf="showError() && errorMessage" class="invalid-feedback d-block">
        {{ errorMessage }}
      </div>
    </div>
  `,
  styles: [`
    .form-label {
      font-size: 0.9rem;
      font-weight: 500;
      color: #1f2937;
      margin-bottom: 0.5rem;
    }

    .form-control {
      padding: 0.75rem 1rem;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      font-size: 0.9rem;
      transition: all 0.3s;
    }

    .form-control:focus {
      border-color: #a855f7;
      box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.1);
      outline: none;
    }

    .form-control::placeholder {
      color: #9ca3af;
    }

    .password-field {
      position: relative;
    }

    .password-toggle {
      position: absolute;
      right: 1rem;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      color: #6b7280;
      cursor: pointer;
      padding: 0.25rem;
    }

    .forgot-password {
      color: #ef4444;
      text-decoration: none;
      font-size: 0.875rem;
      float: right;
      margin-top: -0.25rem;
    }

    .forgot-password:hover {
      text-decoration: underline;
    }

    .is-invalid {
      border-color: #ef4444;
    }

    .invalid-feedback {
      color: #ef4444;
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }
  `]
})
export class InputComponent implements ControlValueAccessor {
  @Input() id = '';
  @Input() label = '';
  @Input() type: 'text' | 'password' | 'email' = 'text';
  @Input() placeholder = '';
  @Input() linkText = '';
  @Input() linkHref = '';
  @Input() errorMessage = '';
  @Input() showError = signal(false);

  // Signals para estado interno
  value = signal('');
  disabled = signal(false);
  currentType = signal<'text' | 'password' | 'email'>('text');

  private onChange: (value: string) => void = () => {};
  onTouched: () => void = () => {};

  constructor() {
    this.currentType.set(this.type);
  }

  writeValue(value: string): void {
    this.value.set(value || '');
  }

  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled.set(isDisabled);
  }

  onInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    const newValue = input.value;
    this.value.set(newValue);
    this.onChange(newValue);
  }

  togglePasswordVisibility(): void {
    this.currentType.set(this.currentType() === 'password' ? 'text' : 'password');
  }
}
