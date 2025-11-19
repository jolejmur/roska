import { Injectable, signal, computed, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap, catchError, throwError } from 'rxjs';
import { User, LoginRequest, LoginResponse, AuthTokens } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly API_URL = 'http://localhost:8000/api';

  // Signals para estado reactivo
  private readonly currentUserSignal = signal<User | null>(null);
  private readonly tokensSignal = signal<AuthTokens | null>(null);
  private readonly isLoadingSignal = signal<boolean>(false);

  // Computed signals (solo lectura)
  readonly currentUser = this.currentUserSignal.asReadonly();
  readonly tokens = this.tokensSignal.asReadonly();
  readonly isLoading = this.isLoadingSignal.asReadonly();
  readonly isAuthenticated = computed(() => !!this.currentUserSignal());

  constructor() {
    this.loadStoredAuth();
  }

  /**
   * Login del usuario
   * Single Responsibility: Solo maneja la autenticación
   */
  login(credentials: LoginRequest): Observable<LoginResponse> {
    this.isLoadingSignal.set(true);

    return this.http.post<LoginResponse>(`${this.API_URL}/auth/login/`, credentials).pipe(
      tap(response => {
        this.handleAuthSuccess(response);
      }),
      catchError(error => {
        this.isLoadingSignal.set(false);
        return throwError(() => error);
      })
    );
  }

  /**
   * Logout del usuario
   */
  logout(): void {
    const refreshToken = this.tokensSignal()?.refresh;

    if (refreshToken) {
      // Intentar hacer logout en el backend
      this.http.post(`${this.API_URL}/auth/logout/`, { refresh: refreshToken })
        .subscribe();
    }

    this.clearAuth();
    this.router.navigate(['/login']);
  }

  /**
   * Refrescar access token
   */
  refreshToken(): Observable<{ access: string; token_type: string }> {
    const refreshToken = this.tokensSignal()?.refresh;

    if (!refreshToken) {
      return throwError(() => new Error('No refresh token available'));
    }

    return this.http.post<{ access: string; token_type: string }>(
      `${this.API_URL}/auth/refresh/`,
      { refresh: refreshToken }
    ).pipe(
      tap(response => {
        const currentTokens = this.tokensSignal();
        if (currentTokens) {
          const newTokens: AuthTokens = {
            access: response.access,
            refresh: currentTokens.refresh
          };
          this.tokensSignal.set(newTokens);
          this.saveTokens(newTokens);
        }
      }),
      catchError(error => {
        this.clearAuth();
        return throwError(() => error);
      })
    );
  }

  /**
   * Obtener usuario actual del backend
   */
  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.API_URL}/users/me/`).pipe(
      tap(user => this.currentUserSignal.set(user))
    );
  }

  /**
   * Obtener access token actual
   */
  getAccessToken(): string | null {
    return this.tokensSignal()?.access || null;
  }

  // Private methods (Open/Closed Principle)

  private handleAuthSuccess(response: LoginResponse): void {
    const tokens: AuthTokens = {
      access: response.access,
      refresh: response.refresh
    };

    this.currentUserSignal.set(response.user);
    this.tokensSignal.set(tokens);
    this.isLoadingSignal.set(false);

    this.saveTokens(tokens);
    this.saveUser(response.user);

    this.router.navigate(['/profile']);
  }

  private clearAuth(): void {
    this.currentUserSignal.set(null);
    this.tokensSignal.set(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_user');
  }

  private saveTokens(tokens: AuthTokens): void {
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
  }

  private saveUser(user: User): void {
    localStorage.setItem('current_user', JSON.stringify(user));
  }

  private loadStoredAuth(): void {
    const accessToken = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    const userJson = localStorage.getItem('current_user');

    if (accessToken && refreshToken && userJson) {
      try {
        const user = JSON.parse(userJson) as User;
        this.currentUserSignal.set(user);
        this.tokensSignal.set({ access: accessToken, refresh: refreshToken });
      } catch (error) {
        this.clearAuth();
      }
    }
  }
}
