let lastReply = "";
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const ttsBtn = document.getElementById("btn-tts");

sendBtn.addEventListener("click", async () => {
    const message = userInput.value.trim();
    if(!message) return;
    appendMessage("Tú", message);
    userInput.value = "";

    const res = await fetch("/api/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ userId: "user_" + Date.now(), message })
    });
    const data = await res.json();
    if(data.reply){
        lastReply = data.reply;
        appendMessage("May Roga", data.reply);
    } else if(data.error){
        appendMessage("Sistema", data.error);
    }
});

ttsBtn.addEventListener("click", () => {
    if(lastReply){
        const utterance = new SpeechSynthesisUtterance(lastReply);
        utterance.lang = "es-ES";
        speechSynthesis.speak(utterance);
    }
});

function appendMessage(user, message){
    const p = document.createElement("p");
    p.innerHTML = `<strong>${user}:</strong> ${message}`;
    chatBox.appendChild(p);
    chatBox.scrollTop = chatBox.scrollHeight;
}
