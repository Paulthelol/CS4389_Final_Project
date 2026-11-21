import { useEffect, useState } from 'react';
import TransactionTable from '../TransactionTable.jsx';

export default function EmployeeStatementPage({ request, onNavigate }) {
  const [accounts, setAccounts] = useState(null);
  const [statement, setStatement] = useState(null);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    const options = { signal: controller.signal };
    Promise.all([request('/accounts', options), request('/customers', options)])
      .then(([accounts, customers]) => {
        const names = new Map(customers.map(({ customer_id, first_name, last_name }) => (
          [customer_id, `${first_name} ${last_name}`]
        )));
        setAccounts(accounts.map(account => ({ ...account, customerName: names.get(account.customer_id) })));
      }).catch(error => {
        if (error.name !== 'AbortError') setMessage(error.message);
      });
    return () => controller.abort();
  }, [request]);

  async function viewStatement(account) {
    setBusy(true);
    setMessage('');
    setStatement(null);
    try {
      const transactions = await request(`/accounts/${account.account_id}/transactions`);
      setStatement({ account, transactions });
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Account Statements</h1>
      <button onClick={() => onNavigate('/employeeHome')}>Back home</button>
      <p role="status">{busy ? 'Loading transactions…' : message}</p>
      {accounts === null && !message && <p>Loading accounts…</p>}
      {accounts?.length === 0 && <p>No accounts found.</p>}
      {accounts?.length > 0 && (
        <table>
          <thead><tr><th>Customer Name</th><th>Account ID</th><th>Account Number</th><th>View Statement</th></tr></thead>
          <tbody>{accounts.map(account => (
            <tr key={account.account_id}>
              <td>{account.customerName ?? `Customer ${account.customer_id}`}</td>
              <td>{account.account_id}</td>
              <td>{account.account_number}</td>
              <td><button disabled={busy} onClick={() => viewStatement(account)}>View statement</button></td>
            </tr>
          ))}</tbody>
        </table>
      )}
      {statement && <>
        <h2>Account {statement.account.account_id} · {statement.account.account_number}</h2>
        <TransactionTable transactions={statement.transactions} />
      </>}
    </>
  );
}
