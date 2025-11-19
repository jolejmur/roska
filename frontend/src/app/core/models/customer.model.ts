export interface CustomerRole {
  id: number;
  name: string;
  code: string;
  assignment_id: number;
}

export interface Customer {
  id: number;
  customer_code: string;
  customer_type: 'INDIVIDUAL' | 'BUSINESS';
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  display_name: string;
  is_active: boolean;
  is_active_customer: boolean;
  ci?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  birth_date?: string;
  profile_picture?: string;
  profile_picture_url?: string;

  // Customer specific fields
  tax_id?: string;
  company_name?: string;
  contact_person?: string;
  credit_limit: number;
  payment_terms: number;
  discount_percentage: number;
  notes?: string;
  has_credit_available: boolean;

  // Timestamps
  created_at?: string;
  updated_at?: string;
  last_login?: string;
  date_joined?: string;

  // Relations
  roles?: CustomerRole[];
}

export interface CustomerCreate {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
  customer_type: 'INDIVIDUAL' | 'BUSINESS';

  // Optional personal info
  ci?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  birth_date?: string;

  // Optional customer info
  tax_id?: string;
  company_name?: string;
  contact_person?: string;
  credit_limit?: number;
  payment_terms?: number;
  discount_percentage?: number;
  notes?: string;
  is_active_customer?: boolean;
}

export interface CustomerUpdate {
  first_name?: string;
  last_name?: string;
  ci?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  birth_date?: string;
  customer_type?: 'INDIVIDUAL' | 'BUSINESS';
  tax_id?: string;
  company_name?: string;
  contact_person?: string;
  credit_limit?: number;
  payment_terms?: number;
  discount_percentage?: number;
  notes?: string;
  is_active_customer?: boolean;
  is_active?: boolean;
}

export interface CustomerProfileUpdate {
  first_name?: string;
  last_name?: string;
  ci?: string;
  phone?: string;
  profile_picture?: File;
  address?: string;
  city?: string;
  country?: string;
  birth_date?: string;
  contact_person?: string;
}
