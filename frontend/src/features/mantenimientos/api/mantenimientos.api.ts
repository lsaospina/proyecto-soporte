import client from '../../../api/client';

const BASE = '/api/v1/mantenimientos';

export interface DatosProgramar {
  activo: number;
  fecha_programada: string;
  observacion?: string;
}

export interface DatosCompletar {
  fecha_realizacion: string;
  tecnico: number;
  costo: string;
  observacion?: string;
}

export interface DatosCorrectivo {
  activo: number;
  fecha_programada: string;
  fecha_seguimiento: string;
  observacion: string;
  tecnico?: number;
}

export const mantenimientosApi = {
  resumen: (anio?: number) =>
    client.get(`${BASE}/resumen/`, { params: anio ? { anio } : {} }).then((r) => r.data),
  calendario: (anio: number, mes: number) =>
    client.get(`${BASE}/calendario/`, { params: { anio, mes } }).then((r) => r.data),
  list: (params?: Record<string, unknown>) =>
    client.get(`${BASE}/`, { params }).then((r) => r.data),
  retrieve: (id: number) => client.get(`${BASE}/${id}/`).then((r) => r.data),
  tecnicos: () => client.get(`${BASE}/tecnicos/`).then((r) => r.data),
  historial: (id: number) => client.get(`${BASE}/${id}/historial/`).then((r) => r.data),
  crear: (data: DatosProgramar) => client.post(`${BASE}/`, data).then((r) => r.data),
  crearCorrectivo: (data: DatosCorrectivo) =>
    client.post(`${BASE}/correctivos/`, data).then((r) => r.data),
  completar: (id: number, data: DatosCompletar) =>
    client.post(`${BASE}/${id}/completar/`, data).then((r) => r.data),
  reprogramar: (id: number, fecha_programada: string) =>
    client
      .post(`${BASE}/${id}/reprogramar/`, { fecha_programada })
      .then((r) => ({ data: r.data, status: r.status })),
  cancelar: (id: number, motivo: string) =>
    client.post(`${BASE}/${id}/cancelar/`, { motivo }).then((r) => r.data),
};
