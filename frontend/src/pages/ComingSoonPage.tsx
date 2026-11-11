import { Construction } from 'lucide-react';
import { PageHeader } from '../components/shared/PageHeader';
import { EmptyState } from '../components/shared/EmptyState';

interface ComingSoonPageProps {
  title: string;
}

export function ComingSoonPage({ title }: ComingSoonPageProps) {
  return (
    <div>
      <PageHeader title={title} />
      <EmptyState
        icon={<Construction size={48} />}
        title="Próximamente"
        description="Este módulo está en desarrollo y estará disponible en una próxima versión."
      />
    </div>
  );
}
