export default function HomePage({ user, onNavigate, onLogout }) {
  return (
    <>
      <h1>Hello {user}</h1>
      <h2>Welcome to Super Kewl Bank</h2>
      <p>Please choose an action</p>
      <button data-nav="/credit" onClick={() => onNavigate('/credit')}>Credit Score</button>
      <button data-nav="/statement" onClick={() => onNavigate('/statement')}>Account Statement</button>
      <button data-nav="/other" onClick={() => onNavigate('/other')}>Other Stuff</button>
      <button data-logout="" onClick={onLogout}>Log out?</button>
    </>
  );
}
