import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Role, RoleCreate, RoleUpdate, RoleAssignment, RoleAssignmentCreate } from '../models/role.model';
import { User } from '../models/user.model';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

@Injectable({
  providedIn: 'root'
})
export class RoleService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/permissions/roles`;
  private readonly assignmentUrl = `${environment.apiUrl}/permissions/role-assignments`;

  /**
   * Get list of roles (no pagination, direct array)
   */
  getRoles(filters?: { search?: string; is_active?: boolean }): Observable<Role[]> {
    let params = new HttpParams();

    if (filters) {
      if (filters.search) params = params.set('search', filters.search);
      if (filters.is_active !== undefined) params = params.set('is_active', filters.is_active);
    }

    return this.http.get<Role[]>(this.apiUrl + '/', { params });
  }

  /**
   * Get a single role by ID
   */
  getRole(id: number): Observable<Role> {
    return this.http.get<Role>(`${this.apiUrl}/${id}/`);
  }

  /**
   * Create a new role
   */
  createRole(role: RoleCreate): Observable<Role> {
    return this.http.post<Role>(this.apiUrl + '/', role);
  }

  /**
   * Update role
   */
  updateRole(id: number, role: RoleUpdate): Observable<Role> {
    return this.http.put<Role>(`${this.apiUrl}/${id}/`, role);
  }

  /**
   * Partial update role
   */
  patchRole(id: number, role: Partial<RoleUpdate>): Observable<Role> {
    return this.http.patch<Role>(`${this.apiUrl}/${id}/`, role);
  }

  /**
   * Delete role (cannot delete system roles)
   */
  deleteRole(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }

  /**
   * Get users assigned to a role
   */
  getRoleUsers(roleId: number): Observable<User[]> {
    return this.http.get<User[]>(`${this.apiUrl}/${roleId}/users/`);
  }

  /**
   * Get role assignments
   */
  getRoleAssignments(filters?: { user?: number; role?: number }): Observable<PaginatedResponse<RoleAssignment>> {
    let params = new HttpParams();

    if (filters) {
      if (filters.user) params = params.set('user', filters.user);
      if (filters.role) params = params.set('role', filters.role);
    }

    return this.http.get<PaginatedResponse<RoleAssignment>>(this.assignmentUrl + '/', { params });
  }

  /**
   * Assign role to user
   */
  assignRole(assignment: RoleAssignmentCreate): Observable<RoleAssignment> {
    return this.http.post<RoleAssignment>(this.assignmentUrl + '/', assignment);
  }

  /**
   * Remove role assignment
   */
  removeRoleAssignment(assignmentId: number): Observable<void> {
    return this.http.delete<void>(`${this.assignmentUrl}/${assignmentId}/`);
  }

  /**
   * Check if role can be deleted
   */
  canDeleteRole(role: Role): boolean {
    // System roles cannot be deleted
    return !role.is_system;
  }

  /**
   * Check if role can be edited
   */
  canEditRole(role: Role): boolean {
    // System roles have limited editing (can only edit name and some fields)
    return true; // All roles can be edited, but system roles have restrictions
  }
}
