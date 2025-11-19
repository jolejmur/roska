import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RoleService } from '../../../../core/services/role.service';
import { FunctionService } from '../../../../core/services/function.service';
import { Role, RoleCreate, RoleUpdate, Function } from '../../../../core/models/role.model';

@Component({
  selector: 'app-role-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './role-list.component.html',
  styleUrls: ['./role-list.component.scss']
})
export class RoleListComponent implements OnInit {
  private readonly roleService = inject(RoleService);
  private readonly functionService = inject(FunctionService);

  roles = signal<Role[]>([]);
  availableFunctions = signal<Function[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);

  isCreating = signal(false);
  editingRole = signal<Role | null>(null);
  expandedRoleId = signal<number | null>(null);

  newRole: RoleCreate = {
    name: '',
    code: '',
    description: '',
    cerbos_role: '',
    is_active: true,
    function_ids: []
  };

  // Track which categories are expanded in create form
  expandedCategoriesCreate = signal<Set<string>>(new Set());
  // Track which categories are expanded in edit form
  expandedCategoriesEdit = signal<Set<string>>(new Set());

  editForm = signal<RoleUpdate>({});

  ngOnInit(): void {
    this.loadRoles();
    this.loadFunctions();
  }

  loadRoles(): void {
    this.loading.set(true);
    this.error.set(null);

    this.roleService.getRoles().subscribe({
      next: (roles) => {
        this.roles.set(roles);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Error al cargar roles: ' + err.message);
        this.loading.set(false);
      }
    });
  }

  loadFunctions(): void {
    this.functionService.getFunctions().subscribe({
      next: (functions) => {
        this.availableFunctions.set(functions);
      },
      error: (err) => {
        console.error('Error loading functions:', err);
      }
    });
  }

  // Create
  startCreating(): void {
    this.isCreating.set(true);
    this.newRole = {
      name: '',
      code: '',
      description: '',
      cerbos_role: '',
      is_active: true,
      function_ids: []
    };
    this.expandedCategoriesCreate.set(new Set());
  }

  // Auto-generate code and cerbos_role from name
  onNameChange(): void {
    if (this.newRole.name) {
      const generatedCode = this.newRole.name
        .toLowerCase()
        .replace(/\s+/g, '_')
        .replace(/[^a-z0-9_]/g, '');
      this.newRole.code = generatedCode;
      this.newRole.cerbos_role = generatedCode;
    }
  }

  cancelCreate(): void {
    this.isCreating.set(false);
  }

  isFormValid(): boolean {
    return !!(
      this.newRole.name &&
      this.newRole.code &&
      this.newRole.description &&
      this.newRole.cerbos_role
    );
  }

  isFunctionSelected(functionId: number): boolean {
    return this.newRole.function_ids?.includes(functionId) || false;
  }

  toggleFunctionForNew(functionId: number): void {
    if (!this.newRole.function_ids) {
      this.newRole.function_ids = [];
    }
    const functionIds = this.newRole.function_ids;
    const index = functionIds.indexOf(functionId);
    if (index > -1) {
      functionIds.splice(index, 1);
    } else {
      functionIds.push(functionId);
    }
  }

  createRole(): void {
    if (!this.isFormValid()) return;

    this.roleService.createRole(this.newRole).subscribe({
      next: () => {
        this.isCreating.set(false);
        this.loadRoles();
      },
      error: (err) => {
        this.error.set('Error al crear rol: ' + err.message);
      }
    });
  }

  // Edit
  isEditing(role: Role): boolean {
    return this.editingRole()?.id === role.id;
  }

  startEdit(role: Role): void {
    if (role.is_system) return;

    this.editingRole.set(role);
    this.editForm.set({
      name: role.name,
      description: role.description,
      is_active: role.is_active,
      level: role.level,
      function_ids: role.functions?.map(f => f.id) || []
    });

    // Auto-expand to show functions
    if (this.expandedRoleId() !== role.id) {
      this.toggleFunctionsView(role.id);
    }
  }

