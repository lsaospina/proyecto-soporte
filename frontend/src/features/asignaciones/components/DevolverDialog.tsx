import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { ConfirmDialog } from '../../../components/shared/ConfirmDialog';
import { FormField } from '../../../components/shared/FormField';
import { aISO } from '../../../lib/format';
import { asignacionesApi } from '../api/asignaciones.api';
import { cerrarSchema, type CerrarFormData } from '../schemas/asignacion.schema';
import type { Asignacion } from '../types';
import { estiloCampo } from '../utils/asignaciones';

interface DevolverDialogProps {
  asignacion: Asignacion;
  onClose: () => void;
  onDone: (mensaje: string) => void;
}

export function DevolverDialog({ asignacion, onClose, onDone }: DevolverDialogProps) {
  const [serverError, setServerError] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [hoy] = useState(() => aISO(new Date()));
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CerrarFormData>({
    resolver: zodResolver(cerrarSchema(asignacion.fecha_inicio)),
    defaultValues: { fecha_fin: hoy },
  });

  const enviar = async (datos: CerrarFormData) => {
    setServerError('');
    setEnviando(true);
    try {
      await asignacionesApi.cerrar(asignacion.id, { fecha_fin: datos.fecha_fin });
      onDone('Devolución registrada.');
    } catch (error: unknown) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      setServerError(
        axiosError.response?.data?.detail || 'No se pudo registrar la devolución.',
      );
    } finally {
      setEnviando(false);
    }
  };

  return (
    <ConfirmDialog
      open
      title="Registrar devolución"
      description={`${asignacion.activo_codigo} · ${asignacion.usuario_nombre}`}
      confirmLabel="Registrar devolución"
      isLoading={enviando}
      onConfirm={handleSubmit(enviar)}
      onCancel={onClose}
    >
      {serverError && (
        <p role="alert" style={{ fontSize: '13px', color: 'var(--danger-fg)', margin: '0 0 12px' }}>
          {serverError}
        </p>
      )}
      <FormField
        label="Fecha de devolución"
        htmlFor="devolver-fecha"
        required
        error={errors.fecha_fin?.message}
      >
        <input
          id="devolver-fecha"
          type="date"
          {...register('fecha_fin')}
          style={estiloCampo(!!errors.fecha_fin)}
        />
      </FormField>
    </ConfirmDialog>
  );
}
