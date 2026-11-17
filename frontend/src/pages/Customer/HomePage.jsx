import { useEffect, useState } from 'react';

export default function HomePage({ user, request, onNavigate, onLogout }) {
  const [profile, setProfile] = useState(null);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    request(`/customers/${user.customer_id}`, { signal: controller.signal })
      .then(setProfile)
      .catch(error => { if (error.name !== 'AbortError') setMessage(error.message); });
    return () => controller.abort();
  }, [request, user.customer_id]);

  async function deleteProfile() {
    if (!window.confirm('Delete your customer profile? This cannot be undone.')) return;
    setBusy(true);
    try {
      await request(`/customers/${user.customer_id}`, { method: 'DELETE' });
      await onLogout();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Hello {profile ? `${profile.first_name} ${profile.last_name}` : user.email}</h1>
      <h2>Welcome to Super Kewl Bank</h2>
      {profile && <p>Customer ID: {profile.customer_id} · Email: {profile.email} · SSN: {profile.ssn}</p>}
      <p role="status">{message}</p>
      <button onClick={() => onNavigate('/balance')}>View account and manage funds</button><br /><br />
      <button onClick={onLogout}>Log out</button>
      <button disabled={busy || !profile} onClick={deleteProfile}>Delete my profile</button>
    </>
  );
}
