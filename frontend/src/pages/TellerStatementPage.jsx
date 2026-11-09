// I was thinking that the view button causes a popup to appear with the statement for that customer. 

export default function TellerStatementPage({ onNavigate }) {
  return (
    <>
      <h1>Account Statement</h1><br></br>
      <button data-nav="/tellerHome" onClick={() => onNavigate('/tellerHome')}>{'<- Back home'}</button><br></br>
        
      <table>
        <thead>
          <tr>
            <th>Customer Name</th>
            <th>Account Number</th>
            <th>View Statement</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>John Doe</td>
            <td>123456789</td>
            <td><button>View</button></td>
          </tr>
          <tr>
            <td>Jane Smith</td>
            <td>987654321</td>
            <td><button>View</button></td>
          </tr>
        </tbody>
      </table>
    </>
  );
}
