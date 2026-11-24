import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { PageHeader } from '../../../components/shared/PageHeader';
import { FormSection } from '../../../components/shared/FormSection';
import { FormField } from '../../../components/shared/FormField';
import { activoSchema, type ActivoFormData } from '../schemas/activo.schema';
import { activosApi } from '../api/activos.api';
import { useOpcionesCatalogo } from '../../catalogos/hooks/useOpcionesCatalogo';

export function ActivosFormPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const activoId = id ? Number(id) : null;
  const esEdicion = activoId !== null;
  const { register, handleSubmit, reset, setError, formState: { errors } } = useForm<ActivoFormData>({
    resolver: zodResolver(activoSchema),
  });
  const marcas = useOpcionesCatalogo('marcas');
  const modelos = useOpcionesCatalogo('modelos', null);
  const { data: activo } = useQuery({
    queryKey: ['activos', activoId],
    queryFn: () => activosApi.retrieve(activoId as number),
    enabled: esEdicion,
  });
  const [marcaSeleccionada, setMarcaSeleccionada] = useState<number | ''>('');
  const [serverError, setServerError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!activo) return;
    reset({
      serial: activo.serial,
      modelo: activo.modelo,
      fecha_adquisicion: activo.fecha_adquisicion,
      valor_adquisicion: activo.valor_adquisicion ?? '',
      procesador: activo.procesador ?? '',
      ram_gb: activo.ram_gb ?? undefined,
      almacenamiento_gb: activo.almacenamiento_gb ?? undefined,
      direccion_mac: activo.direccion_mac ?? '',
      observaciones: activo.observaciones ?? '',
    });
  }, [activo, modelos.data, reset]);

  const modeloDelActivo = activo ? (modelos.data ?? []).find((m: any) => m.id === activo.modelo) : undefined;
  const marcaEfectiva = marcaSeleccionada !== '' ? marcaSeleccionada : (modeloDelActivo?.marca ?? '');

  const modelosFiltrados = (modelos.data ?? []).filter(
    (m: any) => !marcaEfectiva || m.marca === marcaEfectiva,
  );

  const onSubmit = async (data: ActivoFormData) => {
    setServerError('');
    setIsSubmitting(true);
    try {
      if (esEdicion) {
        await activosApi.update(activoId as number, data);
      } else {
        await activosApi.create(data);
      }
      navigate('/activos');
    } catch (e: any) {
      const body = e?.response?.data;
      const serialError = Array.isArray(body?.serial) ? body.serial[0] : body?.serial;
      if (serialError) {
        setError('serial', { type: 'server', message: String(serialError) });
        return;
      }
      setServerError(body?.detail || 'No se pudo registrar el activo.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <PageHeader title={esEdicion ? 'Editar activo' : 'Registrar activo'} subtitle="Activo tecnológico" />
      <form onSubmit={handleSubmit(onSubmit)}>
        <FormSection title="Identificación">
          <FormField label="Serial" htmlFor="serial" required error={errors.serial?.message}>
            <input
              id="serial"
              {...register('serial')}
              style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
            />
          </FormField>
          <FormField label="Marca" htmlFor="marca" required>
            <select
              id="marca"
              value={marcaEfectiva}
              onChange={(e) => setMarcaSeleccionada(e.target.value ? Number(e.target.value) : '')}
              style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
            >
              <option value="">-- Selecciona --</option>
              {(marcas.data ?? []).map((m: any) => (
                <option key={m.id} value={m.id}>
                  {m.nombre}
                </option>
              ))}
            </select>
          </FormField>
          <FormField label="Modelo" htmlFor="modelo" required>
            <select
              id="modelo"
              {...register('modelo', { valueAsNumber: true })}
              style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
            >
              <option value="">-- Selecciona --</option>
              {modelosFiltrados.map((m: any) => (
                <option key={m.id} value={m.id}>
                  {m.nombre}
                </option>
              ))}
            </select>
          </FormField>
        </FormSection>

        <FormSection title="Adquisición">
          <FormField label="Fecha de adquisición" htmlFor="fecha_adquisicion" required>
            <input
              id="fecha_adquisicion"
              type="date"
              {...register('fecha_adquisicion')}
              style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
            />
          </FormField>
          <FormField label="Valor de adquisición (COP)" htmlFor="valor_adquisicion">
            <input
              id="valor_adquisicion"
              {...register('valor_adquisicion')}
              style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
            />
          </FormField>
        </FormSection>

        {serverError && <div style={{ color: 'var(--danger-fg)', marginTop: 8 }}>{serverError}</div>}

        <div style={{ display: 'flex', gap: 8, marginTop: 16, justifyContent: 'flex-end' }}>
          <button
            type="button"
            onClick={() => navigate('/activos')}
            style={{ padding: '8px 16px', border: '1px solid var(--border)', background: 'var(--surface-lowest)', cursor: 'pointer' }}
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            style={{ padding: '8px 16px', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: 6, cursor: 'pointer' }}
          >
            Guardar
          </button>
        </div>
      </form>
    </div>
  );
}
