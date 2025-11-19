import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { CategoryService } from '../../../../core/services/category.service';
import { Category, CategoryUpdate } from '../../../../core/models/role.model';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

@Component({
  selector: 'app-category-list',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonComponent],
  templateUrl: './category-list.component.html',
  styleUrls: ['./category-list.component.scss']
})
export class CategoryListComponent implements OnInit {
  private readonly categoryService = inject(CategoryService);

  // Signals
  categories = signal<Category[]>([]);
  loading = signal(false);
  editingCategory = signal<number | null>(null);
  editForm = signal<{ name: string; description: string; icon: string; color: string; order: number } | null>(null);

  ngOnInit(): void {
    this.loadCategories();
  }

  loadCategories(): void {
    this.loading.set(true);
    this.categoryService.getCategories().subscribe({
      next: (categories) => {
        // Sort by order, then by name
        const sorted = [...categories].sort((a, b) => {
          if (a.order !== b.order) return a.order - b.order;
          return a.name.localeCompare(b.name);
        });
        this.categories.set(sorted);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading categories:', error);
        this.loading.set(false);
      }
    });
  }

  startEdit(category: Category): void {
    this.editingCategory.set(category.id);
    this.editForm.set({
      name: category.name,
      description: category.description || '',
      icon: category.icon,
      color: category.color || '',
      order: category.order
    });
  }

  cancelEdit(): void {
    this.editingCategory.set(null);
    this.editForm.set(null);
  }

  saveEdit(category: Category): void {
    const form = this.editForm();
    if (!form) return;

    const update: CategoryUpdate = {
      name: form.name,
      description: form.description || undefined,
      icon: form.icon,
      color: form.color || undefined,
      order: form.order
    };

    this.categoryService.updateCategory(category.id, update).subscribe({
      next: () => {
        this.editingCategory.set(null);
        this.editForm.set(null);
        this.loadCategories();
      },
      error: (error) => {
        console.error('Error updating category:', error);
        alert('Error al actualizar la categoría');
      }
    });
  }

  updateEditForm(field: 'name' | 'description' | 'icon' | 'color' | 'order', value: string | number): void {
    const current = this.editForm();
    if (!current) return;

    this.editForm.set({
      ...current,
      [field]: value
    });
  }

  onNameInput(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.updateEditForm('name', value);
  }

  onDescriptionInput(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.updateEditForm('description', value);
  }

  onIconInput(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.updateEditForm('icon', value);
  }

  onColorInput(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.updateEditForm('color', value);
  }

  onOrderInput(event: Event): void {
    const value = (event.target as HTMLInputElement).valueAsNumber;
    this.updateEditForm('order', value);
  }

  isEditing(category: Category): boolean {
    return this.editingCategory() === category.id;
  }

  getIconClass(icon: string): string {
    return icon || 'fas fa-folder';
  }

  getCodeDisplay(code: string): string {
    return code || 'N/A';
  }

  getColorDisplay(color?: string): string {
    return color || '#3498db';
  }

  getFunctionsCountDisplay(count?: number): string {
    if (count === undefined || count === 0) return '0 funciones';
    if (count === 1) return '1 función';
    return `${count} funciones`;
  }
}
