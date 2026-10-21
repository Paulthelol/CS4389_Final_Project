export default function AccountStatementPage({ onNavigate }) {
  return (
    <>
      <h1>Account Statement</h1>
      <p>No current activity today</p>
      <button data-nav="/" onClick={() => onNavigate('/')}>{'<- Back home'}</button>
    </>
  );
}
