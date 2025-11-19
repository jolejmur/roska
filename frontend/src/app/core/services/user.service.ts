import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { User, UserCreate, UserUpdate } from '../models/user.model';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

interface UserFilters {
  search?: string;
  is_active?: boolean;
  is_staff?: boolean;
  user_type?: string;
  page?: number;
  page_size?: number;
}

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/users`;

  /**
   * Get list of users with optional filters
   */
  getUsers(filters?: UserFilters): Observable<PaginatedResponse<User>> {
    let params = new HttpParams();

    if (filters) {
      if (filters.search) params = params.set('search', filters.search);
      if (filters.is_active !== undefined) params = params.set('is_active', filters.is_active);
      if (filters.is_staff !== undefined) params = params.set('is_staff', filters.is_staff);
      if (filters.user_type) params = params.set('user_type', filters.user_type);
      if (filters.page) params = params.set('page', filters.page);
      if (filters.page_size) params = params.set('page_size', filters.page_size);
    }

    return this.http.get<PaginatedResponse<User>>(this.apiUrl + '/', { params });
  }

  /**
   * Get a single user by ID
   */
  getUser(id: number): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/${id}/`);
  }

  /**
   * Create a new user (superadmin only)
   */
  createUser(user: UserCreate): Observable<User> {
    return this.http.post<User>(this.apiUrl + '/', user);
  }

  /**
   * Update user (full update)
   */
  updateUser(id: number, user: UserUpdate): Observable<User> {
    return this.http.put<User>(`${this.apiUrl}/${id}/`, user);
  }

  /**
   * Partial update user
   */
  patchUser(id: number, user: Partial<UserUpdate>): Observable<User> {
    return this.http.patch<User>(`${this.apiUrl}/${id}/`, user);
  }

  /**
   * Delete user (superadmin only)
   */
  deleteUser(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }

  /**
   * Toggle user active status
   */
  toggleUserStatus(id: number, is_active: boolean): Observable<User> {
    return this.http.patch<User>(`${this.apiUrl}/${id}/`, { is_active });
  }

  /**
   * Check if user can be edited (superadmin cannot be edited)
   */
  canEditUser(user: User, currentUser: User): boolean {
    // Super admin cannot be edited by anyone (including themselves)
    if (user.is_superuser) {
      return false;
    }

    // Current user must be staff or superuser to edit others
    return currentUser.is_staff || currentUser.is_superuser;
  }

  /**
   * Check if user can be deleted
   */
  canDeleteUser(user: User, currentUser: User): boolean {
    // Super admin cannot be deleted
    if (user.is_superuser) {
      return false;
    }

    // Cannot delete yourself
    if (user.id === currentUser.id) {
      return false;
    }

    // Only superuser can delete
    return currentUser.is_superuser;
  }
}
