(function() {
    const chatWindow = document.getElementById("chat-window");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const micBtn = document.getElementById("mic-btn");

    // Retrieve or generate a unique user ID
    let userId = localStorage.getItem("userId");
    if (!userId) {
      userId = "user-" + Math.floor(Math.random() * 1000000);
      localStorage.setItem("userId", userId);
    }

    // Append message to chat window
    function appendMessage(content, sender) {
      const messageEl = document.createElement("div");
      messageEl.classList.add("message", sender === "user" ? "user-message" : "bot-message");
      messageEl.innerHTML = content;
      chatWindow.appendChild(messageEl);
      chatWindow.scrollTop = chatWindow.scrollHeight;

      // Speech synthesis for bot messages
      if (sender === "bot" && 'speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(content);
        speechSynthesis.speak(utterance);
      }
    }

    // Show spinner while waiting for response
    function showSpinner() {
      const spinnerEl = document.createElement("div");
      spinnerEl.classList.add("spinner-border", "text-success", "spinner");
      spinnerEl.setAttribute("role", "status");
      spinnerEl.innerHTML = '<span class="visually-hidden">Loading...</span>';
      chatWindow.appendChild(spinnerEl);
      chatWindow.scrollTop = chatWindow.scrollHeight;
      return spinnerEl;
    }

    // Send user message to server
    async function sendMessage() {
      const text = userInput.value.trim();
      if (!text) return;

      // Append user's message
      appendMessage(text, "user");
      userInput.value = "";
      const spinner = showSpinner();

      try {
        const response = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId, message: text })
        });
        const data = await response.json();
        chatWindow.removeChild(spinner);

        if (data.assistant) {
          appendMessage(data.assistant, "bot");
        } else if (data.error) {
          appendMessage("Error: " + data.error, "bot");
        }
      } catch (err) {
        chatWindow.removeChild(spinner);
        appendMessage("Error: " + err.message, "bot");
      }
    }

    // Event Listeners
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") sendMessage();
    });

    // Speech Recognition Setup
    let recognition;
    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";

      recognition.addEventListener("result", (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join("");
        userInput.value = transcript;
      });

      recognition.addEventListener("error", (event) => {
        console.error("Speech recognition error:", event.error);
      });
    } else {
      micBtn.style.display = "none";
    }

    micBtn.addEventListener("click", () => {
      if (recognition) {
        recognition.start();
      }
    });
})();
