import { useState } from "react";
import ChatPage from "./components/ChatPage";
import Dashboard from "./components/Dashboard";
import "./App.css";

export default function App() {
  const [tab, setTab] = useState("chat");
  return (
    <div className="app">
      <header>
        <h1>Refund Support</h1>
        <nav>
          <button className={tab === "chat" ? "active" : ""} onClick={() => setTab("chat")}>Customer chat</button>
          <button className={tab === "admin" ? "active" : ""} onClick={() => setTab("admin")}>Support dashboard</button>
        </nav>
      </header>
      {tab === "chat" ? <ChatPage /> : <Dashboard />}
    </div>
  );
}