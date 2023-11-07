const tips = new Map();

function tipSelected(button, enabled) {
  if (enabled === 'true') {
    id = button.id.split('-')[1];
    value = button.id.split('-')[2];
    tips.set(id, value);

    for (const [key, value] of tips) {
      console.log(`${key} = ${value}`);
    }

    var bottomNav = document.getElementById('nav-bottom-button');
    bottomNav.classList.add('visible');
  }
}

function tipButtonPressed() {
  fetch('/register-tips', {
    method: 'POST',
    body: JSON.stringify(Array.from(tips)),
  }).then((_res) => {
    window.location.href = '/tip/register';
  });
}
