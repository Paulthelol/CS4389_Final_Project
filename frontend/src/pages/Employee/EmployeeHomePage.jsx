export default function EmployeeHomePage({ user, onNavigate, onLogout }) {
  return (
    <>
      <h1>Hello employee {user}</h1>
      <h2>Welcome to Super Kewl Bank</h2><br></br>
      <p>Please choose an action</p> <br></br>
      <button data-nav="/employeeBalances" onClick={() => onNavigate('/employeeBalances')}>View Managed Customer's Balances</button><br></br>
      <button data-nav="/employeeStatements" onClick={() => onNavigate('/employeeStatements')}>View Customer Statements</button><br></br>
      <button data-nav="/employeeLoans" onClick={() => onNavigate('/employeeLoans')}>Manage Customer Loans</button><br></br>
      <button data-logout="" onClick={onLogout}>Log out?</button>
    </>
  );
}
