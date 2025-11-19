import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { FunctionService } from '../../../../core/services/function.service';
import { CategoryService } from '../../../../core/services/category.service';
import { Function, FunctionUpdate, Category } from '../../../../core/models/role.model';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

@Component({
  selector: 'app-function-list',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonComponent],
  templateUrl: './function-list.component.html',
  styleUrls: ['./function-list.component.scss']
})
export class FunctionListComponent implements OnInit {
  private readonly functionService = inject(FunctionService);
  private readonly categoryService = inject(CategoryService);

  // Signals
  functions = signal<Function[]>([]);
  categories = signal<Category[]>([]);
  loading = signal(false);
  editingFunction = signal<number | null>(null);
  editForm = signal<{ name: string; order: number; category: number | null } | null>(null);

  ngOnInit(): void {
    this.loadCategories();
    this.loadFunctions();
  }

  loadCategories(): void {
    this.categoryService.getCategories().subscribe({
      next: (categories) => {
        this.categories.set(categories);
      },
      error: (error) => {
        console.error('Error loading categories:', error);
      }
    });
  }

  loadFunctions(): void {
    this.loading.set(true);
    this.functionService.getFunctions().subscribe({
      next: (functions) => {
        // Sort by order, then by name
        const sorted = [...functions].sort((a, b) => {
          if (a.order !== b.order) return a.order - b.order;
          return a.name.localeCompare(b.name);
        });
        this.functions.set(sorted);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading functions:', error);
        this.loading.set(false);
      }
    });
  }

  startEdit(func: Function): void {
    this.editingFunction.set(func.id);
    this.editForm.set({
      name: func.name,
      order: func.order,
      category: func.category || null
    });
  }

  cancelEdit(): void {
    this.editingFunction.set(null);
    this.editForm.set(null);
  }

  saveEdit(func: Function): void {
    const form = this.editForm();
    if (!form) return;

    const update: FunctionUpdate = {
      name: form.name,
      order: form.order,
      category: form.category || undefined
    };

    this.functionService.updateFunction(func.id, update).subscribe({
      next: () => {
        this.editingFunction.set(null);
        this.editForm.set(null);
        this.loadFunctions();
      },
      error: (error) => {
        console.error('Error updating function:', error);
        alert('Error al actualizar la función');
      }
    });
  }

  updateEditForm(field: 'name' | 'order' | 'category', value: string | number | null): void {
    const current = this.editForm();
    if (!current) return;

    this.editForm.set({
      ...current,
      [field]: value
    });
  }

  onOrderInput(event: Event): void {
    const value = (event.target as HTMLInputElement).valueAsNumber;
    this.updateEditForm('order', value);
  }

  onNameInput(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.updateEditForm('name', value);
  }

  onCategoryChange(event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    const categoryId = value ? parseInt(value, 10) : null;
    this.updateEditForm('category', categoryId);
  }

  isEditing(func: Function): boolean {
    return this.editingFunction() === func.id;
  }

  getIconClass(icon: string): string {
    return icon || 'fas fa-circle';
  }

  getRouteDisplay(url: string | null): string {
    return url || '/';
  }

  getCodeDisplay(code: string): string {
    return code || 'N/A';
  }

  getCategoryDisplay(categoryName?: string): string {
    return categoryName || 'Sin categoría';
  }
}
