// Booking Modal Dialog & Light-Dismiss Fallback (per modern-web-guidance `light-dismiss-a-dialog`)
const bookingDialog = document.getElementById('bookingDialog');
const bookingTopicSelect = document.getElementById('bookingTopic');

window.openBookingModal = (defaultTopic = 'Keynote / Conferencia Presencial o Global') => {
  if (bookingTopicSelect && defaultTopic) {
    bookingTopicSelect.value = defaultTopic;
  }
  bookingDialog.showModal();
};

if (bookingDialog && !('closedBy' in HTMLDialogElement.prototype)) {
  bookingDialog.addEventListener('click', (event) => {
    if (event.target !== bookingDialog) return;
    const rect = bookingDialog.getBoundingClientRect();
    const isDialogContent = (
      rect.top <= event.clientY &&
      event.clientY <= rect.top + rect.height &&
      rect.left <= event.clientX &&
      event.clientX <= rect.left + rect.width
    );
    if (isDialogContent) return;
    bookingDialog.close();
  });
}

// Direct Executive Inquiry via WhatsApp / Email
const bookingForm = document.getElementById('bookingForm');
if (bookingForm) {
  bookingForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('bookingName').value.trim();
    const org = document.getElementById('bookingOrg').value.trim();
    const topic = document.getElementById('bookingTopic').value;
    const details = document.getElementById('bookingDetails').value.trim();

    const msg = `Hola Edward, soy *${name}* (${org}). Me interesa conversar sobre: *${topic}*.\n\nDetalles: ${details}`;
    const waUrl = `https://wa.me/17865573119?text=${encodeURIComponent(msg)}`;
    window.open(waUrl, '_blank', 'noopener');
    bookingDialog.close();
  });
}
