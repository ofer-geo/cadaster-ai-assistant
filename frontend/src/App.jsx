import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useEffect, useRef, useState } from "react";
import MapPanel from "./MapPanel";
import "./App.css";

function getTextContent(children) {
  if (
    typeof children === "string" ||
    typeof children === "number"
  ) {
    return String(children);
  }

  if (Array.isArray(children)) {
    return children.map(getTextContent).join("");
  }

  if (children?.props?.children) {
    return getTextContent(children.props.children);
  }

  return "";
}

function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hello! Ask me anything about the cadastral data.",
    },
  ]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [geojson, setGeojson] = useState({
    type: "FeatureCollection",
    features: [],
  });
  const [mapTitle, setMapTitle] = useState("Current Parcels");
  const messagesEndRef = useRef(null);

  const [selectedParcel, setSelectedParcel] = useState(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isLoading]);

  useEffect(() => {
    async function loadCurrentParcels() {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/parcels/current/geojson"
        );

        if (!response.ok) {
          throw new Error("Failed to load parcels.");
        }

        const data = await response.json();
        setGeojson(data);
      } catch (error) {
        console.error(error);
      }
    }

    loadCurrentParcels();
  }, []);

  function focusParcel(parcelUid) {
    setSelectedParcel((currentSelection) => {
      if (currentSelection?.parcelUid === parcelUid) {
        return null;
      }

      return {
        parcelUid,
        requestId: Date.now(),
      };
    });
  }

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
    setSelectedParcel(null);

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

      if (data.geojson?.features?.length > 0) {
        setGeojson(data.geojson);

        setMapTitle(
          data.geojson.features.length === 1
            ? "Parcel Result"
            : "Query Results"
        );
      }

      console.log("Chat response:", data);

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

      <main className="main-layout">
        <section className="chat-panel">
          <div className="messages">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message ${message.role}`}
              >
                <span className="message-label">
                  {message.role === "user" ? "You" : "Assistant"}
                </span>
                <div className="message-content">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({ children }) => (
                        <div className="table-wrapper">
                          <table>{children}</table>
                        </div>
                      ),

                      td: ({ children }) => {
                        const cellText = getTextContent(children);

                        const parcelMatch = cellText.match(/\bPAR-\d+\b/i);

                        if (!parcelMatch) {
                          return <td>{children}</td>;
                        }

                        const parcelUid = parcelMatch[0].toUpperCase();

                        return (
                          <td>
                            <button
                              type="button"
                              className={
                                selectedParcel?.parcelUid === parcelUid
                                  ? "parcel-link selected"
                                  : "parcel-link"
                              }
                              onClick={() => focusParcel(parcelUid)}
                              title={`Zoom to ${parcelUid}`}
                            >
                              {children}
                            </button>
                          </td>
                        );
                      },
                    }}
                  >
                    {message.text}
                  </ReactMarkdown>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="message assistant">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
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
        </section>
        <section className="map-panel">
          <MapPanel
            geojson={geojson}
            title={mapTitle}
            selectedParcel={selectedParcel}
          />
        </section>
      </main>
    </div>
  );
}

export default App;