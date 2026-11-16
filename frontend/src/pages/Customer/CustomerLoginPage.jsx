export default function CustomerLoginPage({ loginResult, onSubmit, onNavigate }) {
  return (
    <>
      <h1>Please Log in Customer</h1>
      <form id="customerLoginForm" onSubmit={onSubmit}>
        <fieldset>
          <label htmlFor="cUsername">Username:</label>
          <input type="text" id="cUsername" name="cUsername" autoComplete="username" required /><br /><br />
          <label htmlFor="cPassword">Password:</label>
          <input type="password" id="cPassword" name="cPassword" autoComplete="current-password" required /><br /><br />
          <input type="submit" value="Submit" /><br /><br />
          <p className="loginResult" role="status"><strong>{loginResult}</strong></p>
        </fieldset>
      </form>
      <footer>
        <button data-nav="/employeeLogin" onClick={() => onNavigate('/employeeLogin')}>Employee Login</button>
      </footer>
    </>
  );
}
