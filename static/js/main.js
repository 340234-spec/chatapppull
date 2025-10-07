// main.js
let socket = null;
let currentUser = null;
let currentEmail = null;
let isMod = false;

// Initialize socket and page
window.addEventListener("DOMContentLoaded", () => {
  socket = io({ transports: ['websocket'] });

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

  // Send message on Enter key
  document.getElementById("msgInput").addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  // Ask for notification permission
  if ("Notification" in window && Notification.permission !== "granted") {
    Notification.requestPermission().then(permission => {
      console.log("Notification permission:", permission);
    });
  }
});

// --- Google Login Handling ---
function handleGoogleLogin(response) {
  const token = response.credential;
  localStorage.setItem("googleToken", token);
  verifyToken(token);
}

function restoreLogin() {
  const token = localStorage.getItem("googleToken");
  if (token) verifyToken(token);
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

      document.querySelector(".g_id_signin").style.display = "none";
      document.getElementById("g_id_onload").style.display = "none";

      if (isMod) document.getElementById("modPanel").style.display = "block";

      document.getElementById("accountInfo").textContent = `Logged in as: ${currentUser}`;

      // Join chat
      socket.emit("join", { token });
    } else {
      console.warn("Token invalid or banned:", data.error);
    }
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
  div.textContent = msg;

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
    icon: "https://chat.openai.com/favicon.ico" // replace with your own icon if desired
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
