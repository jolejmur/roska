export interface UserRole {
  id: number;
  name: string;
  code: string;
  assignment_id: number;
}

export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  is_staff: boolean;
  ci?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  birth_date?: string;
  user_type?: 'EMPLOYEE' | 'CUSTOMER' | 'SUPPLIER' | 'OTHER';
  profile_picture?: string;
  date_joined?: string;
  last_login?: string;
  roles?: UserRole[];
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  first_name: string;
  last_name: string;
  ci?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  birth_date?: string;
  user_type?: string;
  is_active?: boolean;
  is_staff?: boolean;
  role_ids?: number[];
}

export interface UserUpdate {
  first_name?: string;
  last_name?: string;
  ci?: string;
  phone?: string;
  address?: string;
  city?: string;
  country?: string;
  birth_date?: string;
  user_type?: string;
  is_active?: boolean;
  is_staff?: boolean;
  role_ids?: number[];
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  token_type: string;
  user: User;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}
