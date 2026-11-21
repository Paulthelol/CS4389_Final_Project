import { useState } from 'react';
import AccountDetails from '../AccountDetails.jsx';

export default function BalancePage({ request, onNavigate }) {
  const [account, setAccount] = useState(null);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  async function lookup(event) {
    event.preventDefault();
    const fields = new FormData(event.currentTarget);
    setBusy(true);
    setMessage('');
    setAccount(null);
    try {
      setAccount(await request(`/accounts/${fields.get('account_id')}`));
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>My account</h1>
      <button onClick={() => onNavigate('/')}>Back home</button>
      <p>Enter the account ID provided by your bank.</p>
      <form onSubmit={lookup}>
        <fieldset disabled={busy}>
          <label htmlFor="accountId">Account ID:</label>
          <input id="accountId" name="account_id" type="number" min="1" step="1" max={Number.MAX_SAFE_INTEGER} required />
          <button type="submit">View account</button>
        </fieldset>
      </form>
      <p role="status">{message}</p>
      {account && <AccountDetails key={account.account_id} account={account} request={request} onChange={data => setAccount(current => current?.account_id === data.account_id ? data : current)} />}
    </>
  );
}
