import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { ConfirmDialog } from '../../../components/shared/ConfirmDialog';
import { FormField } from '../../../components/shared/FormField';
import { aISO } from '../../../lib/format';
import { activosApi } from '../../activos/api/activos.api';
import { asignacionesApi } from '../api/asignaciones.api';
import { asignarSchema, type AsignarFormData } from '../schemas/asignacion.schema';
import { ETIQUETA_ROL, estiloCampo } from '../utils/asignaciones';

interface ActivoFijo {
  id: number;
  activo_codigo: string;
  activo_serial: string;
  marca_nombre: string;
  modelo_nombre: string;
}

interface AsignarDialogProps {
  modo: 'asignar' | 'reasignar';
  activoFijo?: ActivoFijo | null;
  onClose: () => void;
  onDone: (mensaje: string) => void;
}

export function AsignarDialog({ modo, activoFijo, onClose, onDone }: AsignarDialogProps) {
  const [serverError, setServerError] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [hoy] = useState(() => aISO(new Date()));

  const usuariosQ = useQuery({
    queryKey: ['asignaciones', 'usuarios'],
    queryFn: asignacionesApi.usuarios,
  });
  const activosQ = useQuery({
    queryKey: ['activos', 'disponibles-asignacion'],
    queryFn: () =>
      activosApi.list({
        page_size: 100,
        is_active: true,
        estado: 'DISPONIBLE',
        estado_no: 'DADO_DE_BAJA',
      }),
    enabled: modo === 'asignar',
  });

  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<AsignarFormData>({
    resolver: zodResolver(asignarSchema),
    defaultValues: {
      activo: activoFijo?.id ?? 0,
      usuario: 0,
      fecha_inicio: hoy,
      observacion: '',
    },
  });

  const enviar = async (datos: AsignarFormData) => {
    setServerError('');
    setEnviando(true);
    try {
      if (modo === 'reasignar') {
        await asignacionesApi.reasignar({
          activo: datos.activo,
          usuario: datos.usuario,
          fecha_inicio: datos.fecha_inicio,
          observacion: datos.observacion,
        });
        onDone('Equipo reasignado.');
      } else {
        await asignacionesApi.crear({
          activo: datos.activo,
          usuario: datos.usuario,
          fecha_inicio: datos.fecha_inicio,
          observacion: datos.observacion,
        });
        onDone('Equipo asignado.');
      }
    } catch (error: unknown) {
      const axiosError = error as {
        response?: {
          data?: { detail?: string; errors?: Array<{ field: string; message: string }> };
        };
      };
      const errores = axiosError.response?.data?.errors ?? [];
      let aplicado = false;
      errores.forEach((item) => {
        if (item.field === 'activo' || item.field === 'usuario' || item.field === 'fecha_inicio') {
          setError(item.field, { type: 'server', message: item.message });
          aplicado = true;
        }
      });
      if (!aplicado) {
        setServerError(
          axiosError.response?.data?.detail || 'No se pudo guardar la asignación.',
        );
      }
    } finally {
      setEnviando(false);
    }
  };

  const activos = activosQ.data?.results ?? [];

  return (
    <ConfirmDialog
      open
      title={modo === 'reasignar' ? 'Reasignar activo' : 'Nueva asignación'}
      description={
        modo === 'reasignar' && activoFijo
          ? `${activoFijo.activo_codigo} · ${activoFijo.marca_nombre} ${activoFijo.modelo_nombre}`
          : 'Relaciona un equipo disponible con el colaborador que lo usará.'
      }
      confirmLabel={modo === 'reasignar' ? 'Reasignar' : 'Asignar'}
      isLoading={enviando}
      onConfirm={handleSubmit(enviar)}
      onCancel={onClose}
    >
      {serverError && (
        <p role="alert" style={{ fontSize: '13px', color: 'var(--danger-fg)', margin: '0 0 12px' }}>
          {serverError}
        </p>
      )}

      {modo === 'asignar' ? (
        <FormField
          label="Equipo"
          htmlFor="asignar-activo"
          required
          error={errors.activo?.message}
          helpText="Solo se muestran equipos disponibles."
        >
          <select
            id="asignar-activo"
            {...register('activo')}
            style={estiloCampo(!!errors.activo)}
          >
            <option value={0}>
              {activosQ.isLoading ? 'Cargando equipos…' : 'Seleccione un equipo'}
            </option>
            {activos.map((activo: any) => (
              <option key={activo.id} value={activo.id}>
                {activo.codigo_qr} — {activo.marca_nombre} {activo.modelo_nombre} ({activo.serial})
              </option>
            ))}
          </select>
        </FormField>
      ) : (
        <input type="hidden" {...register('activo')} />
      )}

      <FormField
        label="Colaborador"
        htmlFor="asignar-usuario"
        required
        error={errors.usuario?.message}
      >
        <select
          id="asignar-usuario"
          {...register('usuario')}
          style={estiloCampo(!!errors.usuario)}
        >
          <option value={0}>
            {usuariosQ.isLoading ? 'Cargando colaboradores…' : 'Seleccione un colaborador'}
          </option>
          {(usuariosQ.data ?? []).map((usuario) => (
            <option key={usuario.id} value={usuario.id}>
              {usuario.nombre_completo} — {ETIQUETA_ROL[usuario.rol] ?? usuario.rol}
            </option>
          ))}
        </select>
      </FormField>

      <FormField
        label="Fecha de inicio"
        htmlFor="asignar-fecha"
        required
        error={errors.fecha_inicio?.message}
      >
        <input
          id="asignar-fecha"
          type="date"
          {...register('fecha_inicio')}
          style={estiloCampo(!!errors.fecha_inicio)}
        />
      </FormField>

      <FormField label="Observación" htmlFor="asignar-observacion" error={errors.observacion?.message}>
        <textarea
          id="asignar-observacion"
          rows={2}
          {...register('observacion')}
          placeholder="Acta de entrega, accesorios, condiciones…"
          style={estiloCampo(!!errors.observacion)}
        />
      </FormField>
    </ConfirmDialog>
  );
}
