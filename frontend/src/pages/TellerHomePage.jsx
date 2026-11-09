export default function TellerHomePage({ user, onNavigate, onLogout }) {
  return (
    <>
      <h1>Hello Teller {user}</h1>
      <h2>Welcome to Super Kewl Bank</h2><br></br>
      <p>Please choose an action</p> <br></br>
      <button data-nav="/tellerBalances" onClick={() => onNavigate('/tellerBalances')}>View Managed Customer's Balances</button><br></br>
      <button data-nav="/tellerStatements" onClick={() => onNavigate('/tellerStatements')}>View Customer Statements</button><br></br>
      <button data-nav="/tellerLoans" onClick={() => onNavigate('/tellerLoans')}>Manage Customer Loans</button><br></br>
      <button data-logout="" onClick={onLogout}>Log out?</button>
    </>
  );
}
