document.addEventListener("DOMContentLoaded", () => {
    updateNavbar();
    bindLogoutButtons();
  });
  
  function updateNavbar() {
    const usernameEls = document.querySelectorAll(".nav-username");
    const username = getUsername();
    const loggedIn = !!getAccessToken();
    const admin = isAdmin();
  
    usernameEls.forEach(el => {
      el.textContent = username ? `Logged in as ${username}` : "Not logged in";
    });
  
    document.querySelectorAll(".nav-public").forEach(el => {
      el.classList.toggle("hidden", loggedIn);
    });
  
    document.querySelectorAll(".nav-auth").forEach(el => {
      el.classList.toggle("hidden", !loggedIn);
    });
  
    document.querySelectorAll(".logout-btn").forEach(el => {
      el.classList.toggle("hidden", !loggedIn);
    });
  
    document.querySelectorAll(".nav-admin").forEach(el => {
      el.classList.toggle("hidden", !(loggedIn && admin));
    });
  }
  
  function bindLogoutButtons() {
    const logoutBtns = document.querySelectorAll(".logout-btn");
  
    logoutBtns.forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        clearTokens();
        localStorage.removeItem("is_admin");
        window.location.href = "login.html";
      });
    });
  }