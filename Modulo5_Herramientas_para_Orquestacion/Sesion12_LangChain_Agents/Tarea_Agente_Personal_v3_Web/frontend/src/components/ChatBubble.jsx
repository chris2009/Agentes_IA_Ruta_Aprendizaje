import { Bot, User } from "lucide-react";

export default function ChatBubble({ role, content }) {
  const esUsuario = role === "user";

  return (
    <div className={`chat-bubble-row ${esUsuario ? "chat-row-user" : "chat-row-agent"}`}>
      <div className="chat-avatar">{esUsuario ? <User size={16} /> : <Bot size={16} />}</div>
      <div className={`chat-bubble ${esUsuario ? "chat-bubble-user" : "chat-bubble-agent"}`}>{content}</div>
    </div>
  );
}
