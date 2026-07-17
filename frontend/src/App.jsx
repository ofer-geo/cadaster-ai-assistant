import { useState } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hello! Ask me anything about the cadastral data.",
    },
  ]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function sendMessage() {
    const trimmedInput = input.trim();

    if (!trimmedInput || isLoading) {
      return;
    }

    const userMessage = {
      role: "user",
      text: trimmedInput,
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
    ]);

    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: trimmedInput,
          thread_id: "frontend-conversation-1",
        }),
      });

      if (!response.ok) {
        throw new Error("The backend returned an error.");
      }

      const data = await response.json();

      const assistantMessage = {
        role: "assistant",
        text: data.answer,
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ]);
    } catch (error) {
      console.error(error);

      const errorMessage = {
        role: "assistant",
        text: "Sorry, I could not connect to the assistant.",
      };

      setMessages((currentMessages) => [
        ...currentMessages,
        errorMessage,
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Cadaster AI Assistant</h1>
        <p>Ask questions about parcels, applications, and cadastral data.</p>
      </header>

      <main className="chat-container">
        <div className="messages">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role}`}
            >
              <span className="message-label">
                {message.role === "user" ? "You" : "Assistant"}
              </span>

              <p>{message.text}</p>
            </div>
          ))}

          {isLoading && (
            <div className="message assistant">
              <span className="message-label">Assistant</span>
              <p>Thinking...</p>
            </div>
          )}
        </div>

        <div className="input-area">
          <input
            type="text"
            value={input}
            placeholder="Ask about a parcel..."
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />

          <button
            onClick={sendMessage}
            disabled={isLoading}
          >
            {isLoading ? "Sending..." : "Send"}
          </button>
        </div>
      </main>
    </div>
  );
}

export default App;