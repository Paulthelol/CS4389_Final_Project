import './style.css';

document.querySelector('#app').innerHTML = `
<header>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, intial-scale=1.0">
    <title> Main Teller </title>
</header>

<body>

    <h1>
        Hello
    </h1>
    <h2>
        Welcome to Super Kewl Bank
    </h2>
    <p>
        Please choose an action
    </p>
    <button id="CreditScrBtn">
        Credit Score
    </button>
    <button id = "AccountStateBtn">
        Account Statement
    </button>
    <button id="OtherBtn">
        Other Stuff
    </button>

</body>
`;

document.querySelector('#CreditScrBtn').addEventListener('click', () => {
  alert('Credit Score Button Already Pressed');
});
document.querySelector('#AccountStateBtn').addEventListener('click', () => {
  alert('Account Statement Button Already Pressed');
});
document.querySelector('#OtherBtn').addEventListener('click', () => {
  alert('Other Stuff Button Already Pressed');
});

//setupCounter(document.querySelector('#counter'))
