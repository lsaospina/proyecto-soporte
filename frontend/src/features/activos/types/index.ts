export interface Activo {
  id: number;
  serial: string;
  modelo: number;
  modelo_nombre: string;
  marcaNombre: string;
  categoriaNombre: string;
  fecha_adquisicion: string;
  valor_adquisicion: string | null;
  estado: string;
  codigo_qr: string;
  procesador: string;
  ram_gb: number | null;
  almacenamiento_gb: number | null;
  direccion_mac: string;
  observaciones: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Paginated<T> { count: number; next: string | null; previous: string | null; results: T[]; }

export interface HistorialEntry {
  fecha: string;
  usuario: string | null;
  tipo: string;
  campos: string[];
}