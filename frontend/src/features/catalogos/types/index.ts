export type CatalogoResource = 'sedes' | 'ubicaciones' | 'categorias' | 'marcas' | 'modelos';

export interface Sede { id: number; nombre: string; direccion: string; is_active: boolean; created_at: string; updated_at: string; }
export interface Ubicacion { id: number; sede: number; sede_nombre: string; nombre: string; is_active: boolean; created_at: string; updated_at: string; }
export interface Categoria { id: number; nombre: string; descripcion: string; is_active: boolean; created_at: string; updated_at: string; }
export interface Marca { id: number; nombre: string; is_active: boolean; created_at: string; updated_at: string; }
export interface ModeloActivo { id: number; marca: number; marca_nombre: string; categoria: number; categoria_nombre: string; nombre: string; is_active: boolean; created_at: string; updated_at: string; }

export type CatalogoItem = Sede | Ubicacion | Categoria | Marca | ModeloActivo;

export interface Paginated<T> { count: number; next: string | null; previous: string | null; results: T[]; }
