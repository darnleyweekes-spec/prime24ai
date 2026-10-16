const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('#site-nav');
menu.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  nav.classList.toggle('open', open);
});
nav.addEventListener('click', event => {
  if (event.target.closest('a')) {
    nav.classList.remove('open');
    menu.setAttribute('aria-expanded', 'false');
  }
});
document.querySelector('#year').textContent = new Date().getFullYear();
const form = document.querySelector('#inquiry-form');
const status = document.querySelector('#form-status');
form.addEventListener('submit', event => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const data = Object.fromEntries(new FormData(form));
  const subject = encodeURIComponent(`Prime24AI workflow inquiry — ${data.name}`);
  const body = encodeURIComponent(`Name: ${data.name}\nEmail: ${data.email}\nBusiness: ${data.business || 'Not provided'}\n\nWorkflow:\n${data.message}`);
  status.textContent = 'Gmail is opening. Review the prepared message and press Send there to deliver your inquiry.';
  window.location.href = `https://mail.google.com/mail/?view=cm&fs=1&to=darnley.weekes%40gmail.com&su=${subject}&body=${body}`;
});
