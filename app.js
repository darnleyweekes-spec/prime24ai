const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('#site-nav');
menu?.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  nav.classList.toggle('open', open);
});
nav?.addEventListener('click', event => {
  if (event.target.closest('a')) {
    nav.classList.remove('open');
    menu.setAttribute('aria-expanded', 'false');
  }
});
const year = document.querySelector('#year');
if (year) year.textContent = new Date().getFullYear();
const form = document.querySelector('#inquiry-form');
const status = document.querySelector('#form-status');
if (form) form.querySelector('.compose-options').hidden = false;
form?.addEventListener('submit', async event => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const data = Object.fromEntries(new FormData(form));
  const recipient = 'darnley.weekes@gmail.com';
  const subject = `Prime24AI workflow inquiry — ${data.name}`;
  const body = `Name: ${data.name}\nEmail: ${data.email}\nBusiness: ${data.business || 'Not provided'}\n\nWorkflow:\n${data.message}`;
  const method = event.submitter?.value;
  if (method === 'copy') {
    try {
      await navigator.clipboard.writeText(`To: ${recipient}\nSubject: ${subject}\n\n${body}`);
      status.textContent = 'Message copied. Paste it into an email to ' + recipient + '.';
    } catch {
      status.textContent = 'Clipboard access was unavailable. Choose an email option to open your draft.';
    }
    return;
  }
  const query = `subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  status.textContent = 'Review your draft and send it from your email provider.';
  window.location.href = method === 'gmail'
    ? `https://mail.google.com/mail/?view=cm&fs=1&to=${encodeURIComponent(recipient)}&su=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
    : `mailto:${recipient}?${query}`;
});
