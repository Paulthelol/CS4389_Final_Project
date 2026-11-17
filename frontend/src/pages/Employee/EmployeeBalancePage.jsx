import { useEffect, useState } from 'react';
import AccountDetails from '../AccountDetails.jsx';

export default function EmployeeBalancePage({ request, onNavigate }) {
  const [accounts, setAccounts] = useState(null);
  const [selected, setSelected] = useState(null);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    request('/accounts', { signal: controller.signal }).then(setAccounts).catch(error => {
      if (error.name !== 'AbortError') { setMessage(error.message); setAccounts([]); }
    });
    return () => controller.abort();
  }, [request]);

  async function create(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const fields = new FormData(form);
    setBusy(true);
    setMessage('');
    try {
      const data = await request('/accounts', {
        method: 'POST', body: { customer_id: Number(fields.get('customer_id')), account_number: fields.get('account_number') },
      });
      setAccounts(current => [...(current ?? []), data]);
      setSelected(data);
      form.reset();
      setMessage('Account created.');
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function view(id) {
    setBusy(true);
    setMessage('');
    setSelected(null);
    try {
      setSelected(await request(`/accounts/${id}`));
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  function accountChanged(data) {
    setSelected(current => current?.account_id === data.account_id ? data : current);
    setAccounts(current => current.map(account => account.account_id === data.account_id ? data : account));
  }

  function accountDeleted(id) {
    setSelected(current => current?.account_id === id ? null : current);
    setAccounts(current => current.filter(account => account.account_id !== id));
    setMessage('Account deleted.');
  }

  return (
    <>
      <h1>Accounts and balances</h1>
      <button onClick={() => onNavigate('/employeeHome')}>Back home</button>
      <p role="status">{message}</p>
      <form onSubmit={create}>
        <fieldset disabled={busy || accounts === null}>
          <legend>Create account</legend>
          <label htmlFor="newAccountCustomer">Customer ID:</label>
          <input id="newAccountCustomer" name="customer_id" type="number" min="1" step="1" max={Number.MAX_SAFE_INTEGER} required />
          <label htmlFor="newAccountNumber">Account number:</label>
          <input id="newAccountNumber" name="account_number" maxLength={20} autoComplete="off" required />
          <button type="submit">Create account</button>
        </fieldset>
      </form>
      {selected && <AccountDetails key={selected.account_id} account={selected} request={request} employee onChange={accountChanged} onDelete={accountDeleted} />}
      {accounts === null ? <p>Loading accounts…</p> : accounts.length === 0 ? <p>No accounts found.</p> : (
        <table>
          <thead><tr><th>Account ID</th><th>Customer ID</th><th>Account number</th><th>Balance</th><th>Actions</th></tr></thead>
          <tbody>{accounts.map(account => (
            <tr key={account.account_id}>
              <td>{account.account_id}</td><td>{account.customer_id}</td><td>{account.account_number}</td><td>${account.balance}</td>
              <td><button disabled={busy} onClick={() => view(account.account_id)}>View account</button></td>
            </tr>
          ))}</tbody>
        </table>
      )}
    </>
  );
}
