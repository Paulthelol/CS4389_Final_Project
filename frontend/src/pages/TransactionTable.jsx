const currency = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });

export default function TransactionTable({ transactions }) {
  if (transactions.length === 0) return <p>No transactions found.</p>;

  return (
    <table>
      <thead><tr><th>Transaction ID</th><th>Date</th><th>Amount</th></tr></thead>
      <tbody>{transactions.map(({ transaction_id, created_at, amount }) => (
        <tr key={transaction_id}>
          <td>{transaction_id}</td>
          <td><time dateTime={created_at}>{new Date(created_at).toLocaleDateString()}</time></td>
          <td>{currency.format(amount)}</td>
        </tr>
      ))}</tbody>
    </table>
  );
}
