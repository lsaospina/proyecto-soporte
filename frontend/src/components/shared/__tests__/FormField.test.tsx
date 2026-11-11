import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { FormField } from '../FormField';

describe('FormField', () => {
  it('renders label and input correctly', () => {
    render(
      <FormField label="Correo" htmlFor="email-input">
        <input id="email-input" type="email" />
      </FormField>
    );
    expect(screen.getByText('Correo')).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('renders required indicator when required={true}', () => {
    render(
      <FormField label="Contraseña" required htmlFor="pwd-input">
        <input id="pwd-input" type="password" />
      </FormField>
    );
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('renders error message and applies role alert', () => {
    render(
      <FormField label="Correo" error="Correo no válido" htmlFor="email-input">
        <input id="email-input" type="email" />
      </FormField>
    );
    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent('Correo no válido');
  });

  it('renders help text when provided', () => {
    render(
      <FormField label="Código" helpText="6 dígitos" htmlFor="code-input">
        <input id="code-input" type="text" />
      </FormField>
    );
    expect(screen.getByText('6 dígitos')).toBeInTheDocument();
  });
});
