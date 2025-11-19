export interface MenuItem {
  id: string;
  label: string;
  icon: string;
  route?: string;
  permission?: string; // Nombre del permiso de Cerbos (ej: 'users.list')
  children?: MenuItem[];
  expanded?: boolean;
  is_category?: boolean; // Si es una categoría (colapsable)
  color?: string; // Color de la categoría (hex)
}

export interface UserPermissions {
  user_id: number;
  email: string;
  is_superuser: boolean;
  permissions: {
    users: {
      create: boolean;
      read: boolean;
      update: boolean;
      delete: boolean;
      list: boolean;
    };
  };
}
