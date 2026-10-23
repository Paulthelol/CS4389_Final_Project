// The active application starts at src/main.jsx and does not import this file.
import '../src/style.css';

let isLogIn = false; // holds the state of the page for if the user is logged in or not
let correctU = 'Admin';
let correctP = 'cPassword123';
let correctId = '00';

let user = '';
let loginResult = '';

const routes = {
  '/customerLogin': () =>
    `
      <h1> Please Log in Customer</h1>
      <form id='customerLoginForm'>
        <fieldset>
          <label for="Username">Username:</label>
          <input type="text" id="cUsername" name="cUsername" required><br><br>
          <label for="Password">cPassword:</label>
          <input type="password" id="cPassword" name="cPassword" required><br><br>
          <input type="submit" value="Submit"> <br><br>
          <p class= "loginResult"> <strong>${loginResult}</strong> </p>
        </fieldset>
      </form>
      <footer> 
      <button data-nav="/tellerLogin"> Employee Login </button>
      </footer>
    `,

  '/tellerLogin': () =>
    `
      <h1> Please Log in User</h1>
      <form id='tellerLoginForm'>
        <fieldset>
          <label for="Username">Username:</label>
          <input type="text" id="tUsername" name="tUsername" required><br><br>
          <label for="employeeId">Employee Id:</label>
          <input type="text" inputmode="numeric" id="employeeId" name="employeeId" required><br><br>
          <label for="Password">Password:</label>
          <input type="password" id="tPassword" name="tPassword" required><br><br>
          <input type="submit" value="Submit"> <br><br>
          <p class="loginResult"> <strong>${loginResult}</strong> </p>
        </fieldset>
      </form>
      <footer> 
      <button data-nav="/customerLogin"> Customer Login </button>
      </footer>
    `,

  '/': () => `
        <h1>
            Hello ${user}
        </h1>
        <h2>
            Welcome to Super Kewl Bank
        </h2>
        <p>
            Please choose an action
        </p>
        <button data-nav="/credit"> Credit Score </button>
        <button data-nav = "/statement"> Account Statement </button>
        <button data-nav="/other"> Other Stuff </button>
        <button data-logout> Log out? </button>
    `,

  '/credit': () =>
    `
        <h1>Credit Score</h1>
        <p>Your score is <strong>742</strong>. Nice Work!</p>
        <button data-nav="/"><- Back home</button> 
        
    `,
  //<! button sends the user to / with is the home page>

  '/statement': () =>
    `
        <h1>Account Statement</h1>
        <p>No current activity today</p>
        <button data-nav="/"><- Back home</button> 
    `,

  '/other': () =>
    `
        <h1>Work in Progress</h1>
        <p><strong>Nothing here Yet</strong>. Nice Work!</p>
        <button data-nav="/"><- Back home</button> 
    `,
};

function navigate(path) {
  //navigates the content and updates urls
  // if path not define, go home ('/')
  if (!isLogIn && path !== '/customerLogin' && path !== '/tellerLogin') {
    // if not logged in and not already at the login page
    path = '/customerLogin';
  }
  const render = routes[path] || routes['/'];

  history.pushState({}, '', path); // updated url w/o reloading page
  document.querySelector('#app').innerHTML = render(); // injects new page into the #app

  attachNavHandlers(); //reattach click handlers to buttons
  attachLoginsHandlers();
  attachLogOutHandler(); //attched click handler for the logout btn
}

function attachLoginsHandlers() {
  attachLoginHandlers('customerLoginForm', 'cUsername', 'cPassword', null); // for the customer entries
  attachLoginHandlers(
    'tellerLoginForm',
    'tUsername',
    'tPassword',
    'employeeId'
  ); // for the teller entries
}

function attachNavHandlers() {
  //wires any elements (el) with data-nav to call navigate()
  document.querySelectorAll('[data-nav]').forEach((el) => {
    el.addEventListener('click', () => {
      navigate(el.dataset.nav);
    });
  });
}

function attachLogOutHandler() {
  const btn = document.querySelector('[data-logout]');
  if (!btn) return;

  btn.addEventListener('click', () => {
    //Resets all prior info
    isLogIn = false;
    user = '';
    loginResult = '';
    navigate('/customerLogin');
  });
}

function attachLoginHandlers(formId, usernameField, passwordField, employeeId) {
  //
  const form = document.querySelector(`#${formId}`); // form is the element form login form
  if (!form) return; // not on login page skip

  form.addEventListener('submit', (event) => {
    event.preventDefault(); //stops browser reload

    const username = form[usernameField].value;
    const password = form[passwordField].value;
    const eId = employeeId ? form[employeeId].value : null; // if employee id is null then eId = null

    console.log('Login Submitted');
    if (eId == null) {
      // for customer login

      if (correctU == username && correctP == password) {
        // change correct_ for database input
        isLogIn = true;
        loginResult = '';
        user = username;
        navigate('/');
      } // change if we want to give information away
      else {
        loginResult = 'Login failed due to Insufficent User Login Credituals';
        document.querySelector('.loginResult').textContent = loginResult;
      }
    } else {
      if (correctU == username && correctP == password && correctId == eId) {
        // change correct_ for database input
        isLogIn = true;
        loginResult = '';
        user = username;
        navigate('/');
      } // change if we want to give information away
      else {
        loginResult = 'Login failed due to Insufficent Login Credituals';
        document.querySelector('.loginResult').textContent = loginResult;
      }
    }
  });
}

window.addEventListener('popstate', () => {
  navigate(window.location.pathname); // boot renders whatever page the url is on
});

navigate(window.location.pathname); // boot renders whatever page the url is on
