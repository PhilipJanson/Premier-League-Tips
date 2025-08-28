function fetchApiData() {
  fetch('/admin/fetch-api-data', {
    method: 'POST',
  }).then((_res) => {
    tips = [];
    window.location.href = '/admin';
  });
}
