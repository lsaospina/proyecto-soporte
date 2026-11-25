import { useRef, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Download, FileText, Trash2, Upload } from 'lucide-react';

import { ConfirmDialog } from '../../../components/shared/ConfirmDialog';
import { DataTable, type DataTableColumn } from '../../../components/shared/DataTable';
import { EmptyState } from '../../../components/shared/EmptyState';
import { ErrorState } from '../../../components/shared/ErrorState';
import { FormField } from '../../../components/shared/FormField';
import { FormSection } from '../../../components/shared/FormSection';
import { LoadingSkeleton } from '../../../components/shared/LoadingSkeleton';
import { StatusBadge } from '../../../components/shared/StatusBadge';
import { documentosApi, type Documento } from '../api/documentos.api';

const TIPOS = [
  { value: 'FACTURA', label: 'Factura' },
  { value: 'MANUAL', label: 'Manual' },
  { value: 'GARANTIA', label: 'Garantía' },
  { value: 'CONTRATO', label: 'Contrato' },
  { value: 'EVIDENCIA_MANTENIMIENTO', label: 'Evidencia de mantenimiento' },
  { value: 'OTRO', label: 'Otro' },
];

const MAX_BYTES = 10 * 1024 * 1024;
const EXTENSIONES = ['.pdf', '.png', '.jpg', '.jpeg', '.doc', '.docx', '.xls', '.xlsx', '.txt'];

const estiloSecundario = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 6,
  padding: '8px 14px',
  border: '1px solid var(--border)',
  borderRadius: 'var(--radius-control)',
  background: 'var(--surface-lowest)',
  color: 'var(--text)',
  fontSize: 13,
  fontWeight: 500,
  cursor: 'pointer',
} as const;

const estiloPrimario = {
  ...estiloSecundario,
  background: 'var(--primary)',
  borderColor: 'var(--primary)',
  color: 'var(--text-inverse)',
} as const;

function fechaCorta(iso: string): string {
  if (!iso) return '—';
  return new Date(iso).toLocaleDateString('es-CO');
}

