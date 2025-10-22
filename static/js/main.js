let socket = null;
let currentUser = null;
let currentEmail = null;
let isMod = false;

// Initialize socket and page
window.addEventListener("DOMContentLoaded", () => {
  socket = io({ transports: ['websocket'] });

  // Hide Dev Login button unless localStorage flag is set
  const devBtn = document.getElementById("devLoginBtn");
  const isRenee = localStorage.getItem("isRenee") === "true";
  if (!isRenee && devBtn) {
    devBtn.style.display = "none";
  }

  socket.on("connect", () => {
    console.log("Connected to server:", socket.id);
    restoreLogin();
  });

  socket.on("history", (history) => {
    document.getElementById("chatBox").innerHTML = "";
    history.forEach(renderMessage);
    scrollChat();
  });

  socket.on("message", (msg) => {
    console.log("Received:", msg);
    renderMessage(msg);
    scrollChat();

    const sender = msg.split(":")[0];
    const text = msg.split(":").slice(1).join(":").trim();

    if (isTabInactive() && sender !== currentUser) {
      showNotification(sender, text);
    }
  });

  document.getElementById("msgInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  if ("Notification" in window && Notification.permission !== "granted") {
    Notification.requestPermission().then(permission => {
      console.log("Notification permission:", permission);
    });
  }

  if (devBtn) devBtn.addEventListener("click", handleDevLogin);
});

// --- Google Login Handling ---
function handleGoogleLogin(response) {
  const token = response.credential;
  localStorage.setItem("googleToken", token);
  verifyToken(token);
}

function restoreLogin() {
  const token = localStorage.getItem("googleToken");

  // Only verify if token exists and isn't dev
  if (!token || token === "dev") return;

  verifyToken(token);
}

function verifyToken(token) {
  fetch("/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      currentUser = data.name;
      currentEmail = data.email;
      isMod = data.is_mod;

      const signin = document.querySelector(".g_id_signin");
      const onload = document.getElementById("g_id_onload");
      if (signin) signin.style.display = "none";
      if (onload) onload.style.display = "none";

      document.getElementById("accountInfo").textContent = `Logged in as: ${currentUser}`;
      if (isMod) document.getElementById("modPanel").style.display = "block";

      socket.emit("join", { token });
    } else {
      console.warn("Token invalid or banned:", data.error);
    }
  });
}

// --- Dev Login ---
function handleDevLogin() {
  fetch("/dev-login")
    .then(res => res.json())
    .then(data => {
      if (!data.success) throw new Error("Dev login failed");
      localStorage.setItem("googleToken", data.token);
      verifyToken(data.token);
    })
    .catch(err => {
      console.error("Dev login error:", err);
      alert("Dev login failed: " + err.message);
    });
}

// --- Sending Messages ---
function sendMessage() {
  const textEl = document.getElementById("msgInput");
  const text = textEl.value.trim();
  if (!text || !currentUser) return;

  socket.emit("message", {
    text,
    token: localStorage.getItem("googleToken")
  });

  textEl.value = "";
}

// --- Mod Actions ---
function banUser() {
  const email = document.getElementById("banInput").value.trim();
  if (!email || !currentUser) return;

  socket.emit("ban", {
    email,
    token: localStorage.getItem("googleToken")
  });

  document.getElementById("banInput").value = "";
}

// --- Rendering Messages ---
function renderMessage(msg) {
  const div = document.createElement("div");
  div.className = "message";

  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const safeMsg = msg.replace(urlRegex, url => {
    return `<a href="${url}" target="_blank" style="color:#3498db;text-decoration:underline;">${url}</a>`;
  });

  div.innerHTML = safeMsg;

  const replyBtn = document.createElement("button");
  replyBtn.textContent = "Reply";
  replyBtn.onclick = () => {
    const target = msg.split(":")[0];
    document.getElementById("msgInput").value = `@${target} `;
    document.getElementById("msgInput").focus();
  };

  div.appendChild(replyBtn);
  document.getElementById("chatBox").appendChild(div);
}

// --- Notifications ---
function showNotification(sender, text) {
  if (!("Notification" in window)) return;
  if (Notification.permission !== "granted") return;

  new Notification(`New message from ${sender}`, {
    body: text,
    icon: "https://chat.openai.com/favicon.ico"
  });
}

// --- Utilities ---
function scrollChat() {
  const chat = document.getElementById("chatBox");
  chat.scrollTop = chat.scrollHeight;
}

function isTabInactive() {
  return document.hidden;
}
alert('js loaded this is debug if you see this i messed up and forgot to remove')
