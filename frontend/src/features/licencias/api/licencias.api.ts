import client from '../../../api/client';
import type {
  Licencia,
  LicenciaPayload,
  Paginated,
  ProveedorOpcion,
  RenovarPayload,
  ResumenLicencias,
} from '../types';

const BASE = '/api/v1/licencias';

export const licenciasApi = {
  list: (params?: Record<string, unknown>) =>
    client.get<Paginated<Licencia>>(`${BASE}/`, { params }).then((r) => r.data),
  retrieve: (id: number) => client.get<Licencia>(`${BASE}/${id}/`).then((r) => r.data),
  resumen: () => client.get<ResumenLicencias>(`${BASE}/resumen/`).then((r) => r.data),
  proveedores: () =>
    client.get<ProveedorOpcion[]>(`${BASE}/proveedores/`).then((r) => r.data),
  crear: (data: LicenciaPayload) =>
    client.post<Licencia>(`${BASE}/`, data).then((r) => r.data),
  actualizar: (id: number, data: Partial<LicenciaPayload>) =>
    client.patch<Licencia>(`${BASE}/${id}/`, data).then((r) => r.data),
  renovar: (id: number, data: RenovarPayload) =>
    client.post<Licencia>(`${BASE}/${id}/renovar/`, data).then((r) => r.data),
  inactivar: (id: number) =>
    client.post<Licencia>(`${BASE}/${id}/inactivar/`).then((r) => r.data),
  reactivar: (id: number) =>
    client.post<Licencia>(`${BASE}/${id}/reactivar/`).then((r) => r.data),
};
