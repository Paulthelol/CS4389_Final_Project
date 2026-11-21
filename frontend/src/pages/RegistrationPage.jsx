import { useState } from 'react';
import { apiRequest } from '../api.js';

export default function RegistrationPage({ registrationType, onNavigate }) {
  const isEmployee = registrationType === 'employees';
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [registered, setRegistered] = useState(false);

  async function register(event) {
    event.preventDefault();
    const fields = new FormData(event.currentTarget);
    setBusy(true);
    setMessage('');
    try {
      const data = await apiRequest(`/auth/${registrationType}/register`, {
        method: 'POST', body: Object.fromEntries(fields),
      });
      setRegistered(true);
      setMessage(`${data.message}. You can now log in.`);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>{isEmployee ? 'Employee' : 'Customer'} Registration</h1>
      <p>Use the one-time setup token provided by {isEmployee ? 'an administrator' : 'an employee'}.</p>
      {!registered && (
        <form onSubmit={register}>
          <fieldset disabled={busy}>
            <label htmlFor="registerIdentifier">{isEmployee ? 'Username' : 'Email'}:</label>
            <input id="registerIdentifier" name={isEmployee ? 'username' : 'email'} type={isEmployee ? 'text' : 'email'} maxLength={isEmployee ? 50 : 255} autoComplete="username" required /><br /><br />
            <label htmlFor="setupToken">Setup token:</label>
            <input id="setupToken" name="setup_token" type="password" autoComplete="off" required /><br /><br />
            <label htmlFor="registerPassword">Password:</label>
            <input id="registerPassword" name="password" type="password" minLength={8} maxLength={1024} autoComplete="new-password" required /><br /><br />
            <button type="submit">{busy ? 'Registering…' : 'Register'}</button>
          </fieldset>
        </form>
      )}
      <p role="status">{message}</p>
      <button onClick={() => onNavigate(isEmployee ? '/employeeLogin' : '/customerLogin')}>Back to login</button>
    </>
  );
}
