import { useMemo, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Lock } from 'lucide-react';

import { ConfirmDialog } from '../../../components/shared/ConfirmDialog';
import { DataTable, type DataTableColumn } from '../../../components/shared/DataTable';
import { FormField } from '../../../components/shared/FormField';
import { FormSection } from '../../../components/shared/FormSection';
import { PageHeader } from '../../../components/shared/PageHeader';
import { StatusBadge, type BadgeVariant } from '../../../components/shared/StatusBadge';
import { activosApi } from '../../activos/api/activos.api';
import { useAuth } from '../../auth/hooks/useAuth';
import { mantenimientosApi } from '../api/mantenimientos.api';
import {
  cancelarSchema,
  completarSchema,
  correctivoSchema,
  programarSchema,
  reprogramarSchema,
  type CancelarFormData,
  type CompletarFormData,
  type CorrectivoFormData,
  type ProgramarFormData,
  type ReprogramarFormData,
} from '../schemas/mantenimiento.schema';
import type {
  CalendarioMensual,
  HistorialMantenimiento,
  Mantenimiento,
  Paginated,
  ResumenAnual,
  Situacion,
} from '../types';
import { DIAS_SEMANA, MESES, construirMes, formatFecha } from '../utils/fechas';

const VARIANTE: Record<Situacion, BadgeVariant> = {
  PENDIENTE: 'info',
  COMPLETADO: 'success',
  VENCIDO: 'warning',
  INCUMPLIDO: 'danger',
  CANCELADO: 'neutral',
};

const ETIQUETA: Record<Situacion, string> = {
  PENDIENTE: 'Pendiente',
  COMPLETADO: 'Completado',
  VENCIDO: 'Vencido',
  INCUMPLIDO: 'Incumplido',
  CANCELADO: 'Cancelado',
};

interface Tecnico {
  id: number;
  nombre_completo: string;
  email?: string;
}

type Dialogo = 'programar' | 'completar' | 'reprogramar' | 'cancelar' | 'correctivo' | null;

function Chip({ mantenimiento, onClick }: { mantenimiento: Mantenimiento; onClick: () => void }) {
  const variante = VARIANTE[mantenimiento.situacion];
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={`${mantenimiento.activo_codigo} ${ETIQUETA[mantenimiento.situacion]}`}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 4,
        width: '100%',
        padding: '2px 6px',
        marginBottom: 2,
        fontSize: 11,
        textAlign: 'left',
        borderRadius: 4,
        border: 'none',
        cursor: 'pointer',
        color: `var(--${variante === 'neutral' ? 'neutral' : variante}-fg)`,
        backgroundColor: `var(--${variante === 'neutral' ? 'neutral' : variante}-bg)`,
      }}
    >
      {mantenimiento.situacion === 'INCUMPLIDO' && <Lock size={10} aria-hidden />}
      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {mantenimiento.activo_codigo}
      </span>
      <span style={{ marginLeft: 'auto', fontSize: 10 }}>
        {mantenimiento.situacion === 'INCUMPLIDO' ? 'Evidencia' : ETIQUETA[mantenimiento.situacion]}
      </span>
    </button>
  );
}

function mapearErrores(e: any, setError: (name: any, error: any) => void): boolean {
  const errores = e?.response?.data?.errors as Array<{ field: string; message: string }> | undefined;
  let aplicado = false;
  (errores ?? []).forEach((item) => {
    if (item.field && item.field !== 'general') {
      setError(item.field, { type: 'server', message: item.message });
      aplicado = true;
    }
  });
  return aplicado;
}

