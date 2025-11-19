import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../../core/services/auth.service';
import { InputComponent } from '../../../shared/components/input/input.component';
import { ButtonComponent } from '../../../shared/components/button/button.component';

/**
 * Componente de Login standalone
 * Single Responsibility: Solo maneja la UI del login
 * Dependency Injection: Usa inject() moderno
 */
@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, InputComponent, ButtonComponent],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  private readonly authService = inject(AuthService);
  private readonly fb = inject(FormBuilder);

  // Signals para estado del componente
  loginForm: FormGroup;
  errorMessage = signal('');
  showPassword = signal(false);

  // Computed signal del AuthService
  isLoading = this.authService.isLoading;

  constructor() {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      remember: [false]
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      this.markFormGroupTouched(this.loginForm);
      return;
    }

    const { email, password } = this.loginForm.value;
    this.errorMessage.set('');

    this.authService.login({ email, password }).subscribe({
      next: () => {
        // El AuthService maneja la navegación
      },
      error: (error) => {
        console.error('Login error:', error);

        // Manejar diferentes tipos de errores
        let message = '';

        if (error.status === 0) {
          message = '❌ No se pudo conectar con el servidor. Por favor, verifica tu conexión.';
        } else if (error.status === 400 || error.status === 401) {
          // Intentar obtener el mensaje del error
          if (error.error?.non_field_errors) {
            message = `🔒 ${error.error.non_field_errors[0]?.string || error.error.non_field_errors[0]}`;
          } else if (error.error?.detail) {
            message = `🔒 ${error.error.detail}`;
          } else if (error.error?.message) {
            message = `🔒 ${error.error.message}`;
          } else {
            message = '🔒 Email o contraseña incorrectos. Por favor, verifica tus datos e intenta nuevamente.';
          }
        } else if (error.status === 500) {
          message = '⚠️ Error en el servidor. Por favor, intenta más tarde.';
        } else {
          message = '❌ Ocurrió un error inesperado. Por favor, intenta de nuevo.';
        }

        this.errorMessage.set(message);
      }
    });
  }

  private markFormGroupTouched(formGroup: FormGroup): void {
    Object.keys(formGroup.controls).forEach(key => {
      const control = formGroup.get(key);
      control?.markAsTouched();

      if (control instanceof FormGroup) {
        this.markFormGroupTouched(control);
      }
    });
  }

  get emailErrors(): string {
    const control = this.loginForm.get('email');
    if (control?.hasError('required') && control?.touched) {
      return 'El email es requerido';
    }
    if (control?.hasError('email') && control?.touched) {
      return 'Ingresa un email válido';
    }
    return '';
  }

  get passwordErrors(): string {
    const control = this.loginForm.get('password');
    if (control?.hasError('required') && control?.touched) {
      return 'La contraseña es requerida';
    }
    if (control?.hasError('minlength') && control?.touched) {
      return 'La contraseña debe tener al menos 6 caracteres';
    }
    return '';
  }
}
