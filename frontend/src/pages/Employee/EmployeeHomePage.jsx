export default function EmployeeHomePage({ user, onNavigate, onLogout }) {
  return (
    <>
      <h1>Hello employee {user.username}</h1>
      <h2>Welcome to Super Kewl Bank</h2>
      <p>Role: {user.role}</p>
      <button onClick={() => onNavigate('/employeeBalances')}>Manage accounts and balances</button><br /><br />
      <button onClick={() => onNavigate('/customers')}>Manage customers and setup tokens</button><br /><br />
      <button onClick={() => onNavigate('/employees')}>{user.role === 'admin' ? 'Manage employees and invitations' : 'My employee profile'}</button><br /><br />
      <button onClick={onLogout}>Log out</button>
    </>
  );
}
