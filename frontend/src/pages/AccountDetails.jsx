import { useState } from 'react';

export default function AccountDetails({ account, request, employee = false, onChange, onDelete }) {
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');

  async function update(event, reassign = false) {
    event.preventDefault();
    const fields = new FormData(event.currentTarget);
    setBusy(true);
    setMessage('');
    try {
      const data = await request(`/accounts/${account.account_id}${reassign ? '' : `/${fields.get('operation')}`}`, {
        method: reassign ? 'PUT' : 'POST',
        body: reassign ? { customer_id: Number(fields.get('customer_id')) } : { amount: fields.get('amount') },
      });
      onChange(data);
      setMessage(reassign ? 'Account customer updated.' : 'Balance updated.');
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!window.confirm(`Delete account ${account.account_id}? This cannot be undone.`)) return;
    setBusy(true);
    setMessage('');
    try {
      await request(`/accounts/${account.account_id}`, { method: 'DELETE' });
      onDelete(account.account_id);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section aria-label="Account details">
      <h2>Account {account.account_id}</h2>
      <p>Customer ID: {account.customer_id} · Account number: {account.account_number}</p>
      <p>Current balance: <strong>${account.balance}</strong></p>
      <form onSubmit={update}>
        <fieldset disabled={busy}>
          <legend>Deposit or withdraw</legend>
          <label htmlFor="operation">Operation:</label>
          <select id="operation" name="operation"><option value="deposit">Deposit</option><option value="withdraw">Withdraw</option></select>
          <label htmlFor="amount">Amount:</label>
          <input id="amount" name="amount" type="number" min="0.01" step="0.01" max="9999999999.99" required />
          <button type="submit">Update balance</button>
        </fieldset>
      </form>
      {employee && (
        <>
          <form onSubmit={event => update(event, true)}>
            <fieldset disabled={busy}>
              <legend>Reassign account</legend>
              <label htmlFor="accountCustomer">Customer ID:</label>
              <input id="accountCustomer" name="customer_id" type="number" min="1" step="1" max={Number.MAX_SAFE_INTEGER} defaultValue={account.customer_id} required />
              <button type="submit">Save customer association</button>
            </fieldset>
          </form>
          <button disabled={busy} onClick={remove}>Delete account</button>
        </>
      )}
      <p role="status">{message}</p>
    </section>
  );
}
