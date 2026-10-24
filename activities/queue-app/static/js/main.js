// Served at /static/js/main.js and linked from templates/base.html.

const joinForm = document.getElementById("join-form");
if (joinForm) {
  joinForm.addEventListener("submit", (event) => {
    if (!joinForm.reportValidity()) {
      event.preventDefault();
      return;
    }

    const submitButton = joinForm.querySelector('button[type="submit"]');
    if (submitButton.disabled) {
      event.preventDefault();
      return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Getting your ticket…";
  });
}
