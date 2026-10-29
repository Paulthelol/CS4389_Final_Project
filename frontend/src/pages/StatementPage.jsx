export default function StatementPage({ onNavigate }) {
  return (
    <>
      <h1>Account Statement</h1><br></br>
      <button data-nav="/" onClick={() => onNavigate('/')}>{'<- Back home'}</button><br></br>
      <table>
        <thead>
          <tr>
            <th>Transaction ID</th>
            <th>Date</th>
            <th>Amount</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>123456789</td>
            <td>2023-01-01</td>
            <td>$1,234.56</td>
          </tr>
          <tr>
            <td>987654321</td>
            <td>2023-02-01</td>
            <td>$-2,345.67</td>
          </tr>
        </tbody>
      </table>
    </>
  );
}
