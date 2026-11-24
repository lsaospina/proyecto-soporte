import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

import { ConfirmDialog } from '../../../components/shared/ConfirmDialog';
import { FormField } from '../../../components/shared/FormField';
import { licenciasApi } from '../api/licencias.api';
import {
  renovarLicenciaSchema,
  type RenovarLicenciaFormData,
} from '../schemas/licencia.schema';
import type { Licencia } from '../types';
import { renovacionSugerida } from '../utils/licencias';
import { estiloCampo } from './campos';

interface RenovarLicenciaDialogProps {
  licencia: Licencia;
  onClose: () => void;
  onDone: (mensaje: string) => void;
}

export function RenovarLicenciaDialog({ licencia, onClose, onDone }: RenovarLicenciaDialogProps) {
  const [serverError, setServerError] = useState('');
  const [enviando, setEnviando] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RenovarLicenciaFormData>({
    resolver: zodResolver(renovarLicenciaSchema),
    defaultValues: {
      fecha_renovacion: renovacionSugerida(licencia.fecha_renovacion, licencia.periodicidad),
      valor: licencia.valor ?? '',
    },
  });

  const enviar = async (datos: RenovarLicenciaFormData) => {
    setServerError('');
    setEnviando(true);
    try {
      await licenciasApi.renovar(licencia.id, {
        fecha_renovacion: datos.fecha_renovacion,
        valor: datos.valor.trim() === '' ? null : datos.valor.trim(),
      });
      onDone('Licencia renovada.');
    } catch (error: unknown) {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      setServerError(axiosError.response?.data?.detail || 'No se pudo renovar la licencia.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <ConfirmDialog
      open
      title="Renovar licencia"
      description={`${licencia.servicio} · ${licencia.proveedor_nombre}`}
      confirmLabel="Renovar"
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
        label="Nueva fecha de renovación"
        htmlFor="renovar-fecha"
        required
        error={errors.fecha_renovacion?.message}
      >
        <input
          id="renovar-fecha"
          type="date"
          {...register('fecha_renovacion')}
          style={estiloCampo(!!errors.fecha_renovacion)}
        />
      </FormField>
      <FormField
        label="Valor a pagar (COP)"
        htmlFor="renovar-valor"
        error={errors.valor?.message}
        helpText="Déjelo vacío para conservar el valor actual."
      >
        <input
          id="renovar-valor"
          inputMode="decimal"
          {...register('valor')}
          style={estiloCampo(!!errors.valor)}
          placeholder="0"
        />
      </FormField>
    </ConfirmDialog>
  );
}
