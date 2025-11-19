import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '@environments/environment';

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_superuser: boolean;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  token_type: string;
  user: User;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = `${environment.apiUrl}/auth`;

  // Signals for reactive state management
  currentUser = signal<User | null>(null);
  isAuthenticated = signal<boolean>(false);

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    this.loadUserFromStorage();
  }

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.apiUrl}/login/`, { email, password })
      .pipe(
        tap(response => {
          this.setSession(response);
        })
      );
  }

  logout(): Observable<any> {
    const refreshToken = localStorage.getItem('refresh_token');
    return this.http.post(`${this.apiUrl}/logout/`, { refresh: refreshToken })
      .pipe(
        tap(() => {
          this.clearSession();
        })
      );
  }

  refreshToken(): Observable<{ access: string; token_type: string }> {
    const refreshToken = localStorage.getItem('refresh_token');
    return this.http.post<{ access: string; token_type: string }>(
      `${this.apiUrl}/refresh/`,
      { refresh: refreshToken }
    ).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access);
      })
    );
  }

  private setSession(authResult: LoginResponse): void {
    localStorage.setItem('access_token', authResult.access);
    localStorage.setItem('refresh_token', authResult.refresh);
    localStorage.setItem('user', JSON.stringify(authResult.user));

    this.currentUser.set(authResult.user);
    this.isAuthenticated.set(true);
  }

  private clearSession(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');

    this.currentUser.set(null);
    this.isAuthenticated.set(false);

    this.router.navigate(['/auth/login']);
  }

  private loadUserFromStorage(): void {
    const userStr = localStorage.getItem('user');
    const token = localStorage.getItem('access_token');

    if (userStr && token) {
      const user = JSON.parse(userStr);
      this.currentUser.set(user);
      this.isAuthenticated.set(true);
    }
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }
}
