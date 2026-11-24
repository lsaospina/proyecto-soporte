import type { BadgeVariant } from '../../../components/shared/StatusBadge';
import { aISO, formatearFecha } from '../../../lib/format';
import type { EstadoRenovacion, Periodicidad } from '../types';

export const OPCIONES_PERIODICIDAD: Array<{ value: Periodicidad; label: string }> = [
  { value: 'MENSUAL', label: 'Mensual' },
  { value: 'TRIMESTRAL', label: 'Trimestral' },
  { value: 'SEMESTRAL', label: 'Semestral' },
  { value: 'ANUAL', label: 'Anual' },
  { value: 'BIENAL', label: 'Bienal' },
];

export const ETIQUETA_PERIODICIDAD: Record<Periodicidad, string> = {
  MENSUAL: 'Mensual',
  TRIMESTRAL: 'Trimestral',
  SEMESTRAL: 'Semestral',
  ANUAL: 'Anual',
  BIENAL: 'Bienal',
};

export const ETIQUETA_ESTADO: Record<EstadoRenovacion, string> = {
  VIGENTE: 'Vigente',
  POR_VENCER: 'Por vencer',
  VENCIDA: 'Vencida',
  INACTIVA: 'Inactiva',
};

export const VARIANTE_ESTADO: Record<EstadoRenovacion, BadgeVariant> = {
  VIGENTE: 'success',
  POR_VENCER: 'warning',
  VENCIDA: 'danger',
  INACTIVA: 'neutral',
};

const MESES_POR_PERIODICIDAD: Record<Periodicidad, number> = {
  MENSUAL: 1,
  TRIMESTRAL: 3,
  SEMESTRAL: 6,
  ANUAL: 12,
  BIENAL: 24,
};

export function sumarMeses(fechaISO: string, meses: number): string {
  const fecha = new Date(`${fechaISO.slice(0, 10)}T00:00:00`);
  if (Number.isNaN(fecha.getTime())) return fechaISO;
  const dia = fecha.getDate();
  fecha.setDate(1);
  fecha.setMonth(fecha.getMonth() + meses);
  const ultimoDia = new Date(fecha.getFullYear(), fecha.getMonth() + 1, 0).getDate();
  fecha.setDate(Math.min(dia, ultimoDia));
  return aISO(fecha);
}

export function siguienteRenovacion(fechaISO: string, periodicidad: Periodicidad): string {
  return sumarMeses(fechaISO, MESES_POR_PERIODICIDAD[periodicidad]);
}

export function renovacionSugerida(fechaISO: string, periodicidad: Periodicidad): string {
  const hoy = aISO(new Date());
  const base = fechaISO < hoy ? hoy : fechaISO;
  return siguienteRenovacion(base, periodicidad);
}

export function textoDias(dias: number): string {
  if (dias < 0) {
    const atraso = Math.abs(dias);
    return `Vencida hace ${atraso} día${atraso === 1 ? '' : 's'}`;
  }
  if (dias === 0) return 'Vence hoy';
  return `En ${dias} día${dias === 1 ? '' : 's'}`;
}

export function fechaRenovacion(fechaISO: string, dias: number): string {
  return `${formatearFecha(fechaISO)} · ${textoDias(dias)}`;
}
