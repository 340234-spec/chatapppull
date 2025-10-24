let socket = io({ transports: ['websocket'] });
let targetUser = new URLSearchParams(window.location.search).get("user");
let currentUser = localStorage.getItem("userName") || "Anonymous";

document.getElementById("dmTarget").textContent = targetUser;

socket.on("connect", () => {
  const token = localStorage.getItem("googleToken");
  socket.emit("join", { token });
});

socket.on("message", msg => {
  if (msg.startsWith("[Private]") || msg.startsWith("[Private to")) {
    renderDM(msg);
  }
});

function sendPrivate() {
  const text = document.getElementById("dmInput").value.trim();
  if (!text || !targetUser) return;

  const token = localStorage.getItem("googleToken");
  socket.emit("private", {
    to: targetUser,
    text,
    from: currentUser,
    token
  });

  renderDM(`[Private to ${targetUser}] ${text}`);
  document.getElementById("dmInput").value = "";
}

function renderDM(msg) {
  const div = document.createElement("div");
  div.className = "dmMessage";
  div.textContent = msg;
  document.getElementById("dmBox").appendChild(div);
  document.getElementById("dmBox").scrollTop = document.getElementById("dmBox").scrollHeight;
}

function goBack() {
  window.location.href = "/";
}
