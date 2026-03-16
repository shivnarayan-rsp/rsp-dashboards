// RSP Dashboard — Auth Gate
// SHA-256 hash of the password is checked against stored session token.
// To change the password: update PASSWORD_HASH below with a new SHA-256 hash.
// Generate one at: https://emn178.github.io/online-tools/sha256.html
//
// Current password hash corresponds to: change this password before deploying
// Replace PASSWORD_HASH with your own hash.

const PASSWORD_HASH = '850abe090d258c3cc63a7ea7e945c95e849108279ff0d60a0d0e8bd79a8aa29e';
const SESSION_KEY   = 'rsp_auth';

(function () {
  const token = sessionStorage.getItem(SESSION_KEY);
  if (token !== PASSWORD_HASH) {
    // Save the page they were trying to reach so we can redirect back after login
    sessionStorage.setItem('rsp_redirect', window.location.pathname);
    window.location.replace('login.html');
  }
})();
