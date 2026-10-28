import { useEffect, useState } from 'react';
import CustomerLoginPage from './pages/CustomerLoginPage.jsx';
import TellerLoginPage from './pages/TellerLoginPage.jsx';
import HomePage from './pages/HomePage.jsx';
import TellerHomePage from './pages/TellerHomePage.jsx';
import BalancePage from './pages/BalancePage.jsx';
import TellerBalancePage from './pages/TellerBalancePage.jsx';
import StatementPage from './pages/StatementPage.jsx';
import TellerStatementPage from './pages/TellerStatementPage.jsx';
import LoanPage from './pages/LoanPage.jsx';
import TellerLoanPage from './pages/LoanPage.jsx';

// Each route has its own page skeleton; layout and markup live in src/pages/.
const routes = {
  '/customerLogin': CustomerLoginPage,
  '/tellerLogin': TellerLoginPage,
  '/': HomePage,
  '/tellerHome': TellerHomePage,
  '/balance': BalancePage,
  '/tellerBalances': TellerBalancePage,
  '/statement': StatementPage,
  '/tellerStatements': TellerStatementPage,
  '/userLoans': LoanPage,
  '/tellerLoans': TellerLoanPage,
};

export default function App() {
  const [path, setPath] = useState(window.location.pathname);
  const [user, setUser] = useState('');
  const [loginResult, setLoginResult] = useState('');
  const isLoginPage = path === '/customerLogin' || path === '/tellerLogin';
  const activePath = !user && !isLoginPage ? '/customerLogin' : path;

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

  function submitLogin(event) {
    event.preventDefault();
    const employee = activePath === '/tellerLogin';
    const prefix = employee ? 't' : 'c';
    const fields = new FormData(event.currentTarget);
    const username = fields.get(`${prefix}Username`);
    const password = fields.get(`${prefix}Password`);

    // TODO: Replace temporary frontend client auth with backend authentication.
    if (
      username === 'Customer' && password === 'cPassword123' &&
      (!employee || fields.get('employeeId') === '00')
    ) {
      setUser(username);
      navigate('/');
    } else {
      setLoginResult('Login failed due to incorrect login credentials');
    }
    if (
      username === 'Teller' && password === 'tPassword123' &&
      (!employee || fields.get('employeeId') === '01')
    ) {
      setUser(username);
      navigate('/tellerHome');
    } else {
      setLoginResult('Login failed due to incorrect login credentials');
    }
    if (
      username === 'Admin' && password === 'aPassword123' &&
      (!employee || fields.get('employeeId') === '00')
    ) {
      setUser(username);
      navigate('/tellerHome');
    } else {
      setLoginResult('Login failed due to incorrect login credentials');
    }
  }

  function logout() {
    setUser('');
    navigate('/customerLogin');
  }

  const Page = Object.hasOwn(routes, activePath) ? routes[activePath] : HomePage;

  return (
    <Page
      key={activePath}
      user={user}
      loginResult={loginResult}
      onSubmit={submitLogin}
      onNavigate={navigate}
      onLogout={logout}
    />
  );
}
