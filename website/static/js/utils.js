function loadTips() {
  fetch('/load-tips', {
    method: 'POST',
    body: JSON.stringify(),
  }).then((_res) => {
    window.location.href = '/admin';
  });
}
