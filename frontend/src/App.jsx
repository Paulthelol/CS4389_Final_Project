import { useCallback, useEffect, useState } from 'react';
import { apiRequest } from './api.js';
import CustomerLoginPage from './pages/Customer/CustomerLoginPage.jsx';
import EmployeeLoginPage from './pages/Employee/EmployeeLoginPage.jsx';
import HomePage from './pages/Customer/HomePage.jsx';
import EmployeeHomePage from './pages/Employee/EmployeeHomePage.jsx';
import BalancePage from './pages/Customer/BalancePage.jsx';
import EmployeeBalancePage from './pages/Employee/EmployeeBalancePage.jsx';
import CustomersPage from './pages/Employee/CustomersPage.jsx';
import EmployeesPage from './pages/Employee/EmployeesPage.jsx';
import RegistrationPage from './pages/RegistrationPage.jsx';
import StatementPage from './pages/Customer/StatementPage.jsx';
import EmployeeStatementPage from './pages/Employee/EmployeeStatementPage.jsx';


const routes = {
  '/customerLogin': CustomerLoginPage,
  '/employeeLogin': EmployeeLoginPage,
  '/customerRegister': RegistrationPage,
  '/employeeRegister': RegistrationPage,
  '/': HomePage,
  '/employeeHome': EmployeeHomePage,
  '/balance': BalancePage,
  '/employeeBalances': EmployeeBalancePage,
  '/customers': CustomersPage,
  '/employees': EmployeesPage,
  '/statement': StatementPage,
  '/employeeStatements': EmployeeStatementPage
};
const publicPaths = ['/customerLogin', '/employeeLogin', '/customerRegister', '/employeeRegister'];
const employeePaths = ['/employeeHome', '/employeeBalances', '/customers', '/employees', '/employeeStatements'];

export default function App() {
  const [path, setPath] = useState(window.location.pathname);
  const [user, setUser] = useState(null);
  const [loginResult, setLoginResult] = useState('');
  const [sessionToken, setSessionToken] = useState(null);
  const homePath = user?.type === 'employee' ? '/employeeHome' : '/';
  let activePath = Object.hasOwn(routes, path) ? path : homePath;
  if (!sessionToken && !publicPaths.includes(activePath)) activePath = '/customerLogin';
  if (user && !publicPaths.includes(activePath)
      && employeePaths.includes(activePath) !== (user.type === 'employee')) {
    activePath = homePath;
  }

  useEffect(() => {
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

  const navigate = useCallback((nextPath) => {
    if (nextPath !== window.location.pathname) window.history.pushState({}, '', nextPath);
    setPath(nextPath);
    setLoginResult('');
  }, []);

  // Every protected page uses this function with the current session token.
  const request = useCallback(async (endpoint, options = {}) => {
    try {
      return await apiRequest(endpoint, { ...options, sessionToken });
    } catch (error) {
      if (error.status === 401) {
        setUser(null);
        setSessionToken(null);
        navigate('/customerLogin');
        setLoginResult('Your session expired. Please log in again.');
      }
      throw error;
    }
  }, [sessionToken, navigate]);

  async function submitLogin(event) {
    event.preventDefault();
    const isEmployee = activePath === '/employeeLogin';
    const fields = new FormData(event.currentTarget);
    const identifier = fields.get(isEmployee ? 'tUsername' : 'cEmail');
    const password = fields.get(isEmployee ? 'tPassword' : 'cPassword');
    try {
      const data = await apiRequest(`/auth/${isEmployee ? 'employees' : 'customers'}/login`, {
        method: 'POST',
        body: isEmployee ? { username: identifier, password } : { email: identifier, password },
      });
      setUser({ ...(isEmployee ? data.employee : data.customer), type: isEmployee ? 'employee' : 'customer' });
      setSessionToken(data.session_token);
      navigate(isEmployee ? '/employeeHome' : '/');
    } catch (error) {
      setLoginResult(error.message);
    }
  }

  async function logout() {
    let logoutFailed = false;
    if (sessionToken) {
      try {
        await apiRequest('/auth/logout', { method: 'POST', sessionToken });
      } catch {
        logoutFailed = true;
      }
    }
    setUser(null);
    setSessionToken(null);
    navigate('/customerLogin');
    if (logoutFailed) setLoginResult('Signed out in-browser, but the server session could not be ended.');
  }

  const Page = routes[activePath];
  return (
    <Page
      key={activePath}
      user={user}
      request={request}
      registrationType={activePath === '/employeeRegister' ? 'employees' : 'customers'}
      loginResult={loginResult}
      onSubmit={submitLogin}
      onNavigate={navigate}
      onLogout={logout}
      onUserChange={setUser}
    />
  );
}
