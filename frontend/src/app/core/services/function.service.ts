import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Function, FunctionCreate, FunctionUpdate } from '../models/role.model';

interface ReorderRequest {
  function_id: number;
  new_order: number;
}

@Injectable({
  providedIn: 'root'
})
export class FunctionService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/navigation/functions`;

  /**
   * Get list of all functions (flat)
   */
  getFunctions(): Observable<Function[]> {
    return this.http.get<Function[]>(this.apiUrl + '/');
  }

  /**
   * Get functions as hierarchical tree
   */
  getFunctionTree(): Observable<Function[]> {
    return this.http.get<Function[]>(`${this.apiUrl}/tree/`);
  }

  /**
   * Get a single function by ID
   */
  getFunction(id: number): Observable<Function> {
    return this.http.get<Function>(`${this.apiUrl}/${id}/`);
  }

  /**
   * Create a new function (admin only - for hardcoded functions)
   * Note: In production, this should be restricted as functions are mostly hardcoded
   */
  createFunction(func: FunctionCreate): Observable<Function> {
    return this.http.post<Function>(this.apiUrl + '/', func);
  }

  /**
   * Update function (only name and order can be edited)
   */
  updateFunction(id: number, func: FunctionUpdate): Observable<Function> {
    return this.http.patch<Function>(`${this.apiUrl}/${id}/`, func);
  }

  /**
   * Delete function
   * Note: Should be restricted in production
   */
  deleteFunction(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }

  /**
   * Reorder functions
   */
  reorderFunctions(reorders: ReorderRequest[]): Observable<void> {
    return this.http.post<void>(`${this.apiUrl}/reorder/`, { reorders });
  }

  /**
   * Check if function field can be edited
   */
  canEditField(fieldName: string): boolean {
    // Only name, category, order, and is_active can be edited
    const editableFields = ['name', 'category', 'order', 'is_active'];
    return editableFields.includes(fieldName);
  }

  /**
   * Get editable fields
   */
  getEditableFields(): string[] {
    return ['name', 'category', 'order', 'is_active'];
  }
}
