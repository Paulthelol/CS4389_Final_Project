import { useEffect, useState } from 'react';
import CustomerLoginPage from './pages/Customer/CustomerLoginPage.jsx';
import EmployeeLoginPage from './pages/Employee/EmployeeLoginPage.jsx';
import HomePage from './pages/Customer/HomePage.jsx';
import EmployeeHomePage from './pages/Employee/EmployeeHomePage.jsx';
import BalancePage from './pages/Customer/BalancePage.jsx';
import EmployeeBalancePage from './pages/Employee/EmployeeBalancePage.jsx';
import StatementPage from './pages/Customer/StatementPage.jsx';
import EmployeeStatementPage from './pages/Employee/EmployeeStatementPage.jsx';
import LoanPage from './pages/Customer/LoanPage.jsx';
import EmployeeLoanPage from './pages/Customer/LoanPage.jsx';

// Each route has its own page skeleton; layout and markup live in src/pages/.
const routes = {
  '/customerLogin': CustomerLoginPage,
  '/employeeLogin': EmployeeLoginPage,
  '/': HomePage,
  '/employeeHome': EmployeeHomePage,
  '/balance': BalancePage,
  '/employeeBalances': EmployeeBalancePage,
  '/statement': StatementPage,
  '/employeeStatements': EmployeeStatementPage,
  '/userLoans': LoanPage,
  '/employeeLoans': EmployeeLoanPage,
};

export default function App() {
  const [path, setPath] = useState(window.location.pathname);
  const [user, setUser] = useState('');
  const [loginResult, setLoginResult] = useState('');
  const [sessionToken, setSessionToken] = useState(null);
  const isLoginPage = path === '/customerLogin';
  const isEmployeeLogin = path === '/employeeLogin';
  const activePath = !user && !isLoginPage && !isEmployeeLogin ? '/customerLogin' : path;

  useEffect(() => {
    // Replace guarded URLs so browser Back does not create extra history entries.
    if (window.location.pathname !== activePath) {
      window.history.replaceState({}, '', activePath);
    }
  }, [activePath, path]);

  useEffect(() => {
    const onPopState = () => {
      setPath(window.location.pathname);
      setLoginResult('');
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  function navigate(nextPath) {
    if (nextPath !== window.location.pathname) {
      window.history.pushState({}, '', nextPath);
    }
    setPath(nextPath);
    setLoginResult('');
  }

  async function submitLogin(event) {
    event.preventDefault();
    const isEmployee = activePath === '/employeeLogin';
    const form = event.currentTarget
    const fields = new FormData(form);
    const username = fields.get(isEmployee ? 'tUsername' : 'cUsername'); // this will probably be emails
    const password = fields.get(isEmployee ? 'tPassword' : 'cPassword');

    const endpoint = isEmployee ? '/auth/employees/login' : '/auth/customers/login';
    const body = isEmployee ? {username: username, password } : {email: username, password }; // employee login uses username, customer login uses email
    
    try 
    {
      const response = await fetch(endpoint, {                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
      });
      const data = await response.json();

      if (!response.ok) 
      {
        setLoginResult(data.error || 'Login failed due to incorrect login credentials');
        return;  
      }

    // data = message from backend, session token, expires at , employee or customer
      setUser(data.customer?.email ?? data.employee?.username ?? '');

      setSessionToken(data.session_token);
      navigate(isEmployee ? '/employeeHome' : '/');

  } catch (err){
    setLoginResult('Unable to reach Server')
    }
  }

  async function logout() {
    if(sessionToken)
    {
      try{
        await fetch('http://localhost:5000/auth/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${sessionToken}` },
        });
      }catch{/* ignore network errors on logout*/ }
    }
    setUser('');
    setSessionToken(null);
    navigate('/customerLogin');
  }

  const Page = Object.hasOwn(routes, activePath) ? routes[activePath] : HomePage;

  return (
    <Page
      key={activePath}
      user={user}
      seesionToken={sessionToken}
      loginResult={loginResult}
      onSubmit={submitLogin}
      onNavigate={navigate}
      onLogout={logout}
    />
  );
}
