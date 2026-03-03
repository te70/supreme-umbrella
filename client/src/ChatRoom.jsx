import React, { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";

const socket = io("http://server:3001");

export default function ChatRoom() {
  const [username, setUsername] = useState("");
  const [joined, setJoined] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [room, setRoom] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    socket.on("receive_message", (data) => {
      setMessages((prev) => [...prev, data]);
    });

    return () => socket.off("receive_message");
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const joinRoom = () => {
  if (room) {
    const normalizedRoom = room.trim().toLowerCase();
    socket.emit("join_room", normalizedRoom);
    setRoom(normalizedRoom);
    setJoined(true);
  }
};

  const sendMessage = () => {
    if (!message.trim()) return;

    const msgData = {
      id: Date.now(),
      username,
      room,
      message,
      time: new Date().toLocaleTimeString(),
    };

    socket.emit("send_message", msgData);
    setMessages((prev) => [...prev, msgData]);
    setMessage("");
  };

  if (!joined) {
    return (
      <div style={styles.center}>
        <div style={styles.card}>
          <h2>Join Chat Room</h2>
          <input
            placeholder="Enter room name"
            value={room}
            onChange={(e) => setRoom(e.target.value)}
            style={styles.input}
            />

            <button onClick={joinRoom} style={styles.button}>
            Join
            </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3>Realtime Chat</h3>
        <span>{username}</span>
      </div>

      <div style={styles.chatBox}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              ...styles.message,
              alignSelf:
                msg.username === username ? "flex-end" : "flex-start",
              background:
                msg.username === username ? "#4f46e5" : "#ffffff",
              color:
                msg.username === username ? "white" : "black",
            }}
          >
            <strong>{msg.username}</strong>
            <div>{msg.message}</div>
            <small>{msg.time}</small>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div style={styles.footer}>
        <input
          placeholder="Type message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          style={styles.input}
        />
        <button onClick={sendMessage} style={styles.button}>
          Send
        </button>
      </div>
    </div>
  );
}

const styles = {
  center: {
    display: "flex",
    height: "100vh",
    justifyContent: "center",
    alignItems: "center",
    background: "linear-gradient(135deg, #6366f1, #9333ea)",
  },
  card: {
    background: "white",
    padding: "2rem",
    borderRadius: "12px",
    width: "300px",
    textAlign: "center",
  },
  container: {
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    background: "#f3f4f6",
  },
  header: {
    padding: "1rem",
    background: "white",
    display: "flex",
    justifyContent: "space-between",
    borderBottom: "1px solid #ddd",
  },
  chatBox: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    padding: "1rem",
    gap: "0.5rem",
    overflowY: "auto",
  },
  message: {
    padding: "0.5rem 1rem",
    borderRadius: "12px",
    maxWidth: "60%",
  },
  footer: {
    display: "flex",
    padding: "1rem",
    background: "white",
    gap: "0.5rem",
  },
  input: {
    flex: 1,
    padding: "0.5rem",
  },
  button: {
    padding: "0.5rem 1rem",
    background: "#4f46e5",
    color: "white",
    border: "none",
    cursor: "pointer",
  },
};