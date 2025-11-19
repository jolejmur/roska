import { Component, Input, forwardRef, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, ReactiveFormsModule } from '@angular/forms';

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
    <div class="w-full">
      <label *ngIf="label" [for]="id" class="block text-sm font-medium text-gray-700 mb-1">{{ label }}</label>
      <div class="relative">
        <input
          [type]="currentType()"
          [id]="id"
          [placeholder]="placeholder"
          [value]="value()"
          (input)="onInput($event)"
          (blur)="onTouched()"
          [disabled]="disabled()"
          class="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          [class.is-invalid]="showError()"
        />
        <button
          *ngIf="type === 'password'"
          type="button"
          class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500"
          (click)="togglePasswordVisibility()"
        >
          <i [class]="currentType() === 'password' ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
        </button>
      </div>
      <div *ngIf="showError() && errorMessage" class="text-xs text-red-600 mt-1">
        {{ errorMessage }}
      </div>
    </div>
  `,
  styles: [`
    // Se eliminan los estilos específicos para usar Tailwind CSS directamente en el template,
    // asegurando consistencia con el resto de la aplicación.
    .is-invalid {
      border-color: #ef4444; // red-500
    }
    .is-invalid:focus {
      box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
    }
  `]
})
export class InputComponent implements ControlValueAccessor {
  @Input() id = '';
  @Input() label = '';
  @Input() type: 'text' | 'password' | 'email' | 'tel' | 'number' = 'text';
  @Input() placeholder = '';
  @Input() errorMessage = '';
  @Input() showError = signal(false);

  value = signal('');
  disabled = signal(false);
  currentType = signal<'text' | 'password' | 'email' | 'tel' | 'number'>('text');

  private onChange: (value: string) => void = () => {};
  onTouched: () => void = () => {};

  ngOnInit() {
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
    const newValue = (event.target as HTMLInputElement).value;
    this.value.set(newValue);
    this.onChange(newValue);
  }

  togglePasswordVisibility(): void {
    this.currentType.set(this.currentType() === 'password' ? 'text' : 'password');
  }
}