function ProgramarDialog({
  fecha,
  onClose,
  onDone,
}: {
  fecha: string;
  onClose: () => void;
  onDone: (mensaje: string) => void;
}) {
  const [busqueda, setBusqueda] = useState('');
  const [serverError, setServerError] = useState('');
  const { register, handleSubmit, formState: { errors }, setError } = useForm<ProgramarFormData>({
    resolver: zodResolver(programarSchema),
    defaultValues: { activo: 0, fecha_programada: fecha, observacion: '' },
  });
  const activosQ = useQuery({
    queryKey: ['activos-opciones', busqueda],
    queryFn: () =>
      activosApi.list({
        page_size: 100,
        is_active: true,
        estado_no: 'DADO_DE_BAJA',
        ...(busqueda.trim() ? { search: busqueda.trim() } : {}),
      }),
  });
  const resultados: any[] = activosQ.data?.results ?? [];

  const enviar = async (data: ProgramarFormData) => {
    setServerError('');
    try {
      await mantenimientosApi.crear(data);
      onDone('Mantenimiento programado.');
    } catch (e: any) {
      if (!mapearErrores(e, setError)) {
        setServerError(e?.response?.data?.detail || 'No se pudo programar el mantenimiento.');
      }
    }
  };

  return (
    <ConfirmDialog
      open
      title="Programar mantenimiento"
      confirmLabel="Programar"
      onCancel={onClose}
      onConfirm={handleSubmit(enviar)}
    >
      <FormField
        label="Equipos (se muestran todos los activos; filtre si lo necesita)"
        htmlFor="buscar_activo"
      >
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            id="buscar_activo"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Filtrar por serial, código, marca o modelo"
            style={{ flex: 1, padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
          />
          <button
            type="button"
            onClick={() => setBusqueda('')}
            style={{ padding: '8px 12px', border: '1px solid var(--border)', background: 'var(--surface-lowest)', borderRadius: 6, cursor: 'pointer' }}
          >
            Ver todos
          </button>
        </div>
      </FormField>
      <FormField label="Equipo" htmlFor="activo" required error={errors.activo?.message}>
        <select
          id="activo"
          {...register('activo', { valueAsNumber: true })}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        >
          <option value={0}>
            {activosQ.isLoading ? 'Cargando equipos…' : '-- Selecciona --'}
          </option>
          {resultados.map((a) => (
            <option key={a.id} value={a.id}>
              {a.codigo_qr} · {a.serial}
              {a.marca_nombre ? ` · ${a.marca_nombre} / ${a.modelo_nombre}` : ''}
            </option>
          ))}
        </select>
      </FormField>
      <FormField label="Fecha programada" htmlFor="fecha_programada" required error={errors.fecha_programada?.message}>
        <input
          id="fecha_programada"
          type="date"
          {...register('fecha_programada')}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        />
      </FormField>
      <FormField label="Observación" htmlFor="observacion">
        <textarea
          id="observacion"
          {...register('observacion')}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        />
      </FormField>
      {serverError && <div role="alert" style={{ color: 'var(--danger-fg)' }}>{serverError}</div>}
    </ConfirmDialog>
  );
}

function CorrectivoDialog({
  hoy,
  tecnicos,
  onClose,
  onDone,
}: {
  hoy: string;
  tecnicos: Tecnico[];
  onClose: () => void;
  onDone: (mensaje: string) => void;
}) {
  const { user } = useAuth();
  const [busqueda, setBusqueda] = useState('');
  const [serverError, setServerError] = useState('');
  const { register, handleSubmit, formState: { errors }, setError } = useForm<CorrectivoFormData>({
    resolver: zodResolver(correctivoSchema),
    defaultValues: {
      activo: 0,
      observacion: '',
      fecha_programada: hoy,
      fecha_seguimiento: hoy,
      tecnico: user?.id ?? 0,
    },
  });
  const activosQ = useQuery({
    queryKey: ['activos-opciones-correctivo', busqueda],
    queryFn: () =>
      activosApi.list({
        page_size: 100,
        is_active: true,
        estado_no: 'DADO_DE_BAJA',
        ...(busqueda.trim() ? { search: busqueda.trim() } : {}),
      }),
  });
  const resultados: any[] = activosQ.data?.results ?? [];

  const enviar = async (data: CorrectivoFormData) => {
    setServerError('');
    try {
      await mantenimientosApi.crearCorrectivo({
        activo: data.activo,
        observacion: data.observacion,
        fecha_programada: data.fecha_programada,
        fecha_seguimiento: data.fecha_seguimiento,
        tecnico: data.tecnico || undefined,
      });
      onDone('Correctivo registrado.');
    } catch (e: any) {
      if (!mapearErrores(e, setError)) {
        setServerError(e?.response?.data?.detail || 'No se pudo registrar el correctivo.');
      }
    }
  };

  return (
    <ConfirmDialog
      open
      title="Registrar correctivo"
      confirmLabel="Registrar"
      onCancel={onClose}
      onConfirm={handleSubmit(enviar)}
    >
      <FormField
        label="Equipos (se muestran todos los activos; filtre si lo necesita)"
        htmlFor="buscar_activo_correctivo"
      >
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            id="buscar_activo_correctivo"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            placeholder="Filtrar por serial, código, marca o modelo"
            style={{ flex: 1, padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
          />
          <button
            type="button"
            onClick={() => setBusqueda('')}
            style={{ padding: '8px 12px', border: '1px solid var(--border)', background: 'var(--surface-lowest)', borderRadius: 6, cursor: 'pointer' }}
          >
            Ver todos
          </button>
        </div>
      </FormField>
      <FormField label="Equipo" htmlFor="activo_correctivo" required error={errors.activo?.message}>
        <select
          id="activo_correctivo"
          {...register('activo', { valueAsNumber: true })}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        >
          <option value={0}>
            {activosQ.isLoading ? 'Cargando equipos…' : '-- Selecciona --'}
          </option>
          {resultados.map((a) => (
            <option key={a.id} value={a.id}>
              {a.codigo_qr} · {a.serial}
              {a.marca_nombre ? ` · ${a.marca_nombre} / ${a.modelo_nombre}` : ''}
            </option>
          ))}
        </select>
      </FormField>
      <FormField label="¿Qué pasó?" htmlFor="descripcion_correctivo" required error={errors.observacion?.message}>
        <textarea
          id="descripcion_correctivo"
          {...register('observacion')}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        />
      </FormField>
      <FormField label="Fecha del evento" htmlFor="fecha_evento" required error={errors.fecha_programada?.message}>
        <input
          id="fecha_evento"
          type="date"
          max={hoy}
          {...register('fecha_programada')}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        />
      </FormField>
      <FormField label="Fecha de seguimiento" htmlFor="fecha_seguimiento" required error={errors.fecha_seguimiento?.message}>
        <input
          id="fecha_seguimiento"
          type="date"
          {...register('fecha_seguimiento')}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        />
      </FormField>
      <FormField label="Técnico" htmlFor="tecnico_correctivo">
        <select
          id="tecnico_correctivo"
          {...register('tecnico', { valueAsNumber: true })}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        >
          <option value={0}>-- Sin asignar --</option>
          {tecnicos.map((t) => (
            <option key={t.id} value={t.id}>
              {t.nombre_completo}
            </option>
          ))}
        </select>
      </FormField>
      {serverError && <div role="alert" style={{ color: 'var(--danger-fg)' }}>{serverError}</div>}
    </ConfirmDialog>
  );
}

function CompletarDialog({
  mantenimiento,
  hoy,
  tecnicos,
  onClose,
  onDone,
}: {
  mantenimiento: Mantenimiento;
  hoy: string;
  tecnicos: Tecnico[];
  onClose: () => void;
  onDone: (mensaje: string) => void;
}) {
  const { user } = useAuth();
  const [serverError, setServerError] = useState('');
  const { register, handleSubmit, formState: { errors }, setError } = useForm<CompletarFormData>({
    resolver: zodResolver(completarSchema),
    defaultValues: {
      fecha_realizacion: hoy,
      tecnico: user?.id ?? 0,
      costo: '',
      observacion: '',
    },
  });

  const enviar = async (data: CompletarFormData) => {
    setServerError('');
    try {
      await mantenimientosApi.completar(mantenimiento.id, data);
      onDone('Mantenimiento completado.');
    } catch (e: any) {
      if (!mapearErrores(e, setError)) {
        setServerError(e?.response?.data?.detail || 'No se pudo completar el mantenimiento.');
      }
    }
  };

  return (
    <ConfirmDialog
      open
      title="Completar mantenimiento"
      confirmLabel="Completar"
      onCancel={onClose}
      onConfirm={handleSubmit(enviar)}
    >
      <FormSection title="Datos de la realización">
        <FormField label="Fecha de realización" htmlFor="fecha_realizacion" required error={errors.fecha_realizacion?.message}>
          <input
            id="fecha_realizacion"
            type="date"
            max={hoy}
            {...register('fecha_realizacion')}
            style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
          />
        </FormField>
        <FormField label="Técnico" htmlFor="tecnico" required error={errors.tecnico?.message}>
          <select
            id="tecnico"
            {...register('tecnico', { valueAsNumber: true })}
            style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
          >
            <option value={0}>-- Selecciona --</option>
            {tecnicos.map((t) => (
              <option key={t.id} value={t.id}>
                {t.nombre_completo}
              </option>
            ))}
          </select>
        </FormField>
        <FormField label="Costo" htmlFor="costo" required error={errors.costo?.message}>
          <input
            id="costo"
            {...register('costo')}
            style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
          />
        </FormField>
        <FormField label="Observación" htmlFor="observacion_completar">
          <textarea
            id="observacion_completar"
            {...register('observacion')}
            style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
          />
        </FormField>
      </FormSection>
      {serverError && <div role="alert" style={{ color: 'var(--danger-fg)' }}>{serverError}</div>}
    </ConfirmDialog>
  );
}

function ReprogramarDialog({
  mantenimiento,
  hoy,
  onClose,
  onDone,
}: {
  mantenimiento: Mantenimiento;
  hoy: string;
  onClose: () => void;
  onDone: (mensaje: string, nuevoId?: number) => void;
}) {
  const [serverError, setServerError] = useState('');
  const { register, handleSubmit, formState: { errors }, setError } = useForm<ReprogramarFormData>({
    resolver: zodResolver(reprogramarSchema),
    defaultValues: { fecha_programada: hoy },
  });

  const enviar = async (data: ReprogramarFormData) => {
    setServerError('');
    try {
      const { data: creado, status } = await mantenimientosApi.reprogramar(
        mantenimiento.id,
        data.fecha_programada,
      );
      if (status === 201) {
        onDone('Se creó un nuevo registro; el original queda como evidencia.', creado.id);
      } else {
        onDone('Mantenimiento reprogramado.');
      }
    } catch (e: any) {
      if (!mapearErrores(e, setError)) {
        setServerError(e?.response?.data?.detail || 'No se pudo reprogramar el mantenimiento.');
      }
    }
  };

  return (
    <ConfirmDialog
      open
      title="Reprogramar mantenimiento"
      confirmLabel="Reprogramar"
      onCancel={onClose}
      onConfirm={handleSubmit(enviar)}
    >
      {mantenimiento.situacion === 'VENCIDO' && (
        <p role="note" style={{ fontSize: 13, color: 'var(--warning-fg)', marginTop: 0 }}>
          El mantenimiento está vencido: se creará un registro nuevo y este quedará como evidencia.
        </p>
      )}
      <FormField label="Nueva fecha" htmlFor="nueva_fecha" required error={errors.fecha_programada?.message}>
        <input
          id="nueva_fecha"
          type="date"
          {...register('fecha_programada')}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        />
      </FormField>
      {serverError && <div role="alert" style={{ color: 'var(--danger-fg)' }}>{serverError}</div>}
    </ConfirmDialog>
  );
}

function CancelarDialog({
  mantenimiento,
  onClose,
  onDone,
}: {
  mantenimiento: Mantenimiento;
  onClose: () => void;
  onDone: (mensaje: string) => void;
}) {
  const [serverError, setServerError] = useState('');
  const { register, handleSubmit, formState: { errors }, setError } = useForm<CancelarFormData>({
    resolver: zodResolver(cancelarSchema),
    defaultValues: { motivo: '' },
  });

  const enviar = async (data: CancelarFormData) => {
    setServerError('');
    try {
      await mantenimientosApi.cancelar(mantenimiento.id, data.motivo);
      onDone('Mantenimiento cancelado.');
    } catch (e: any) {
      if (!mapearErrores(e, setError)) {
        setServerError(e?.response?.data?.detail || 'No se pudo cancelar el mantenimiento.');
      }
    }
  };

  return (
    <ConfirmDialog
      open
      destructive
      title="Cancelar mantenimiento"
      description={`${mantenimiento.activo_codigo} · ${formatFecha(mantenimiento.fecha_programada)}`}
      confirmLabel="Cancelar mantenimiento"
      onCancel={onClose}
      onConfirm={handleSubmit(enviar)}
    >
      <FormField label="Motivo" htmlFor="motivo" required error={errors.motivo?.message}>
        <textarea
          id="motivo"
          {...register('motivo')}
          style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
        />
      </FormField>
      {serverError && <div role="alert" style={{ color: 'var(--danger-fg)' }}>{serverError}</div>}
    </ConfirmDialog>
  );
}

export function MantenimientosPage() {
  const { user } = useAuth();
  const esAdmin = user?.rol === 'ADMINISTRADOR';
  const qc = useQueryClient();

  const [tab, setTab] = useState<'calendario' | 'lista' | 'correctivos'>('calendario');
  const [anio, setAnio] = useState<number | undefined>(undefined);
  const [mes, setMes] = useState<number | undefined>(undefined);
  const [seleccionado, setSeleccionado] = useState<number | null>(null);
  const [dialogo, setDialogo] = useState<Dialogo>(null);
  const [fechaDialogo, setFechaDialogo] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [verHistorial, setVerHistorial] = useState(false);

  const [fAnio, setFAnio] = useState<number | ''>('');
  const [fMes, setFMes] = useState<number | ''>('');
  const [fSituacion, setFSituacion] = useState('');
  const [fTecnico, setFTecnico] = useState('');
  const [busqueda, setBusqueda] = useState('');
  const [page, setPage] = useState(1);
  const [cBusqueda, setCBusqueda] = useState('');
  const [cPage, setCPage] = useState(1);

  const resumenQ = useQuery<ResumenAnual>({
    queryKey: ['mant-resumen', anio],
    queryFn: () => mantenimientosApi.resumen(anio),
  });
  const anioEfectivo = resumenQ.data?.anio;
  const hoy = resumenQ.data?.hoy ?? '';
  const mesEfectivo = mes ?? (hoy ? Number(hoy.slice(5, 7)) : 1);

  const calendarioQ = useQuery<CalendarioMensual>({
    queryKey: ['mant-calendario', anioEfectivo, mesEfectivo],
    queryFn: () => mantenimientosApi.calendario(anioEfectivo as number, mesEfectivo),
    enabled: anioEfectivo !== undefined,
  });

  const tecnicosQ = useQuery<Tecnico[]>({
    queryKey: ['mant-tecnicos'],
    queryFn: () => mantenimientosApi.tecnicos(),
  });
  const tecnicos = tecnicosQ.data ?? [];

  const detalleQ = useQuery<Mantenimiento>({
    queryKey: ['mant', seleccionado],
    queryFn: () => mantenimientosApi.retrieve(seleccionado as number),
    enabled: seleccionado !== null,
  });
  const historialQ = useQuery<HistorialMantenimiento[]>({
    queryKey: ['mant-hist', seleccionado],
    queryFn: () => mantenimientosApi.historial(seleccionado as number),
    enabled: seleccionado !== null && verHistorial,
  });

  const params = useMemo(() => {
    const p: Record<string, unknown> = { page, page_size: 20, tipo: 'PREVENTIVO' };
    const anioLista = fAnio === '' ? anioEfectivo : fAnio;
    if (anioLista) p.anio = anioLista;
    if (fMes !== '') p.mes = fMes;
    if (fSituacion) p.situacion = fSituacion;
    if (fTecnico) p.tecnico = fTecnico;
    if (busqueda.trim()) p.search = busqueda.trim();
    return p;
  }, [anioEfectivo, fAnio, fMes, fSituacion, fTecnico, busqueda, page]);

  const listaQ = useQuery<Paginated<Mantenimiento>>({
    queryKey: ['mant-lista', params],
    queryFn: () => mantenimientosApi.list(params),
    enabled: tab === 'lista' && anioEfectivo !== undefined,
  });

  const correctivosQ = useQuery<Paginated<Mantenimiento>>({
    queryKey: ['mant-correctivos', cBusqueda, cPage],
    queryFn: () =>
      mantenimientosApi.list({
        tipo: 'CORRECTIVO',
        page: cPage,
        page_size: 20,
        ...(cBusqueda.trim() ? { search: cBusqueda.trim() } : {}),
      }),
    enabled: tab === 'correctivos',
  });

  const invalidar = () => {
    qc.invalidateQueries({ queryKey: ['mant-resumen'] });
    qc.invalidateQueries({ queryKey: ['mant-calendario'] });
    qc.invalidateQueries({ queryKey: ['mant-lista'] });
    qc.invalidateQueries({ queryKey: ['mant-correctivos'] });
    qc.invalidateQueries({ queryKey: ['mant'] });
    qc.invalidateQueries({ queryKey: ['mant-hist'] });
  };

  const cerrarDialogo = () => setDialogo(null);
  const terminar = (texto: string, nuevoId?: number) => {
    setMensaje(texto);
    setDialogo(null);
    invalidar();
    if (nuevoId) setSeleccionado(nuevoId);
  };

  const celdas = anioEfectivo ? construirMes(anioEfectivo, mesEfectivo) : [];
  const porFecha = useMemo(() => {
    const mapa: Record<string, Mantenimiento[]> = {};
    (calendarioQ.data?.mantenimientos ?? []).forEach((m) => {
      mapa[m.fecha_programada] = [...(mapa[m.fecha_programada] ?? []), m];
    });
    return mapa;
  }, [calendarioQ.data]);

  const detalle = detalleQ.data;
  const accionesVisibles = detalle && ['PENDIENTE', 'VENCIDO'].includes(detalle.situacion);

  const columnas: DataTableColumn<Mantenimiento>[] = [
    { key: 'fecha', header: 'Fecha', render: (m) => formatFecha(m.fecha_programada) },
    { key: 'equipo', header: 'Equipo', render: (m) => `${m.activo_codigo} · ${m.activo_serial}` },
    { key: 'modelo', header: 'Marca / Modelo', render: (m) => `${m.marca_nombre} / ${m.modelo_nombre}` },
    { key: 'tecnico', header: 'Técnico', render: (m) => m.tecnico_nombre ?? '—' },
    {
      key: 'situacion',
      header: 'Situación',
      render: (m) => (
        <StatusBadge variant={VARIANTE[m.situacion]}>{ETIQUETA[m.situacion]}</StatusBadge>
      ),
    },
    {
      key: 'acciones',
      header: '',
      render: (m) => (
        <button
          type="button"
          onClick={() => {
            setSeleccionado(m.id);
            setVerHistorial(false);
          }}
          style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer' }}
        >
          Ver
        </button>
      ),
    },
  ];

  const columnasCorrectivos: DataTableColumn<Mantenimiento>[] = [
    { key: 'fecha', header: 'Fecha del evento', render: (m) => formatFecha(m.fecha_programada) },
    { key: 'equipo', header: 'Equipo', render: (m) => `${m.activo_codigo} · ${m.activo_serial}` },
    { key: 'que_paso', header: '¿Qué pasó?', render: (m) => m.observacion },
    { key: 'seguimiento', header: 'Seguimiento', render: (m) => formatFecha(m.fecha_seguimiento) },
    { key: 'tecnico', header: 'Técnico', render: (m) => m.tecnico_nombre ?? '—' },
  ];

  return (
    <div>
      <PageHeader title="Mantenimientos" subtitle="Calendario preventivo anual y seguimiento" />

      <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 16 }}>
        <label htmlFor="anio" style={{ fontSize: 13, fontWeight: 500 }}>
          Año
        </label>
        <select
          id="anio"
          value={anioEfectivo ?? ''}
          onChange={(e) => {
            setAnio(Number(e.target.value));
            setMes(undefined);
            setPage(1);
          }}
          disabled={!anioEfectivo}
          style={{ padding: '6px 10px', border: '1px solid var(--border)', borderRadius: 6 }}
        >
          {anioEfectivo &&
            [anioEfectivo - 2, anioEfectivo - 1, anioEfectivo, anioEfectivo + 1, anioEfectivo + 2].map(
              (a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ),
            )}
        </select>
        <div role="tablist" style={{ display: 'flex', gap: 8, marginLeft: 'auto' }}>
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'calendario'}
            onClick={() => setTab('calendario')}
            style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid var(--border)', background: tab === 'calendario' ? 'var(--primary-light)' : 'var(--surface-lowest)', cursor: 'pointer' }}
          >
            Calendario
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'lista'}
            onClick={() => setTab('lista')}
            style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid var(--border)', background: tab === 'lista' ? 'var(--primary-light)' : 'var(--surface-lowest)', cursor: 'pointer' }}
          >
            Lista
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'correctivos'}
            onClick={() => setTab('correctivos')}
            style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid var(--border)', background: tab === 'correctivos' ? 'var(--primary-light)' : 'var(--surface-lowest)', cursor: 'pointer' }}
          >
            Correctivos
          </button>
        </div>
      </div>

      {mensaje && (
        <div role="status" style={{ marginBottom: 12, color: 'var(--success-fg)' }}>
          {mensaje}
        </div>
      )}

      {resumenQ.isError && (
        <div role="alert" style={{ color: 'var(--danger-fg)' }}>
          No se pudo cargar el resumen anual.
        </div>
      )}

      {tab === 'calendario' && resumenQ.data && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, minmax(0, 1fr))', gap: 8, marginBottom: 16 }}>
            {resumenQ.data.meses.map((m) => (
              <button
                key={m.mes}
                type="button"
                onClick={() => setMes(m.mes)}
                aria-label={`Mes ${MESES[m.mes - 1]}`}
                style={{
                  textAlign: 'left',
                  padding: 8,
                  borderRadius: 8,
                  border: `1px solid ${mesEfectivo === m.mes ? 'var(--primary)' : 'var(--border)'}`,
                  background: 'var(--surface-lowest)',
                  cursor: 'pointer',
                }}
              >
                <div style={{ fontSize: 13, fontWeight: 600 }}>{MESES[m.mes - 1]}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  {m.agendados} agendados · {m.completados} realizados
                </div>
                <div style={{ fontSize: 11, color: 'var(--warning-fg)' }}>
                  {m.vencidos + m.incumplidos} vencidos/incumplidos
                </div>
                <div style={{ fontSize: 12, fontWeight: 600 }}>{m.porcentaje_cumplimiento}% avance</div>
              </button>
            ))}
          </div>

          <h2 style={{ fontSize: 16, margin: '0 0 8px' }}>
            {MESES[mesEfectivo - 1]} {anioEfectivo}
          </h2>

          {calendarioQ.isError ? (
            <div role="alert" style={{ color: 'var(--danger-fg)' }}>
              No se pudo cargar el calendario.
            </div>
          ) : (
            <div role="grid" aria-label="Calendario mensual" style={{ border: '1px solid var(--border)', borderRadius: 8, overflow: 'hidden' }}>
              <div role="row" style={{ display: 'grid', gridTemplateColumns: 'repeat(7, minmax(0, 1fr))', background: 'var(--surface-low)' }}>
                {DIAS_SEMANA.map((d) => (
                  <div key={d} role="columnheader" style={{ padding: 6, fontSize: 11, color: 'var(--text-muted)' }}>
                    {d}
                  </div>
                ))}
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, minmax(0, 1fr))' }}>
                {celdas.map((c) => {
                  const items = porFecha[c.fecha] ?? [];
                  const programable = c.enMes && items.length === 0 && hoy && c.fecha >= hoy;
                  return (
                    <div
                      key={c.fecha}
                      role="gridcell"
                      style={{
                        minHeight: 72,
                        padding: 4,
                        borderTop: '1px solid var(--border)',
                        borderRight: '1px solid var(--border)',
                        opacity: c.enMes ? 1 : 0.45,
                        background: 'var(--surface-lowest)',
                      }}
                    >
                      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>{c.dia}</div>
                      {items.map((m) => (
                        <Chip
                          key={m.id}
                          mantenimiento={m}
                          onClick={() => {
                            setSeleccionado(m.id);
                            setVerHistorial(false);
                          }}
                        />
                      ))}
                      {programable && (
                        <button
                          type="button"
                          aria-label={`Programar ${c.fecha}`}
                          onClick={() => {
                            setFechaDialogo(c.fecha);
                            setDialogo('programar');
                          }}
                          style={{ width: '100%', border: '1px dashed var(--border)', background: 'none', color: 'var(--primary)', cursor: 'pointer', borderRadius: 4, fontSize: 11 }}
                        >
                          + Programar
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {calendarioQ.data && calendarioQ.data.mantenimientos.length === 0 && (
            <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
              Sin mantenimientos programados en este mes.
            </p>
          )}
        </>
      )}

      {tab === 'lista' && (
        <div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
            <input
              value={busqueda}
              onChange={(e) => {
                setBusqueda(e.target.value);
                setPage(1);
              }}
              placeholder="Buscar serial, código, marca o modelo"
              style={{ padding: '6px 10px', border: '1px solid var(--border)', borderRadius: 6, minWidth: 240 }}
            />
            <select
              aria-label="Filtrar por año"
              value={fAnio}
              onChange={(e) => {
                setFAnio(e.target.value ? Number(e.target.value) : '');
                setPage(1);
              }}
              style={{ padding: '6px 10px', border: '1px solid var(--border)', borderRadius: 6 }}
            >
              <option value="">Año actual</option>
              {anioEfectivo && [anioEfectivo - 1, anioEfectivo, anioEfectivo + 1].map((a) => (
                <option key={a} value={a}>
                  {a}
                </option>
              ))}
            </select>
            <select
              aria-label="Filtrar por mes"
              value={fMes}
              onChange={(e) => {
                setFMes(e.target.value ? Number(e.target.value) : '');
                setPage(1);
              }}
              style={{ padding: '6px 10px', border: '1px solid var(--border)', borderRadius: 6 }}
            >
              <option value="">Todos los meses</option>
              {MESES.map((m, i) => (
                <option key={m} value={i + 1}>
                  {m}
                </option>
              ))}
            </select>
            <select
              aria-label="Filtrar por situación"
              value={fSituacion}
              onChange={(e) => {
                setFSituacion(e.target.value);
                setPage(1);
              }}
              style={{ padding: '6px 10px', border: '1px solid var(--border)', borderRadius: 6 }}
            >
              <option value="">Todas las situaciones</option>
              {Object.entries(ETIQUETA).map(([valor, texto]) => (
                <option key={valor} value={valor}>
                  {texto}
                </option>
              ))}
            </select>
            <select
              aria-label="Filtrar por técnico"
              value={fTecnico}
              onChange={(e) => {
                setFTecnico(e.target.value);
                setPage(1);
              }}
              style={{ padding: '6px 10px', border: '1px solid var(--border)', borderRadius: 6 }}
            >
              <option value="">Todos los técnicos</option>
              {tecnicos.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.nombre_completo}
                </option>
              ))}
            </select>
          </div>

          {listaQ.isError ? (
            <div role="alert" style={{ color: 'var(--danger-fg)' }}>
              No se pudo cargar la lista.
            </div>
          ) : (
            <DataTable
              columns={columnas}
              data={listaQ.data?.results ?? []}
              rowKey={(m) => m.id}
              emptyState={<p style={{ fontSize: 13, color: 'var(--text-muted)' }}>No hay mantenimientos con esos filtros.</p>}
            />
          )}

          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 12 }}>
            <button type="button" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              Anterior
            </button>
            <span style={{ fontSize: 13 }}>Página {page}</span>
            <button
              type="button"
              disabled={!listaQ.data?.next}
              onClick={() => setPage((p) => p + 1)}
            >
              Siguiente
            </button>
          </div>
        </div>
      )}

      {tab === 'correctivos' && (
        <div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
            <input
              value={cBusqueda}
              onChange={(e) => {
                setCBusqueda(e.target.value);
                setCPage(1);
              }}
              placeholder="Buscar serial, código, marca o modelo"
              style={{ padding: '6px 10px', border: '1px solid var(--border)', borderRadius: 6, minWidth: 240 }}
            />
            <button
              type="button"
              onClick={() => setDialogo('correctivo')}
              style={{ marginLeft: 'auto', padding: '8px 14px', borderRadius: 6, border: 'none', background: 'var(--primary)', color: '#fff', cursor: 'pointer' }}
            >
              Registrar correctivo
            </button>
          </div>

          {correctivosQ.isError ? (
            <div role="alert" style={{ color: 'var(--danger-fg)' }}>
              No se pudieron cargar los correctivos.
            </div>
          ) : (
            <DataTable
              columns={columnasCorrectivos}
              data={correctivosQ.data?.results ?? []}
              rowKey={(m) => m.id}
              emptyState={<p style={{ fontSize: 13, color: 'var(--text-muted)' }}>No hay correctivos registrados.</p>}
            />
          )}

          <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 12 }}>
            <button type="button" disabled={cPage <= 1} onClick={() => setCPage((p) => p - 1)}>
              Anterior
            </button>
            <span style={{ fontSize: 13 }}>Página {cPage}</span>
            <button
              type="button"
              disabled={!correctivosQ.data?.next}
              onClick={() => setCPage((p) => p + 1)}
            >
              Siguiente
            </button>
          </div>
        </div>
      )}

      {detalle && (
        <section style={{ marginTop: 20, padding: 16, border: '1px solid var(--border)', borderRadius: 8, background: 'var(--surface-lowest)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h2 style={{ margin: 0, fontSize: 16 }}>
                {detalle.activo_codigo} · {detalle.activo_serial}
              </h2>
              <p style={{ margin: '4px 0', fontSize: 13, color: 'var(--text-muted)' }}>
                {detalle.marca_nombre} / {detalle.modelo_nombre} · {detalle.categoria_nombre}
              </p>
              <p style={{ margin: '4px 0', fontSize: 13 }}>
                Técnico: {detalle.tecnico_nombre ?? 'Sin asignar'} · Programado: {formatFecha(detalle.fecha_programada)}
              </p>
              {detalle.reprogramado_como && (
                <button type="button" onClick={() => setSeleccionado(detalle.reprogramado_como)} style={{ background: 'none', border: 'none', color: 'var(--primary)', padding: 0, cursor: 'pointer', fontSize: 13 }}>
                  Reprogramado como #{detalle.reprogramado_como}
                </button>
              )}
              {detalle.reprogramacion_de && (
                <button type="button" onClick={() => setSeleccionado(detalle.reprogramacion_de)} style={{ background: 'none', border: 'none', color: 'var(--primary)', padding: 0, cursor: 'pointer', fontSize: 13 }}>
                  Reprogramación de #{detalle.reprogramacion_de}
                </button>
              )}
            </div>
            <StatusBadge variant={VARIANTE[detalle.situacion]}>{ETIQUETA[detalle.situacion]}</StatusBadge>
          </div>

          <div style={{ display: 'flex', gap: 8, margin: '12px 0' }}>
            {accionesVisibles && (
              <>
                <button type="button" onClick={() => setDialogo('completar')} style={{ padding: '6px 12px', border: '1px solid var(--border)', borderRadius: 6, cursor: 'pointer' }}>
                  Completar
                </button>
                <button type="button" onClick={() => setDialogo('reprogramar')} style={{ padding: '6px 12px', border: '1px solid var(--border)', borderRadius: 6, cursor: 'pointer' }}>
                  Reprogramar
                </button>
                {esAdmin && (
                  <button type="button" onClick={() => setDialogo('cancelar')} style={{ padding: '6px 12px', border: '1px solid var(--danger-fg)', color: 'var(--danger-fg)', borderRadius: 6, cursor: 'pointer' }}>
                    Cancelar
                  </button>
                )}
              </>
            )}
            {detalle.situacion === 'INCUMPLIDO' && detalle.reprogramado_como && (
              <button type="button" onClick={() => setSeleccionado(detalle.reprogramado_como)} style={{ padding: '6px 12px', border: '1px solid var(--border)', borderRadius: 6, cursor: 'pointer' }}>
                Ver reprogramación
              </button>
            )}
          </div>

          <div style={{ display: 'flex', gap: 8, borderBottom: '1px solid var(--border)' }}>
            <button type="button" onClick={() => setVerHistorial(false)} aria-pressed={!verHistorial} style={{ padding: '6px 10px', border: 'none', background: 'none', fontWeight: !verHistorial ? 600 : 400, cursor: 'pointer' }}>
              Resumen
            </button>
            <button type="button" onClick={() => setVerHistorial(true)} aria-pressed={verHistorial} style={{ padding: '6px 10px', border: 'none', background: 'none', fontWeight: verHistorial ? 600 : 400, cursor: 'pointer' }}>
              Historial
            </button>
          </div>

          {verHistorial ? (
            <ul style={{ fontSize: 13 }}>
              {(historialQ.data ?? []).map((h, i) => (
                <li key={i}>
                  {formatFecha(h.fecha)} — {h.usuario ?? 'Sistema'} — {h.tipo} — {h.campos.join(', ')}
                </li>
              ))}
            </ul>
          ) : (
            <div style={{ fontSize: 13 }}>
              <p>Estado: {detalle.estado}</p>
              <p>Realizado: {detalle.fecha_realizacion ? formatFecha(detalle.fecha_realizacion) : '—'}</p>
              <p>Costo: {detalle.costo ?? '—'}</p>
              <p>Observación: {detalle.observacion || '—'}</p>
              {detalle.motivo_cancelacion && <p>Motivo de cancelación: {detalle.motivo_cancelacion}</p>}
            </div>
          )}
        </section>
      )}

      {dialogo === 'programar' && (
        <ProgramarDialog fecha={fechaDialogo} onClose={cerrarDialogo} onDone={terminar} />
      )}
      {dialogo === 'correctivo' && (
        <CorrectivoDialog
          hoy={hoy}
          tecnicos={tecnicos}
          onClose={cerrarDialogo}
          onDone={terminar}
        />
      )}
      {dialogo === 'completar' && detalle && (
        <CompletarDialog
          mantenimiento={detalle}
          hoy={hoy}
          tecnicos={tecnicos}
          onClose={cerrarDialogo}
          onDone={terminar}
        />
      )}
      {dialogo === 'reprogramar' && detalle && (
        <ReprogramarDialog mantenimiento={detalle} hoy={hoy} onClose={cerrarDialogo} onDone={terminar} />
      )}
      {dialogo === 'cancelar' && detalle && (
        <CancelarDialog mantenimiento={detalle} onClose={cerrarDialogo} onDone={terminar} />
      )}
    </div>
  );
}