export function DocumentosTab({ activoId }: { activoId: number }) {
  const qc = useQueryClient();
  const inputRef = useRef<HTMLInputElement>(null);
  const [nombre, setNombre] = useState('');
  const [tipo, setTipo] = useState('OTRO');
  const [descripcion, setDescripcion] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [aEliminar, setAEliminar] = useState<Documento | null>(null);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['documentos', 'activo', activoId],
    queryFn: () => documentosApi.list({ activo: activoId, page_size: 100 }),
  });

  const subir = useMutation({
    mutationFn: (form: FormData) => documentosApi.create(form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['documentos'] });
      setNombre('');
      setTipo('OTRO');
      setDescripcion('');
      setFile(null);
      if (inputRef.current) inputRef.current.value = '';
      setMensaje('Documento subido correctamente.');
      setError('');
    },
    onError: (e: any) => {
      const dataErr = e?.response?.data;
      const campos = dataErr?.errors?.map((x: any) => x.message).join(' ');
      const primero =
        dataErr && typeof dataErr === 'object'
          ? Object.values(dataErr)
              .flat()
              .filter((v) => typeof v === 'string')
              .join(' ')
          : '';
      setMensaje('');
      setError(campos || primero || dataErr?.detail || 'No se pudo subir el documento.');
    },
  });

  const eliminar = useMutation({
    mutationFn: (id: number) => documentosApi.remove(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['documentos'] });
      setAEliminar(null);
    },
    onError: (e: any) =>
      setError(e?.response?.data?.detail || 'No se pudo eliminar el documento.'),
  });

  const enviar = () => {
    setError('');
    setMensaje('');
    if (!file) {
      setError('Selecciona un archivo.');
      return;
    }
    const extension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
    if (!EXTENSIONES.includes(extension)) {
      setError('Tipo de archivo no permitido. Usa PDF, imágenes, Word, Excel o TXT.');
      return;
    }
    if (file.size > MAX_BYTES) {
      setError('El archivo supera el tamaño máximo de 10 MB.');
      return;
    }
    const form = new FormData();
    form.append('activo', String(activoId));
    form.append('nombre', nombre.trim() || file.name);
    form.append('tipo', tipo);
    form.append('descripcion', descripcion);
    form.append('archivo', file);
    subir.mutate(form);
  };

  const descargar = async (doc: Documento) => {
    setError('');
    try {
      const blob = await documentosApi.descargar(doc.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = doc.archivo_nombre ?? doc.nombre;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'No se pudo descargar el documento.');
    }
  };

  const documentos = data?.results ?? [];

  const columnas: DataTableColumn<Documento>[] = [
    {
      key: 'nombre',
      header: 'Documento',
      render: (d) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <FileText size={16} style={{ color: 'var(--text-muted)' }} />
          <div>
            <div style={{ fontWeight: 500 }}>{d.nombre}</div>
            {d.descripcion && (
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{d.descripcion}</div>
            )}
          </div>
        </div>
      ),
    },
    {
      key: 'tipo',
      header: 'Tipo',
      render: (d) => (
        <StatusBadge variant="neutral" dot={false}>
          {d.tipo_etiqueta}
        </StatusBadge>
      ),
    },
    { key: 'fecha', header: 'Subido', render: (d) => fechaCorta(d.created_at) },
    { key: 'autor', header: 'Por', render: (d) => d.subido_por_nombre },
    {
      key: 'acciones',
      header: 'Acciones',
      render: (d) => (
        <div style={{ display: 'flex', gap: 12 }}>
          <button
            type="button"
            onClick={() => descargar(d)}
            style={{ display: 'inline-flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', color: 'var(--primary)', fontSize: 13, cursor: 'pointer', padding: 0 }}
          >
            <Download size={14} /> Descargar
          </button>
          <button
            type="button"
            onClick={() => setAEliminar(d)}
            style={{ display: 'inline-flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', color: 'var(--danger-fg)', fontSize: 13, cursor: 'pointer', padding: 0 }}
          >
            <Trash2 size={14} /> Eliminar
          </button>
        </div>
      ),
    },
  ];

  return (
    <FormSection
      title="Documentos"
      description="Facturas, manuales, garantías, contratos y evidencias asociadas al activo."
    >
      <form
        onSubmit={(e) => {
          e.preventDefault();
          enviar();
        }}
        style={{
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-card)',
          padding: 16,
          marginBottom: 16,
          background: 'var(--surface-low)',
          display: 'flex',
          flexDirection: 'column',
          gap: 12,
        }}
      >
        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text)' }}>Subir documento</div>
        <FormField label="Archivo" htmlFor="doc_archivo" required>
          <input
            id="doc_archivo"
            ref={inputRef}
            type="file"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            accept={EXTENSIONES.join(',')}
            style={{ width: '100%', fontSize: 13 }}
          />
        </FormField>
        <FormField label="Nombre" htmlFor="doc_nombre">
          <input
            id="doc_nombre"
            value={nombre}
            onChange={(e) => setNombre(e.target.value)}
            placeholder="Por defecto, el nombre del archivo"
            style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
          />
        </FormField>
        <FormField label="Tipo" htmlFor="doc_tipo">
          <select
            id="doc_tipo"
            value={tipo}
            onChange={(e) => setTipo(e.target.value)}
            style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
          >
            {TIPOS.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </FormField>
        <FormField label="Descripción" htmlFor="doc_descripcion">
          <textarea
            id="doc_descripcion"
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            style={{ width: '100%', padding: 8, border: '1px solid var(--border)', borderRadius: 6 }}
          />
        </FormField>
        {error && (
          <div role="alert" style={{ color: 'var(--danger-fg)', fontSize: 13 }}>
            {error}
          </div>
        )}
        {mensaje && (
          <div role="status" style={{ color: 'var(--success-fg)', fontSize: 13 }}>
            {mensaje}
          </div>
        )}
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button type="submit" disabled={subir.isPending} style={estiloPrimario}>
            <Upload size={14} /> {subir.isPending ? 'Subiendo…' : 'Subir documento'}
          </button>
        </div>
      </form>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          {documentos.length} documento{documentos.length === 1 ? '' : 's'}
        </span>
      </div>

      {isLoading ? (
        <LoadingSkeleton lines={4} />
      ) : isError ? (
        <ErrorState message="No se pudieron cargar los documentos." onRetry={() => refetch()} />
      ) : (
        <DataTable
          columns={columnas}
          data={documentos}
          rowKey={(d) => d.id}
          emptyState={
            <EmptyState
              icon={<FileText size={32} />}
              title="Sin documentos"
              description="Sube facturas, manuales, garantías o evidencias de este activo con el formulario de arriba."
            />
          }
        />
      )}

      <ConfirmDialog
        open={aEliminar !== null}
        title="Eliminar documento"
        description={`¿Eliminar "${aEliminar?.nombre ?? ''}"? Esta acción no se puede deshacer.`}
        confirmLabel="Eliminar"
        destructive
        onConfirm={() => aEliminar && eliminar.mutate(aEliminar.id)}
        onCancel={() => setAEliminar(null)}
      />
    </FormSection>
  );
}
