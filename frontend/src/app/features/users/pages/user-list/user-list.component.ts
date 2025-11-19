import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { UserService } from '../../../../core/services/user.service';
import { AuthService } from '../../../../core/services/auth.service';
import { RoleService } from '../../../../core/services/role.service';
import { User } from '../../../../core/models/user.model';
import { Role } from '../../../../core/models/role.model';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, ButtonComponent],
  templateUrl: './user-list.component.html',
  styleUrls: ['./user-list.component.scss']
})
export class UserListComponent implements OnInit {
  private readonly userService = inject(UserService);
  private readonly authService = inject(AuthService);
  private readonly roleService = inject(RoleService);

  // Expose Math for template
  Math = Math;

  // Signals
  users = signal<User[]>([]);
  availableRoles = signal<Role[]>([]);
  loading = signal(false);
  currentUser = this.authService.currentUser;

  // Pagination
  currentPage = signal(1);
  pageSize = signal(10);
  totalUsers = signal(0);

  // Filters
  searchTerm = signal('');
  filterStatus = signal<'all' | 'active' | 'inactive'>('all');
  filterType = signal<'all' | 'EMPLOYEE' | 'CUSTOMER' | 'SUPPLIER'>('all');

  // Modal
  showCreateModal = signal(false);
  showEditModal = signal(false);
  selectedUser = signal<User | null>(null);

  // Form data
  userForm: any = {
    email: '',
    username: '',
    password: '',
    first_name: '',
    last_name: '',
    ci: '',
    phone: '',
    address: '',
    city: '',
    country: 'Bolivia',
    birth_date: '',
    is_staff: false,
    is_active: true,
    role_ids: []
  };

  ngOnInit(): void {
    this.loadUsers();
    this.loadRoles();
  }

  loadRoles(): void {
    this.roleService.getRoles({ is_active: true }).subscribe({
      next: (roles) => {
        this.availableRoles.set(roles);
      },
      error: (err) => {
        console.error('Error loading roles:', err);
      }
    });
  }

  // Track selected roles as individual selects
  selectedRoles: (number | null)[] = [null];

  initializeRoles(): void {
    if (this.userForm.role_ids && this.userForm.role_ids.length > 0) {
      this.selectedRoles = [...this.userForm.role_ids];
    } else {
      this.selectedRoles = [null];
    }
  }

  addRoleSelector(): void {
    this.selectedRoles.push(null);
  }

  removeRoleSelector(index: number): void {
    if (this.selectedRoles.length > 1) {
      this.selectedRoles.splice(index, 1);
      this.updateRoleIds();
    }
  }

  onRoleChange(index: number, event: Event): void {
    const value = (event.target as HTMLSelectElement).value;
    this.selectedRoles[index] = value ? parseInt(value, 10) : null;
    this.updateRoleIds();
  }

  updateRoleIds(): void {
    this.userForm.role_ids = this.selectedRoles.filter(id => id !== null) as number[];
  }

  getAvailableRolesForSelect(currentIndex: number): Role[] {
    const selectedIds = this.selectedRoles
      .map((id, idx) => idx !== currentIndex ? id : null)
      .filter(id => id !== null);

    // Filter out the basic_user role (it's assigned automatically and cannot be removed)
    return this.availableRoles().filter(role =>
      !selectedIds.includes(role.id) &&
      !(role.code === 'basic_user' && role.is_system)
    );
  }

  canRemoveRoleSelector(): boolean {
    return this.selectedRoles.length > 1;
  }

  loadUsers(): void {
    this.loading.set(true);

    const filters: any = {
      page: this.currentPage(),
      page_size: this.pageSize(),
    };

    if (this.searchTerm()) {
      filters.search = this.searchTerm();
    }

    if (this.filterStatus() !== 'all') {
      filters.is_active = this.filterStatus() === 'active';
    }

    if (this.filterType() !== 'all') {
      filters.user_type = this.filterType();
    }

    this.userService.getUsers(filters).subscribe({
      next: (response) => {
        this.users.set(response.results);
        this.totalUsers.set(response.count);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading users:', error);
        this.loading.set(false);
      }
    });
  }

  onSearch(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.searchTerm.set(value);
    this.currentPage.set(1);
    this.loadUsers();
  }

