export default function BalancePage({ onNavigate }) {
  return (
    <>
      <h1>Account Balance</h1>
      <p>Your balance is <strong>$1,234.56</strong>. Keep up the good work!</p>
      <button data-nav="/" onClick={() => onNavigate('/')}>{'<- Back home'}</button>
    </>
  );
}
