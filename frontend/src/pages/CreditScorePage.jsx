export default function CreditScorePage({ onNavigate }) {
  return (
    <>
      <h1>Credit Score</h1>
      <p>Your score is <strong>742</strong>. Nice Work!</p>
      <button data-nav="/" onClick={() => onNavigate('/')}>{'<- Back home'}</button>
    </>
  );
}
