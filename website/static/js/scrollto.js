document.addEventListener('DOMContentLoaded', () => {
  const id = document.getElementById('next-fixture-id').innerText.trim();
  const fixture = document.getElementById(id);
  fixture.scrollIntoView({
    alignToTop: true,
    block: 'center',
    behavior: 'smooth',
  });
});
