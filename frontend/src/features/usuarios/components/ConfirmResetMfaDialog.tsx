import { ConfirmDialog } from '../../../components/shared/ConfirmDialog';

interface ConfirmResetMfaDialogProps {
  open: boolean;
  userName?: string;
  isLoading?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmResetMfaDialog({
  open,
  userName,
  isLoading,
  onConfirm,
  onCancel,
}: ConfirmResetMfaDialogProps) {
  return (
    <ConfirmDialog
      open={open}
      title="Resetear segundo factor (MFA)"
      description={
        userName
          ? `Se eliminará el dispositivo MFA de ${userName} y se revocarán sus sesiones activas. El usuario deberá configurarlo nuevamente al iniciar sesión.`
          : 'Se eliminará el dispositivo MFA del usuario y se revocarán sus sesiones activas.'
      }
      confirmLabel="Resetear MFA"
      destructive
      isLoading={isLoading}
      onConfirm={onConfirm}
      onCancel={onCancel}
    />
  );
}
