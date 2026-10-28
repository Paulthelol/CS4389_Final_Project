export default function TellerStatementPage({ onNavigate }) {
  return (
    <>
      <h1>Account Statement</h1>
      <p>No current activity today</p><br></br>
      <button data-nav="/tellerHome" onClick={() => onNavigate('/tellerHome')}>{'<- Back home'}</button><br></br>

      <table>
        <thead>
          <tr>
            <th>Customer Name</th>
            <th>Account Number</th>
            <th>Action</th>
            <th>Amount</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>John Doe</td>
            <td>123456789</td>
            <td>Deposit</td>
            <td>$1,234.56</td>
          </tr>
          <tr>
            <td>Jane Smith</td>
            <td>987654321</td>
            <td>Withdrawal</td>
            <td>$2,345.67</td>
          </tr>
        </tbody>
      </table>
    </>
  );
}
