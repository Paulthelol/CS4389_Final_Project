export default function TellerLoginPage({ loginResult, onSubmit, onNavigate }) {
  return (
    <>
      <h1>Please Log in User</h1>
      <form id="tellerLoginForm" onSubmit={onSubmit}>
        <fieldset>
          <label htmlFor="tUsername">Username:</label>
          <input type="text" id="tUsername" name="tUsername" autoComplete="username" required /><br /><br />
          <label htmlFor="employeeId">Employee Id:</label>
          <input type="text" inputMode="numeric" id="employeeId" name="employeeId" required /><br /><br />
          <label htmlFor="tPassword">Password:</label>
          <input type="password" id="tPassword" name="tPassword" autoComplete="current-password" required /><br /><br />
          <input type="submit" value="Submit" /><br /><br />
          <p className="loginResult" role="status"><strong>{loginResult}</strong></p>
        </fieldset>
      </form>
      <footer>
        <button data-nav="/customerLogin" onClick={() => onNavigate('/customerLogin')}>Customer Login</button>
      </footer>
    </>
  );
}
