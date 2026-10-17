import './style.css';

const routes = {
  '/': () => `
        <h1>
            Hello
        </h1>
        <h2>
            Welcome to Super Kewl Bank
        </h2>
        <p>
            Please choose an action
        </p>
        <button data-nav="/credit">
            Credit Score
        </button>
        <button data-nav = "/statement">
            Account Statement
        </button>
        <button data-nav="/other">
            Other Stuff
        </button>
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
  const render = routes[path] || routes['/'];

  history.pushState({}, '', path); // updated url w/o reloading page

  document.querySelector('#app').innerHTML = render(); // injects new page into the #app

  attachNavHandlers(); //reattach click handlers to buttons
}

function attachNavHandlers() {
  //wires any elements (el) with data-nav to call navigate()
  document.querySelectorAll('[data-nav]').forEach((el) => {
    el.addEventListener('click', () => {
      navigate(el.dataset.nav);
    });
  });
}

window.addEventListener('popstate', () => {
  const path = window.location.pathname;
  const render = routes[path] || routes['/'];
  document.querySelector('#app').innerHTML = render();
  attachNavHandlers();
}); // handles the back and forth browers buttons

navigate(window.location.pathname); // boot renders whatever page the url is on
