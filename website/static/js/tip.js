const csrfToken = document
  .querySelector('meta[name="csrf-token"]')
  .getAttribute('content');

class Tip {
  constructor(fixtureId, value) {
    this.fixtureId = fixtureId;
    this.value = value;
  }
}

let tips = new Array();

function tipSelected(button, enabled) {
  if (enabled !== 'true') return;

  const [_, fixtureId, value] = button.id.split('-');
  tips = tips.filter((t) => t.fixtureId !== fixtureId);
  tips.push(new Tip(fixtureId, value));

  document.getElementById('nav-bottom-button').classList.add('visible');
}

function tipButtonPressed() {
  fetch('/register-tips', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
    },
    body: JSON.stringify(tips),
  }).then((_res) => {
    tips = [];
    window.location.href = '/tip/register';
  });
}
