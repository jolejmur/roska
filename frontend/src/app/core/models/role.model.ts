export interface Role {
  id: number;
  name: string;
  code: string;
  description: string;
  cerbos_role: string;
  is_active: boolean;
  is_system: boolean;
  level: number;
  created_at: string;
  updated_at: string;
  created_by?: number;
  created_by_name?: string;
  users_count?: number;
  functions_count?: number;
  functions?: Function[];
}

export interface RoleCreate {
  name: string;
  code: string;
  description: string;
  cerbos_role: string;
  is_active?: boolean;
  level?: number;
  function_ids?: number[];
}

export interface RoleUpdate {
  name?: string;
  description?: string;
  is_active?: boolean;
  level?: number;
  function_ids?: number[];
}

export interface RoleAssignment {
  id: number;
  user: number;
  role: number;
  role_name?: string;
  assigned_at: string;
  assigned_by?: number;
  expires_at?: string;
  scope_type?: string;
  scope_id?: number;
  is_active: boolean;
}

export interface RoleAssignmentCreate {
  user: number;
  role: number;
  expires_at?: string;
  scope_type?: string;
  scope_id?: number;
}

export interface Category {
  id: number;
  name: string;
  code: string;
  description?: string;
  icon: string;
  color?: string;
  order: number;
  is_active: boolean;
  is_system: boolean;
  active_functions_count?: number;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  name: string;
  code: string;
  description?: string;
  icon: string;
  color?: string;
  order?: number;
  is_active?: boolean;
}

export interface CategoryUpdate {
  name?: string;
  description?: string;
  icon?: string;
  color?: string;
  order?: number;
  is_active?: boolean;
}

export interface Function {
  id: number;
  name: string;
  code: string;
  url: string | null;
  icon: string;
  category?: number;
  category_name?: string;
  category_code?: string;
  cerbos_resource?: string;
  parent?: number;
  parent_name?: string;
  order: number;
  is_active: boolean;
  is_system: boolean;
  children?: Function[];
  created_at: string;
  updated_at: string;
}

export interface FunctionCreate {
  name: string;
  code: string;
  url?: string;
  icon: string;
  category?: number;
  cerbos_resource?: string;
  parent?: number;
  order?: number;
  is_active?: boolean;
}

export interface FunctionUpdate {
  name?: string;
  category?: number;
  order?: number;
  is_active?: boolean;
}
