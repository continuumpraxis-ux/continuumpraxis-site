const menuBtn = document.getElementById("menu");
const navLinks = document.getElementById("nav-links");
menuBtn?.addEventListener("click", () => {
  const open = navLinks?.classList.toggle("open");
  menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
});

const form = document.getElementById("intake");
if (form) {
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    const body = [
      `Name: ${data.name || ""}`,
      `Email: ${data.email || ""}`,
      `Company: ${data.company || ""}`,
      `Need: ${data.need || ""}`,
      "",
      data.message || ""
    ].join("\n");
    const mailto = `mailto:continuumpraxismarketing@outlook.com?cc=continuumpraxis@gmail.com&subject=${encodeURIComponent("Continuum Praxis inquiry — " + (data.company || data.name || ""))}&body=${encodeURIComponent(body)}`;
    window.location.href = mailto;
    const status = document.getElementById("form-status");
    if (status) status.textContent = "Your email client should open with the brief filled in. If it does not, write directly to continuumpraxismarketing@outlook.com.";
  });
}
