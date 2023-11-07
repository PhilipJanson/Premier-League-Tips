window.onload = function () {
  var id = document.getElementById('dateid').innerText.trim();

  var fixture = document.getElementById(id);
  fixture.scrollIntoView({
    alignToTop: true,
    block: 'center',
    behavior: 'smooth',
  });
};
