import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Category, CategoryCreate, CategoryUpdate, Function } from '../models/role.model';

interface ReorderRequest {
  categories: { id: number; order: number }[];
}

@Injectable({
  providedIn: 'root'
})
export class CategoryService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/navigation/categories`;

  /**
   * Get list of all categories
   */
  getCategories(isActive?: boolean): Observable<Category[]> {
    const params: any = {};
    if (isActive !== undefined) {
      params['is_active'] = isActive;
    }
    return this.http.get<Category[]>(this.apiUrl + '/', { params });
  }

  /**
   * Get a single category by ID
   */
  getCategory(id: number): Observable<Category> {
    return this.http.get<Category>(`${this.apiUrl}/${id}/`);
  }

  /**
   * Get functions belonging to a category
   */
  getCategoryFunctions(id: number): Observable<Function[]> {
    return this.http.get<Function[]>(`${this.apiUrl}/${id}/functions/`);
  }

  /**
   * Create a new category (admin only)
   */
  createCategory(category: CategoryCreate): Observable<Category> {
    return this.http.post<Category>(this.apiUrl + '/', category);
  }

  /**
   * Update category
   */
  updateCategory(id: number, category: CategoryUpdate): Observable<Category> {
    return this.http.patch<Category>(`${this.apiUrl}/${id}/`, category);
  }

  /**
   * Delete category (admin only)
   */
  deleteCategory(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }

  /**
   * Reorder categories
   */
  reorderCategories(reorders: ReorderRequest): Observable<{ message: string; updated_count: number }> {
    return this.http.post<{ message: string; updated_count: number }>(`${this.apiUrl}/reorder/`, reorders);
  }

  /**
   * Check if category field can be edited
   */
  canEditField(fieldName: string): boolean {
    const editableFields = ['name', 'description', 'icon', 'color', 'order', 'is_active'];
    return editableFields.includes(fieldName);
  }

  /**
   * Get editable fields
   */
  getEditableFields(): string[] {
    return ['name', 'description', 'icon', 'color', 'order', 'is_active'];
  }
}
