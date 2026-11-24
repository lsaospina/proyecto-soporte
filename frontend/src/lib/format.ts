const formateadorCOP = new Intl.NumberFormat('es-CO', {
  style: 'currency',
  currency: 'COP',
  maximumFractionDigits: 0,
});

export function formatearMoneda(valor: string | number | null | undefined): string {
  if (valor === null || valor === undefined || valor === '') return '—';
  const numero = typeof valor === 'string' ? Number(valor) : valor;
  if (!Number.isFinite(numero)) return '—';
  return formateadorCOP.format(numero);
}

export function formatearFecha(iso: string | null | undefined): string {
  if (!iso) return '—';
  const [anio, mes, dia] = iso.slice(0, 10).split('-');
  if (!anio || !mes || !dia) return iso;
  return `${dia}/${mes}/${anio}`;
}

export function diaYMes(iso: string): { dia: string; mes: string } {
  const fecha = new Date(`${iso.slice(0, 10)}T00:00:00`);
  if (Number.isNaN(fecha.getTime())) return { dia: '--', mes: '---' };
  const dia = fecha.getDate().toString().padStart(2, '0');
  const mes = fecha.toLocaleDateString('es-CO', { month: 'short' }).replace('.', '');
  return { dia, mes };
}

export function formatearPorcentaje(valor: number): string {
  return `${valor}%`;
}

export function aISO(fecha: Date): string {
  const anio = fecha.getFullYear();
  const mes = (fecha.getMonth() + 1).toString().padStart(2, '0');
  const dia = fecha.getDate().toString().padStart(2, '0');
  return `${anio}-${mes}-${dia}`;
}
