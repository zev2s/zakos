
export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/telegram" && request.method === "POST") {
      if (
        request.headers.get("X-Telegram-Bot-Api-Secret-Token") !==
        env.WEBHOOK_SECRET
      ) {
        return new Response("Forbidden", { status: 403 });
      }

      const update = await request.json();
      const msg = update.message;

      if (!msg || !msg.from || msg.chat.type !== "private") {
        return new Response("OK");
      }

      const userId = String(msg.from.id);
      const adminId = String(env.ADMIN_ID);
      const text = msg.text || "";

      async function send(chatId, message, extra = {}) {
        return fetch(
          `https://api.telegram.org/bot${env.BOT_TOKEN}/sendMessage`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              chat_id: chatId,
              text: message,
              ...extra
            })
          }
        );
      }

      if (userId === adminId) {
        if (msg.reply_to_message && text) {
          const match = (
            msg.reply_to_message.text || ""
          ).match(/User ID: (\d+)/);

          if (match) {
            await send(
              match[1],
              "✉️ Ответ администратора:\n\n" + text
            );
            await send(adminId, "✅ Ответ отправлен!");
          }
        }

        return new Response("OK");
      }

      if (msg.from.is_bot) return new Response("OK");

      if (text === "/start") {
        await send(
          userId,
          "Привет! Напиши сообщение, и я передам его администратору."
        );
        return new Response("OK");
      }

      if (!text) {
        await send(userId, "Пожалуйста, отправляй текстовые сообщения.");
        return new Response("OK");
      }

      const username = msg.from.username
        ? "@" + msg.from.username
        : "Не указан";

      await send(
        adminId,
        "📩 НОВОЕ СООБЩЕНИЕ\n\n" +
        "👤 Username: " + username + "\n" +
        "🆔 User ID: " + userId + "\n\n" +
        "💬 " + text,
        { reply_markup: { force_reply: true } }
      );

      await send(userId, "✅ Сообщение отправлено!");

      return new Response("OK");
    }

    return new Response("Bot is running!");
  }
};
