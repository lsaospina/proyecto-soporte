import { useEffect, useState, type CSSProperties } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowLeft } from 'lucide-react';

import { ErrorState } from '../../../components/shared/ErrorState';
import { FormField } from '../../../components/shared/FormField';
import { FormSection } from '../../../components/shared/FormSection';
import { LoadingSkeleton } from '../../../components/shared/LoadingSkeleton';
import { PageHeader } from '../../../components/shared/PageHeader';
import { aISO } from '../../../lib/format';
import { licenciasApi } from '../api/licencias.api';
import { estiloCampo } from '../components/campos';
import { licenciaSchema, type LicenciaFormData } from '../schemas/licencia.schema';
import { OPCIONES_PERIODICIDAD } from '../utils/licencias';

const gridCampos: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
  gap: '0 16px',
};

const botonPrimario: CSSProperties = {
  padding: '8px 16px',
  borderRadius: 'var(--radius-control)',
  border: 'none',
  backgroundColor: 'var(--primary)',
  color: 'var(--text-inverse)',
  fontSize: '13px',
  fontWeight: 600,
};

const botonSecundario: CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: '8px 16px',
  borderRadius: 'var(--radius-control)',
  border: '1px solid var(--border)',
  backgroundColor: 'var(--surface-lowest)',
  color: 'var(--text)',
  fontSize: '13px',
  fontWeight: 500,
};

function valoresIniciales(): LicenciaFormData {
  return {
    proveedor: '',
    servicio: '',
    periodicidad: 'ANUAL',
    fecha_renovacion: aISO(new Date()),
    cantidad: 1,
    valor: '',
    renovacion_automatica: false,
    medio_pago: '',
    cuenta_vinculada: '',
    responsable_uso: '',
    observacion: '',
  };
}

