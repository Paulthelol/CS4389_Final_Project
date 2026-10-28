//The teller is able to see all the customer' balances **UNDER THEIR MANAGEMENT**

export default function TellerBalancePage({ onNavigate }) {
  return (
    <>
      <h1>Account Balance</h1><br></br>
      <button data-nav="/tellerHome" onClick={() => onNavigate('/tellerHome')}>{'<- Back home'}</button><br></br>
      <table>
        <thead>
          <tr>
            <th>Customer Name</th>
            <th>Account Number</th>
            <th>Balance</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>John Doe</td>
            <td>123456789</td>
            <td>$1,234.56</td>
          </tr>
          <tr>
            <td>Jane Smith</td>
            <td>987654321</td>
            <td>$2,345.67</td>
          </tr>
        </tbody>
      </table>
    </>
  );
}
