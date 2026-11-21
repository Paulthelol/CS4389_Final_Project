import { useState } from 'react';
import TransactionTable from '../TransactionTable.jsx';

export default function StatementPage({ request, onNavigate }) {
  const [statement, setStatement] = useState(null);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  async function viewStatement(event) {
    event.preventDefault();
    const accountId = Number(new FormData(event.currentTarget).get('account_id'));
    setBusy(true);
    setMessage('');
    setStatement(null);
    try {
      const transactions = await request(`/accounts/${accountId}/transactions`);
      setStatement({ accountId, transactions });
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Account Statement</h1>
      <button onClick={() => onNavigate('/')}>Back home</button>
      <form onSubmit={viewStatement}>
        <fieldset disabled={busy}>
          <label htmlFor="statementAccountId">Account ID:</label>
          <input id="statementAccountId" name="account_id" type="number" min="1" step="1" max={Number.MAX_SAFE_INTEGER} required />
          <button type="submit">View statement</button>
        </fieldset>
      </form>
      <p role="status">{busy ? 'Loading transactions…' : message}</p>
      {statement && <>
        <h2>Account {statement.accountId}</h2>
        <TransactionTable transactions={statement.transactions} />
      </>}
    </>
  );
}
