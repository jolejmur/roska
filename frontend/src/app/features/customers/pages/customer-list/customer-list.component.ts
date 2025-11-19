import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { CustomerService } from '../../../../core/services/customer.service';
import { AuthService } from '../../../../core/services/auth.service';
import { Customer } from '../../../../core/models/customer.model';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

@Component({
  selector: 'app-customer-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, ButtonComponent],
  templateUrl: './customer-list.component.html',
  styleUrls: ['./customer-list.component.scss']
})
export class CustomerListComponent implements OnInit {
  private readonly customerService = inject(CustomerService);
  private readonly authService = inject(AuthService);

  // Expose Math for template
  Math = Math;

  // Signals
  customers = signal<Customer[]>([]);
  loading = signal(false);
  currentUser = this.authService.currentUser;

  // Pagination
  currentPage = signal(1);
  pageSize = signal(10);
  totalCustomers = signal(0);

  // Filters
  searchTerm = signal('');
  filterStatus = signal<'all' | 'active' | 'inactive'>('all');
  filterType = signal<'all' | 'INDIVIDUAL' | 'BUSINESS'>('all');

  // Modal
  showDeleteModal = signal(false);
  customerToDelete = signal<Customer | null>(null);

  ngOnInit(): void {
    this.loadCustomers();
  }

  loadCustomers(): void {
    this.loading.set(true);

    const filters: any = {
      page: this.currentPage(),
      page_size: this.pageSize()
    };

    if (this.searchTerm()) {
      filters.search = this.searchTerm();
    }

    if (this.filterStatus() !== 'all') {
      filters.is_active_customer = this.filterStatus() === 'active';
    }

    if (this.filterType() !== 'all') {
      filters.customer_type = this.filterType();
    }

    this.customerService.getCustomers(filters).subscribe({
      next: (response) => {
        this.customers.set(response.results);
        this.totalCustomers.set(response.count);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading customers:', err);
        this.loading.set(false);
      }
    });
  }

  onSearch(): void {
    this.currentPage.set(1);
    this.loadCustomers();
  }

  onFilterChange(): void {
    this.currentPage.set(1);
    this.loadCustomers();
  }

  onPageChange(page: number): void {
    this.currentPage.set(page);
    this.loadCustomers();
  }

  get totalPages(): number {
    return Math.ceil(this.totalCustomers() / this.pageSize());
  }

  get pages(): number[] {
    const total = this.totalPages;
    return Array.from({ length: total }, (_, i) => i + 1);
  }

  toggleCustomerStatus(customer: Customer): void {
    const newStatus = !customer.is_active_customer;
    const action = newStatus ? 'activar' : 'desactivar';

    if (confirm(`¿Está seguro de ${action} este cliente?`)) {
      this.customerService.toggleCustomerStatus(customer.id, newStatus).subscribe({
        next: () => {
          this.loadCustomers();
        },
        error: (err) => {
          console.error('Error updating customer status:', err);
          alert('Error al actualizar el estado del cliente');
        }
      });
    }
  }

  confirmDelete(customer: Customer): void {
    this.customerToDelete.set(customer);
    this.showDeleteModal.set(true);
  }

  deleteCustomer(): void {
    const customer = this.customerToDelete();
    if (!customer) return;

    if (!this.canDeleteCustomer(customer)) {
      alert('No tiene permisos para eliminar este cliente');
      return;
    }

    this.customerService.deleteCustomer(customer.id).subscribe({
      next: () => {
        this.showDeleteModal.set(false);
        this.customerToDelete.set(null);
        this.loadCustomers();
      },
      error: (err) => {
        console.error('Error deleting customer:', err);
        alert('Error al eliminar el cliente');
      }
    });
  }

  canEditCustomer(): boolean {
    const user = this.currentUser();
    return user ? this.customerService.canEditCustomer(user) : false;
  }

  canDeleteCustomer(customer: Customer): boolean {
    const user = this.currentUser();
    return user ? this.customerService.canDeleteCustomer(customer, user) : false;
  }

  getCustomerTypeLabel(type: string): string {
    return this.customerService.getCustomerTypeLabel(type);
  }

  formatCreditLimit(amount: number): string {
    return this.customerService.formatCreditLimit(amount);
  }

  getCustomerStatusClass(customer: Customer): string {
    if (!customer.is_active) return 'bg-gray-100 text-gray-800';
    return customer.is_active_customer ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
  }

  getCustomerStatusText(customer: Customer): string {
    if (!customer.is_active) return 'Inactivo';
    return customer.is_active_customer ? 'Activo' : 'Desactivado';
  }
}