  onFilterStatusChange(event: Event): void {
    const value = (event.target as HTMLSelectElement).value as 'all' | 'active' | 'inactive';
    this.filterStatus.set(value);
    this.currentPage.set(1);
    this.loadUsers();
  }

  onFilterTypeChange(event: Event): void {
    const value = (event.target as HTMLSelectElement).value as any;
    this.filterType.set(value);
    this.currentPage.set(1);
    this.loadUsers();
  }

  onPageChange(page: number): void {
    this.currentPage.set(page);
    this.loadUsers();
  }

  getTotalPages(): number {
    return Math.ceil(this.totalUsers() / this.pageSize());
  }

  canEdit(user: User): boolean {
    return this.userService.canEditUser(user, this.currentUser()!);
  }

  canDelete(user: User): boolean {
    return this.userService.canDeleteUser(user, this.currentUser()!);
  }

  onCreateUser(): void {
    this.userForm = {
      email: '',
      username: '',
      password: '',
      first_name: '',
      last_name: '',
      ci: '',
      phone: '',
      address: '',
      city: '',
      country: 'Bolivia',
      birth_date: '',
      is_staff: false,
      is_active: true,
      role_ids: []
    };
    this.selectedRoles = [null];
    this.showCreateModal.set(true);
  }

  onEditUser(user: User): void {
    if (!this.canEdit(user)) {
      alert('No puedes editar este usuario');
      return;
    }
    this.selectedUser.set(user);
    this.userForm = {
      email: user.email,
      username: user.username,
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      ci: user.ci || '',
      phone: user.phone || '',
      address: user.address || '',
      city: user.city || '',
      country: user.country || 'Bolivia',
      birth_date: user.birth_date || '',
      is_staff: user.is_staff,
      is_active: user.is_active,
      role_ids: user.roles?.map(r => r.id) || []
    };
    this.initializeRoles();
    this.showEditModal.set(true);
  }

  closeForm(): void {
    this.showCreateModal.set(false);
    this.showEditModal.set(false);
    this.selectedUser.set(null);
  }

  onSubmitForm(): void {
    if (this.showCreateModal()) {
      // Create user
      this.userService.createUser(this.userForm).subscribe({
        next: () => {
          this.closeForm();
          this.loadUsers();
          alert('Usuario creado exitosamente');
        },
        error: (error) => {
          console.error('Error creating user:', error);
          const message = error.error?.detail || error.error?.message || 'Error al crear el usuario';
          alert(message);
        }
      });
    } else if (this.showEditModal()) {
      // Update user
      const userId = this.selectedUser()?.id;
      if (!userId) return;

      const updateData = {
        first_name: this.userForm.first_name,
        last_name: this.userForm.last_name,
        ci: this.userForm.ci,
        phone: this.userForm.phone,
        address: this.userForm.address,
        city: this.userForm.city,
        country: this.userForm.country,
        birth_date: this.userForm.birth_date,
        is_staff: this.userForm.is_staff,
        is_active: this.userForm.is_active,
        role_ids: this.userForm.role_ids
      };

      this.userService.patchUser(userId, updateData).subscribe({
        next: () => {
          this.closeForm();
          this.loadUsers();
          alert('Usuario actualizado exitosamente');
        },
        error: (error) => {
          console.error('Error updating user:', error);
          const message = error.error?.detail || error.error?.message || 'Error al actualizar el usuario';
          alert(message);
        }
      });
    }
  }

  onDeleteUser(user: User): void {
    if (!this.canDelete(user)) {
      alert('No puedes eliminar este usuario');
      return;
    }

    if (confirm(`¿Estás seguro de eliminar al usuario ${user.full_name}?`)) {
      this.userService.deleteUser(user.id).subscribe({
        next: () => {
          this.loadUsers();
        },
        error: (error) => {
          console.error('Error deleting user:', error);
          alert('Error al eliminar el usuario');
        }
      });
    }
  }

  onToggleStatus(user: User): void {
    this.userService.toggleUserStatus(user.id, !user.is_active).subscribe({
      next: () => {
        this.loadUsers();
      },
      error: (error) => {
        console.error('Error toggling user status:', error);
        alert('Error al cambiar el estado del usuario');
      }
    });
  }

}