export function LicenciaFormPage() {
  const { id } = useParams();
  const isEdit = Boolean(id);
  const licenciaId = id ? Number(id) : null;
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [serverError, setServerError] = useState('');

  const licenciaQ = useQuery({
    queryKey: ['licencia', licenciaId],
    queryFn: () => licenciasApi.retrieve(licenciaId!),
    enabled: isEdit && licenciaId !== null,
  });
  const proveedoresQ = useQuery({
    queryKey: ['licencias', 'proveedores'],
    queryFn: licenciasApi.proveedores,
  });

  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors },
  } = useForm<LicenciaFormData>({
    resolver: zodResolver(licenciaSchema),
    defaultValues: valoresIniciales(),
  });

  useEffect(() => {
    if (isEdit && licenciaQ.data) {
      const licencia = licenciaQ.data;
      reset({
        proveedor: licencia.proveedor_nombre,
        servicio: licencia.servicio,
        periodicidad: licencia.periodicidad,
        fecha_renovacion: licencia.fecha_renovacion,
        cantidad: licencia.cantidad,
        valor: licencia.valor ?? '',
        renovacion_automatica: licencia.renovacion_automatica,
        medio_pago: licencia.medio_pago,
        cuenta_vinculada: licencia.cuenta_vinculada,
        responsable_uso: licencia.responsable_uso,
        observacion: licencia.observacion,
      });
    }
  }, [isEdit, licenciaQ.data, reset]);

  const guardar = useMutation({
    mutationFn: (datos: LicenciaFormData) => {
      const payload = {
        ...datos,
        valor: datos.valor.trim() === '' ? null : datos.valor.trim(),
      };
      return isEdit && licenciaId !== null
        ? licenciasApi.actualizar(licenciaId, payload)
        : licenciasApi.crear(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['licencias'] });
      queryClient.invalidateQueries({ queryKey: ['licencia', licenciaId] });
      navigate('/licencias');
    },
    onError: (error: unknown) => {
      const axiosError = error as {
        response?: { data?: { detail?: string; errors?: Array<{ field: string; message: string }> } };
      };
      const errores = axiosError.response?.data?.errors ?? [];
      let aplicado = false;
      errores.forEach((item) => {
        if (item.field && item.field in valoresIniciales()) {
          setError(item.field as keyof LicenciaFormData, { type: 'server', message: item.message });
          aplicado = true;
        }
      });
      if (!aplicado) {
        setServerError(
          axiosError.response?.data?.detail || 'No se pudo guardar la licencia.',
        );
      }
    },
  });

  if (isEdit && licenciaQ.isLoading) return <LoadingSkeleton lines={6} />;
  if (isEdit && licenciaQ.isError) {
    return <ErrorState message="No se pudo cargar la licencia." onRetry={() => licenciaQ.refetch()} />;
  }

  const onSubmit = (datos: LicenciaFormData) => {
    setServerError('');
    guardar.mutate(datos);
  };

  return (
    <div>
      <Link
        to="/licencias"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '4px',
          color: 'var(--text-muted)',
          fontSize: '13px',
          marginBottom: '12px',
        }}
      >
        <ArrowLeft size={16} /> Volver a licencias
      </Link>

      <PageHeader
        title={isEdit ? 'Editar licencia' : 'Nueva licencia'}
        subtitle={
          isEdit
            ? `Actualización de ${licenciaQ.data?.servicio ?? ''}`
            : 'Registra la suscripción para controlar su próxima renovación.'
        }
      />

      {serverError && (
        <div
          role="alert"
          style={{
            marginBottom: '16px',
            padding: '10px 12px',
            borderRadius: 'var(--radius-control)',
            backgroundColor: 'var(--danger-bg)',
            color: 'var(--danger-fg)',
            fontSize: '13px',
          }}
        >
          {serverError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        <FormSection title="Servicio" description="Proveedor, nombre del servicio y periodicidad de cobro.">
          <div style={gridCampos}>
            <FormField
              label="Proveedor"
              htmlFor="proveedor"
              required
              error={errors.proveedor?.message}
              helpText="Puede escribir uno nuevo; se creará automáticamente."
            >
              <input
                id="proveedor"
                list="proveedores-opciones"
                {...register('proveedor')}
                placeholder="Microsoft, Google, Hostingred…"
                style={estiloCampo(!!errors.proveedor)}
              />
              <datalist id="proveedores-opciones">
                {(proveedoresQ.data ?? []).map((opcion) => (
                  <option key={opcion.id} value={opcion.nombre} />
                ))}
              </datalist>
            </FormField>
            <FormField
              label="Servicio"
              htmlFor="servicio"
              required
              error={errors.servicio?.message}
            >
              <input
                id="servicio"
                {...register('servicio')}
                placeholder="Microsoft 365, Dominio, Internet dedicado…"
                style={estiloCampo(!!errors.servicio)}
              />
            </FormField>
            <FormField
              label="Periodicidad"
              htmlFor="periodicidad"
              required
              error={errors.periodicidad?.message}
            >
              <select
                id="periodicidad"
                {...register('periodicidad')}
                style={estiloCampo(!!errors.periodicidad)}
              >
                {OPCIONES_PERIODICIDAD.map((opcion) => (
                  <option key={opcion.value} value={opcion.value}>
                    {opcion.label}
                  </option>
                ))}
              </select>
            </FormField>
            <FormField
              label="Cantidad de licencias"
              htmlFor="cantidad"
              required
              error={errors.cantidad?.message}
            >
              <input
                id="cantidad"
                type="number"
                min={1}
                {...register('cantidad')}
                style={estiloCampo(!!errors.cantidad)}
              />
            </FormField>
          </div>
        </FormSection>

        <FormSection
          title="Renovación y costo"
          description="Fecha del próximo pago, valor y si el cobro se hace automáticamente."
        >
          <div style={gridCampos}>
            <FormField
              label="Fecha de renovación"
              htmlFor="fecha_renovacion"
              required
              error={errors.fecha_renovacion?.message}
            >
              <input
                id="fecha_renovacion"
                type="date"
                {...register('fecha_renovacion')}
                style={estiloCampo(!!errors.fecha_renovacion)}
              />
            </FormField>
            <FormField
              label="Valor a pagar (COP)"
              htmlFor="valor"
              error={errors.valor?.message}
              helpText="Déjelo vacío si el valor es variable."
            >
              <input
                id="valor"
                inputMode="decimal"
                {...register('valor')}
                placeholder="0"
                style={estiloCampo(!!errors.valor)}
              />
            </FormField>
            <FormField
              label="Renovación automática"
              htmlFor="renovacion_automatica"
              error={errors.renovacion_automatica?.message}
            >
              <label
                htmlFor="renovacion_automatica"
                style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', minHeight: '37px' }}
              >
                <input id="renovacion_automatica" type="checkbox" {...register('renovacion_automatica')} />
                El cobro se realiza automáticamente
              </label>
            </FormField>
          </div>
        </FormSection>

        <FormSection title="Pago y uso" description="Medio de pago, cuenta vinculada y persona o área que usa la licencia.">
          <div style={gridCampos}>
            <FormField
              label="Medio de pago"
              htmlFor="medio_pago"
              error={errors.medio_pago?.message}
            >
              <input
                id="medio_pago"
                {...register('medio_pago')}
                placeholder="Facturación electrónica, Visa **0000…"
                style={estiloCampo(!!errors.medio_pago)}
              />
            </FormField>
            <FormField
              label="Cuenta vinculada"
              htmlFor="cuenta_vinculada"
              error={errors.cuenta_vinculada?.message}
            >
              <input
                id="cuenta_vinculada"
                {...register('cuenta_vinculada')}
                placeholder="cuenta@empresa.com"
                style={estiloCampo(!!errors.cuenta_vinculada)}
              />
            </FormField>
            <FormField
              label="Responsable o área de uso"
              htmlFor="responsable_uso"
              error={errors.responsable_uso?.message}
            >
              <input
                id="responsable_uso"
                {...register('responsable_uso')}
                placeholder="Equipo de Sistemas, Oficina Bogotá…"
                style={estiloCampo(!!errors.responsable_uso)}
              />
            </FormField>
          </div>
          <FormField label="Observaciones" htmlFor="observacion" error={errors.observacion?.message}>
            <textarea
              id="observacion"
              rows={3}
              {...register('observacion')}
              placeholder="Notas de la renovación, condiciones del proveedor…"
              style={estiloCampo(!!errors.observacion)}
            />
          </FormField>
        </FormSection>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '8px' }}>
          <button type="button" onClick={() => navigate('/licencias')} style={botonSecundario}>
            Cancelar
          </button>
          <button type="submit" disabled={guardar.isPending} style={botonPrimario}>
            {guardar.isPending ? 'Guardando…' : 'Guardar licencia'}
          </button>
        </div>
      </form>
    </div>
  );
}