  cancelEdit(): void {
    this.editingRole.set(null);
    this.editForm.set({});
  }

  isFunctionInEditForm(functionId: number): boolean {
    return this.editForm().function_ids?.includes(functionId) || false;
  }

  toggleFunction(functionId: number): void {
    const currentIds = this.editForm().function_ids || [];
    const index = currentIds.indexOf(functionId);

    if (index > -1) {
      currentIds.splice(index, 1);
    } else {
      currentIds.push(functionId);
    }

    this.editForm.update(form => ({
      ...form,
      function_ids: [...currentIds]
    }));
  }

  saveEdit(roleId: number): void {
    this.roleService.patchRole(roleId, this.editForm()).subscribe({
      next: () => {
        this.editingRole.set(null);
        this.editForm.set({});
        this.loadRoles();
      },
      error: (err) => {
        this.error.set('Error al actualizar rol: ' + err.message);
      }
    });
  }

  // Delete
  deleteRole(role: Role): void {
    if (role.is_system) {
      this.error.set('No se pueden eliminar roles del sistema');
      return;
    }

    if (!confirm(`¿Estás seguro de eliminar el rol "${role.name}"?`)) {
      return;
    }

    this.roleService.deleteRole(role.id).subscribe({
      next: () => {
        this.roles.update(roles => roles.filter(r => r.id !== role.id));
      },
      error: (err) => {
        this.error.set('Error al eliminar rol: ' + err.message);
      }
    });
  }

  // Expand/Collapse Functions View
  toggleFunctionsView(roleId: number): void {
    if (this.expandedRoleId() === roleId) {
      this.expandedRoleId.set(null);
      this.expandedCategoriesEdit.set(new Set());
    } else {
      // Load role with functions details
      this.roleService.getRole(roleId).subscribe({
        next: (role) => {
          this.roles.update(roles =>
            roles.map(r => r.id === roleId ? role : r)
          );
          this.expandedRoleId.set(roleId);
          this.expandedCategoriesEdit.set(new Set());
        },
        error: (err) => {
          this.error.set('Error al cargar funciones: ' + err.message);
        }
      });
    }
  }

  // Group functions by category
  getFunctionsByCategory(): Map<string, Function[]> {
    const grouped = new Map<string, Function[]>();

    this.availableFunctions().forEach(func => {
      const categoryName = func.category_name || 'Sin categoría';
      if (!grouped.has(categoryName)) {
        grouped.set(categoryName, []);
      }
      grouped.get(categoryName)!.push(func);
    });

    return grouped;
  }

  // Toggle category expansion for create form
  toggleCategoryCreate(categoryName: string): void {
    const expanded = new Set(this.expandedCategoriesCreate());
    if (expanded.has(categoryName)) {
      expanded.delete(categoryName);
    } else {
      expanded.add(categoryName);
    }
    this.expandedCategoriesCreate.set(expanded);
  }

  // Toggle category expansion for edit form
  toggleCategoryEdit(categoryName: string): void {
    const expanded = new Set(this.expandedCategoriesEdit());
    if (expanded.has(categoryName)) {
      expanded.delete(categoryName);
    } else {
      expanded.add(categoryName);
    }
    this.expandedCategoriesEdit.set(expanded);
  }

  // Check if category is expanded in create form
  isCategoryExpandedCreate(categoryName: string): boolean {
    return this.expandedCategoriesCreate().has(categoryName);
  }

  // Check if category is expanded in edit form
  isCategoryExpandedEdit(categoryName: string): boolean {
    return this.expandedCategoriesEdit().has(categoryName);
  }

  // Get functions in a category
  getFunctionsInCategory(categoryName: string): Function[] {
    return this.availableFunctions().filter(f =>
      (f.category_name || 'Sin categoría') === categoryName
    );
  }
}
