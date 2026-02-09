const activityEntries = [
  "Invoice captured via camera upload",
  "AI extracts items, quantities, and prices",
  "Clover inventory updates automatically",
  "Operators review only exceptions",
];

const activityLog = document.getElementById("activity-log");
const accuracyBar = document.getElementById("accuracy-bar");

const renderActivity = () => {
  activityLog.innerHTML = "";
  activityEntries.forEach((entry, index) => {
    const div = document.createElement("div");
    div.textContent = `${index + 1}. ${entry}`;
    activityLog.appendChild(div);
  });
};

renderActivity();
accuracyBar.style.width = "85%";

const scrollButtons = document.querySelectorAll("[data-scroll]");
scrollButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const target = document.querySelector(button.dataset.scroll);
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  });
});

const nav = document.querySelector(".nav");
const hamburger = document.querySelector(".hamburger");

hamburger.addEventListener("click", () => {
  nav.classList.toggle("open");
});
