class Tip {
  constructor(fixtureId, value) {
    this.fixtureId = fixtureId;
    this.value = value;
  }
}

let tips = new Array();

function tipSelected(button, enabled) {
  if (enabled === 'true') {
    // Button ID format: tipbutton-<fixtureId>-<tip>
    let fixtureId = button.id.split('-')[1];
    let value = button.id.split('-')[2];
    let tip = new Tip(fixtureId, value);
    tips.push(tip);

    var bottomNav = document.getElementById('nav-bottom-button');
    bottomNav.classList.add('visible');
  }
}

function tipButtonPressed() {
  fetch('/register-tips', {
    method: 'POST',
    body: JSON.stringify(tips),
  }).then((_res) => {
    tips = [];
    window.location.href = '/tip/register';
  });
}
