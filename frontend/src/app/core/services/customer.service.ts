import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Customer, CustomerCreate, CustomerUpdate } from '../models/customer.model';

interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

interface CustomerFilters {
  search?: string;
  is_active?: boolean;
  is_active_customer?: boolean;
  customer_type?: 'INDIVIDUAL' | 'BUSINESS';
  page?: number;
  page_size?: number;
}

@Injectable({
  providedIn: 'root'
})
export class CustomerService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${environment.apiUrl}/customers`;

  /**
   * Get list of customers with optional filters
   */
  getCustomers(filters?: CustomerFilters): Observable<PaginatedResponse<Customer>> {
    let params = new HttpParams();

    if (filters) {
      if (filters.search) params = params.set('search', filters.search);
      if (filters.is_active !== undefined) params = params.set('is_active', filters.is_active);
      if (filters.is_active_customer !== undefined) params = params.set('is_active_customer', filters.is_active_customer);
      if (filters.customer_type) params = params.set('customer_type', filters.customer_type);
      if (filters.page) params = params.set('page', filters.page);
      if (filters.page_size) params = params.set('page_size', filters.page_size);
    }

    return this.http.get<PaginatedResponse<Customer>>(this.apiUrl + '/', { params });
  }

  /**
   * Get a single customer by ID
   */
  getCustomer(id: number): Observable<Customer> {
    return this.http.get<Customer>(`${this.apiUrl}/${id}/`);
  }

  /**
   * Get current customer profile (for customer users)
   */
  getMyProfile(): Observable<Customer> {
    return this.http.get<Customer>(`${this.apiUrl}/me/`);
  }

  /**
   * Get current customer permissions
   */
  getMyPermissions(): Observable<any> {
    return this.http.get(`${this.apiUrl}/me/permissions/`);
  }

  /**
   * Create a new customer (admin/staff only)
   */
  createCustomer(customer: CustomerCreate): Observable<Customer> {
    return this.http.post<Customer>(this.apiUrl + '/', customer);
  }

  /**
   * Update customer (full update)
   */
  updateCustomer(id: number, customer: CustomerUpdate): Observable<Customer> {
    return this.http.put<Customer>(`${this.apiUrl}/${id}/`, customer);
  }

  /**
   * Partial update customer
   */
  patchCustomer(id: number, customer: Partial<CustomerUpdate>): Observable<Customer> {
    return this.http.patch<Customer>(`${this.apiUrl}/${id}/`, customer);
  }

  /**
   * Update current customer profile
   */
  updateMyProfile(customer: Partial<CustomerUpdate>): Observable<Customer> {
    return this.http.patch<Customer>(`${this.apiUrl}/me/update/`, customer);
  }

  /**
   * Delete customer (admin/staff only)
   */
  deleteCustomer(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }

  /**
   * Toggle customer active status
   */
  toggleCustomerStatus(id: number, is_active_customer: boolean): Observable<Customer> {
    return this.http.patch<Customer>(`${this.apiUrl}/${id}/`, { is_active_customer });
  }

  /**
   * Check if customer can be edited
   */
  canEditCustomer(currentUser: any): boolean {
    // Admin or staff can edit customers
    return currentUser.is_staff || currentUser.is_superuser;
  }

  /**
   * Check if customer can be deleted
   */
  canDeleteCustomer(customer: Customer, currentUser: any): boolean {
    // Cannot delete yourself
    if (customer.id === currentUser.id) {
      return false;
    }

    // Only admin/staff can delete
    return currentUser.is_staff || currentUser.is_superuser;
  }

  /**
   * Get customer type label
   */
  getCustomerTypeLabel(type: string): string {
    const labels: { [key: string]: string } = {
      'INDIVIDUAL': 'Persona Natural',
      'BUSINESS': 'Empresa'
    };
    return labels[type] || type;
  }

  /**
   * Format credit limit for display
   */
  formatCreditLimit(amount: number): string {
    return new Intl.NumberFormat('es-BO', {
      style: 'currency',
      currency: 'BOB'
    }).format(amount);
  }
}
