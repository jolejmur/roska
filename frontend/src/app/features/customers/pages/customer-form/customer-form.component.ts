import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { CustomerService } from '../../../../core/services/customer.service';
import { AuthService } from '../../../../core/services/auth.service';
import { Customer, CustomerCreate, CustomerUpdate } from '../../../../core/models/customer.model';
import { ButtonComponent } from '../../../../shared/components/button/button.component';

@Component({
  selector: 'app-customer-form',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink, ButtonComponent],
  templateUrl: './customer-form.component.html',
  styleUrls: ['./customer-form.component.scss']
})
export class CustomerFormComponent implements OnInit {
  private readonly customerService = inject(CustomerService);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);

  // Signals
  loading = signal(false);
  saving = signal(false);
  isEditMode = signal(false);
  customerId = signal<number | null>(null);
  currentUser = this.authService.currentUser;

  // Form data
  customerForm: any = {
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
    customer_type: 'INDIVIDUAL',
    tax_id: '',
    company_name: '',
    contact_person: '',
    credit_limit: 0,
    payment_terms: 30,
    discount_percentage: 0,
    notes: '',
    is_active_customer: true,
    is_active: true
  };

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id && id !== 'new') {
      this.isEditMode.set(true);
      this.customerId.set(+id);
      this.loadCustomer(+id);
    }
  }

  loadCustomer(id: number): void {
    this.loading.set(true);
    this.customerService.getCustomer(id).subscribe({
      next: (customer) => {
        this.populateForm(customer);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading customer:', err);
        alert('Error al cargar el cliente');
        this.router.navigate(['/customers']);
      }
    });
  }

  populateForm(customer: Customer): void {
    this.customerForm = {
      email: customer.email,
      username: customer.username,
      first_name: customer.first_name || '',
      last_name: customer.last_name || '',
      ci: customer.ci || '',
      phone: customer.phone || '',
      address: customer.address || '',
      city: customer.city || '',
      country: customer.country || 'Bolivia',
      birth_date: customer.birth_date || '',
      customer_type: customer.customer_type || 'INDIVIDUAL',
      tax_id: customer.tax_id || '',
      company_name: customer.company_name || '',
      contact_person: customer.contact_person || '',
      credit_limit: customer.credit_limit || 0,
      payment_terms: customer.payment_terms || 30,
      discount_percentage: customer.discount_percentage || 0,
      notes: customer.notes || '',
      is_active_customer: customer.is_active_customer,
      is_active: customer.is_active
    };
  }

  onSubmit(): void {
    if (!this.validateForm()) {
      return;
    }

    this.saving.set(true);

    if (this.isEditMode()) {
      this.updateCustomer();
    } else {
      this.createCustomer();
    }
  }

  validateForm(): boolean {
    // Required fields for creation
    if (!this.isEditMode()) {
      if (!this.customerForm.email || !this.customerForm.username || !this.customerForm.password) {
        alert('Por favor complete los campos requeridos: Email, Username y Password');
        return false;
      }

      if (this.customerForm.password.length < 8) {
        alert('La contraseña debe tener al menos 8 caracteres');
        return false;
      }
    }

    // Validate business customers
    if (this.customerForm.customer_type === 'BUSINESS' && !this.customerForm.company_name) {
      alert('Por favor ingrese el nombre de la empresa para clientes tipo Empresa');
      return false;
    }

    // Validate numeric fields
    if (this.customerForm.credit_limit < 0) {
      alert('El límite de crédito no puede ser negativo');
      return false;
    }

    if (this.customerForm.discount_percentage < 0 || this.customerForm.discount_percentage > 100) {
      alert('El porcentaje de descuento debe estar entre 0 y 100');
      return false;
    }

    return true;
  }

  createCustomer(): void {
    const customerData: CustomerCreate = {
      email: this.customerForm.email,
      username: this.customerForm.username,
      password: this.customerForm.password,
      first_name: this.customerForm.first_name,
      last_name: this.customerForm.last_name,
      customer_type: this.customerForm.customer_type,
      ci: this.customerForm.ci || undefined,
      phone: this.customerForm.phone || undefined,
      address: this.customerForm.address || undefined,
      city: this.customerForm.city || undefined,
      country: this.customerForm.country || undefined,
      birth_date: this.customerForm.birth_date || undefined,
      tax_id: this.customerForm.tax_id || undefined,
      company_name: this.customerForm.company_name || undefined,
      contact_person: this.customerForm.contact_person || undefined,
      credit_limit: this.customerForm.credit_limit,
      payment_terms: this.customerForm.payment_terms,
      discount_percentage: this.customerForm.discount_percentage,
      notes: this.customerForm.notes || undefined,
      is_active_customer: this.customerForm.is_active_customer
    };

    this.customerService.createCustomer(customerData).subscribe({
      next: (customer) => {
        this.saving.set(false);
        alert('Cliente creado exitosamente');
        this.router.navigate(['/customers', customer.id]);
      },
      error: (err) => {
        console.error('Error creating customer:', err);
        this.saving.set(false);
        const errorMsg = err.error?.detail || err.error?.email?.[0] || 'Error al crear el cliente';
        alert(errorMsg);
      }
    });
  }

  updateCustomer(): void {
    if (!this.customerId()) return;

    const customerData: CustomerUpdate = {
      first_name: this.customerForm.first_name,
      last_name: this.customerForm.last_name,
      ci: this.customerForm.ci || undefined,
      phone: this.customerForm.phone || undefined,
      address: this.customerForm.address || undefined,
      city: this.customerForm.city || undefined,
      country: this.customerForm.country || undefined,
      birth_date: this.customerForm.birth_date || undefined,
      customer_type: this.customerForm.customer_type,
      tax_id: this.customerForm.tax_id || undefined,
      company_name: this.customerForm.company_name || undefined,
      contact_person: this.customerForm.contact_person || undefined,
      credit_limit: this.customerForm.credit_limit,
      payment_terms: this.customerForm.payment_terms,
      discount_percentage: this.customerForm.discount_percentage,
      notes: this.customerForm.notes || undefined,
      is_active_customer: this.customerForm.is_active_customer,
      is_active: this.customerForm.is_active
    };

    this.customerService.updateCustomer(this.customerId()!, customerData).subscribe({
      next: (customer) => {
        this.saving.set(false);
        alert('Cliente actualizado exitosamente');
        this.router.navigate(['/customers', customer.id]);
      },
      error: (err) => {
        console.error('Error updating customer:', err);
        this.saving.set(false);
        const errorMsg = err.error?.detail || 'Error al actualizar el cliente';
        alert(errorMsg);
      }
    });
  }

  onCancel(): void {
    if (this.isEditMode() && this.customerId()) {
      this.router.navigate(['/customers', this.customerId()]);
    } else {
      this.router.navigate(['/customers']);
    }
  }

  get isBusinessCustomer(): boolean {
    return this.customerForm.customer_type === 'BUSINESS';
  }
}
