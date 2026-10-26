const menuToggle = document.querySelector(".menu-toggle");
const navMenu = document.querySelector(".nav-menu");

if (menuToggle && navMenu) {
  const closeMenu = () => {
    menuToggle.setAttribute("aria-expanded", "false");
    menuToggle.setAttribute("aria-label", "Open navigation menu");
    navMenu.classList.remove("is-open");
    document.body.classList.remove("menu-open");
  };

  menuToggle.addEventListener("click", () => {
    const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!isOpen));
    menuToggle.setAttribute(
      "aria-label",
      isOpen ? "Open navigation menu" : "Close navigation menu",
    );
    navMenu.classList.toggle("is-open", !isOpen);
    document.body.classList.toggle("menu-open", !isOpen);
  });

  navMenu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menuToggle.getAttribute("aria-expanded") === "true") {
      closeMenu();
      menuToggle.focus();
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 640) closeMenu();
  });
}

const backToTop = document.querySelector(".back-to-top");
if (backToTop) {
  const updateBackToTop = () => {
    const isVisible = window.scrollY > 500;
    backToTop.classList.toggle("is-visible", isVisible);
    backToTop.inert = !isVisible;
  };
  window.addEventListener("scroll", updateBackToTop, { passive: true });
  updateBackToTop();
}

const projectDialog = document.querySelector("#project-dialog");
if (projectDialog instanceof HTMLDialogElement) {
  const title = projectDialog.querySelector("#project-dialog-title");
  const description = projectDialog.querySelector("#project-dialog-description");
  const tools = projectDialog.querySelector("#project-dialog-tools");
  const contactLink = projectDialog.querySelector('a[href="#contact"]');

  document.querySelectorAll("[data-project-title]").forEach((trigger) => {
    trigger.addEventListener("click", () => {
      if (!title || !description || !tools) return;
      title.textContent = trigger.dataset.projectTitle || "";
      description.textContent = trigger.dataset.projectDescription || "";
      tools.textContent = trigger.dataset.projectTools || "";
      projectDialog.showModal();
    });
  });

  projectDialog.addEventListener("click", (event) => {
    if (event.target === projectDialog) projectDialog.close();
  });

  contactLink?.addEventListener("click", () => projectDialog.close());
}

const contactForm = document.querySelector(".contact-form");
if (contactForm instanceof HTMLFormElement) {
  const submitButton = contactForm.querySelector(".form-submit");

  contactForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!(submitButton instanceof HTMLButtonElement)) return;

    const originalButtonContent = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.setAttribute("aria-busy", "true");
    submitButton.textContent = "Sending…";

    try {
      let response;
      try {
        response = await fetch(contactForm.action, {
          method: "POST",
          body: new FormData(contactForm),
          headers: { Accept: "text/html" },
        });
      } catch {
        let alert = contactForm.querySelector(".form-alert");
        if (!alert) {
          alert = document.createElement("div");
          contactForm.prepend(alert);
        }
        alert.className = "form-alert form-error";
        alert.setAttribute("role", "alert");
        alert.setAttribute("tabindex", "-1");
        alert.textContent =
          "We couldn’t reach the server. Check your connection and try again.";
        alert.focus();
        return;
      }

      const responseDocument = new DOMParser().parseFromString(
        await response.text(),
        "text/html",
      );
      const responseAlert = responseDocument.querySelector(".form-alert");
      const currentAlert = contactForm.querySelector(".form-alert");

      if (currentAlert) currentAlert.remove();

      if (responseAlert) {
        const alert = document.importNode(responseAlert, true);
        contactForm.prepend(alert);
        alert.focus();
      } else {
        const alert = document.createElement("div");
        alert.className = `form-alert ${response.ok ? "form-success" : "form-error"}`;
        alert.setAttribute("role", response.ok ? "status" : "alert");
        alert.setAttribute("tabindex", "-1");
        alert.textContent = response.ok
          ? "Your message was sent successfully."
          : "Your message could not be delivered. Please try again later.";
        contactForm.prepend(alert);
        alert.focus();
      }

      if (response.ok) contactForm.reset();
    } finally {
      submitButton.disabled = false;
      submitButton.removeAttribute("aria-busy");
      submitButton.innerHTML = originalButtonContent;
    }
  });
}
