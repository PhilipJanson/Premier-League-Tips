window.onload = function () {
  var id = document.getElementById('next-fixture-id').innerText.trim();

  var fixture = document.getElementById(id);
  fixture.scrollIntoView({
    alignToTop: true,
    block: 'center',
    behavior: 'smooth',
  });
};
