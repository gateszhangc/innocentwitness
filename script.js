const topbar = document.querySelector("[data-topbar]");
const revealNodes = Array.from(document.querySelectorAll(".reveal"));
const yearNode = document.querySelector("#current-year");

const handleScroll = () => {
  if (!topbar) return;
  topbar.classList.toggle("is-scrolled", window.scrollY > 12);
};

const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  {
    rootMargin: "0px 0px -10% 0px",
    threshold: 0.12
  }
);

revealNodes.forEach((node) => revealObserver.observe(node));

if (yearNode) {
  yearNode.textContent = new Date().getFullYear();
}

window.addEventListener("scroll", handleScroll, { passive: true });
handleScroll();
