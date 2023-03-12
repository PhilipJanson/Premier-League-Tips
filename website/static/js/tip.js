const tips = new Map();

window.onload = function () {
  var id = document.getElementById('dateid').innerText.trim();

  var fixture = document.getElementById(id);
  fixture.scrollIntoView({
    alignToTop: true,
    block: 'center',
    behavior: 'smooth',
  });
};

function tipSelected(button, enabled) {
  if (enabled == 'true') {
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
