const express = require("express");
const http = require("http");
const cors = require("cors");
const { Server } = require("socket.io");

const app = express();
app.use(cors());

const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: "*",
  },
});

io.on("connection", (socket) => {
  console.log("User connected:", socket.id);

  // Join a room
  socket.on("join_room", (room) => {
    const normalizedRoom = room.trim().toLowerCase();
    socket.join(normalizedRoom);
    console.log(`User ${socket.id} joined room ${normalizedRoom}`);
  });

  // Send message to the room only
  socket.on("send_message", (data) => {
    const room = data.room?.trim().toLowerCase();
    if (room) {
      io.to(room).emit("receive_message", data);
    }
  });

  socket.on("disconnect", () => {
    console.log("User disconnected:", socket.id);
  });
});

server.listen(3001, () => console.log("Server running on port 3001"));