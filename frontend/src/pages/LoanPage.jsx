export default function LoanPage({ onNavigate }) {
  return (
    <>
      <h1>Make Your Loans (PROBS WON"T USE THIS T-T)</h1>
      <button data-nav="/" onClick={() => onNavigate('/')}>{'<- Back home'}</button>
      <table>
        <thead>
          <tr>
            <th>Loan Number/ID</th>
            <th>Date</th>
            <th>Amount</th>
            <th>Interest Rate</th>
            <th>Pay?</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>123457896</td>
            <td>2023-01-01</td>
            <td>$1,234.56</td>
            <td>5.5%</td>
            <td><button>Pay</button></td>
          </tr>
          <tr>
            <td>987564321</td>
            <td>2023-02-01</td>
            <td>$2,345.67</td>
            <td>6.0%</td>
            <td><button>Pay</button></td>
          </tr>
        </tbody>
      </table>
    </>
    
  );
}
