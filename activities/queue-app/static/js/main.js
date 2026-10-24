// Served at /static/js/main.js and linked from templates/base.html.

const joinForm = document.getElementById("join-form_button");
if (joinForm) {
   //print("found join form")
   // ^ y ts opens my printer ;-;

  joinForm.addEventListener("submit", () => {
    const button = joinForm.querySelector("button[type=submit]");
    button.disabled = true;
    button.textContent = "Getting your ticket…";
  });
}
