export default function HomePage({ user, onNavigate, onLogout }) {
  return (
    <>
      <h1>Hello {user}</h1>
      <h2>Welcome to Super Kewl Bank</h2>
      <p>Please choose an action</p>
      <button data-nav="/balance" onClick={() => onNavigate('/balance')}>View Current Balance </button><br /><br />
      <button data-nav="/statement" onClick={() => onNavigate('/statement')}>Account Statement</button><br /><br />
      <button data-nav="/userLoans" onClick={() => onNavigate('/userLoans')}>Manage Loans</button><br /><br />
      <button data-logout="" onClick={onLogout}>Log out?</button>
    </>
  );
}
