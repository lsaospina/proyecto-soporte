export const MESES = [
  'Enero',
  'Febrero',
  'Marzo',
  'Abril',
  'Mayo',
  'Junio',
  'Julio',
  'Agosto',
  'Septiembre',
  'Octubre',
  'Noviembre',
  'Diciembre',
];

export const DIAS_SEMANA = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

export function formatFecha(iso: string | null | undefined): string {
  if (!iso) return '';
  const [anio, mes, dia] = iso.slice(0, 10).split('-');
  return `${dia}/${mes}/${anio}`;
}

export function isoHoyLocal(): string {
  const d = new Date();
  const mes = String(d.getMonth() + 1).padStart(2, '0');
  const dia = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${mes}-${dia}`;
}

export interface CeldaCalendario {
  fecha: string;
  dia: number;
  enMes: boolean;
}

export function construirMes(anio: number, mes: number): CeldaCalendario[] {
  const primerDia = new Date(anio, mes - 1, 1);
  const desplazamiento = (primerDia.getDay() + 6) % 7;
  const inicio = new Date(anio, mes - 1, 1 - desplazamiento);
  const celdas: CeldaCalendario[] = [];
  for (let i = 0; i < 42; i += 1) {
    const fecha = new Date(inicio.getFullYear(), inicio.getMonth(), inicio.getDate() + i);
    const iso = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}-${String(
      fecha.getDate(),
    ).padStart(2, '0')}`;
    celdas.push({ fecha: iso, dia: fecha.getDate(), enMes: fecha.getMonth() === mes - 1 });
  }
  return celdas;
}
