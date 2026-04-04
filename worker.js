// ---------- Insert Your Data ---------- //

const BOT_TOKEN = "8613353608:AAF43Ri5n5CoMa2YWKzHpeIeSzv5d9dOHvg"; // Insert your bot token.
const BOT_WEBHOOK = "/endpoint"; // Let it be as it is.
const BOT_SECRET = "nY7kQ2_ZmP4xA9vLwRt8HcD1uE6sF3Jb"; // Insert a powerful secret text (only [A-Z, a-z, 0-9, _, -] are allowed).
const BOT_OWNER = 8014518098; // Insert your telegram account id.
const BOT_CHANNEL = -1003813217467; // Insert your telegram channel id which the bot is admin in.
const SIA_SECRET = "Xq8LzR5_Ty9VbC2mKp7WnE4hA6uDsJf0"; // Insert a powerful secret text and keep it safe.
const PUBLIC_BOT = false; // Make your bot public (only [true, false] are allowed).

// ---------- Do Not Modify ---------- //

addEventListener("fetch", event => {
  event.respondWith(handleRequest(event));
});

// ---------- Main Handler ---------- //

async function handleRequest(event) {
  const url = new URL(event.request.url);
  const file = url.searchParams.get("file");

  if (url.pathname === BOT_WEBHOOK) return Bot.handleWebhook(event);
  if (url.pathname === "/registerWebhook") return Bot.registerWebhook(url);

  if (!file) return new Response("Missing file", { status: 400 });

  let message_id;

  try {
    message_id = await Cryptic.deHash(file);
  } catch {
    return new Response("Invalid link", { status: 400 });
  }

  const data = await Bot.getMessage(BOT_CHANNEL, message_id);

  if (!data) {
    return new Response("File not found", { status: 404 });
  }

  let file_id;

  if (data.document) file_id = data.document.file_id;
  else if (data.video) file_id = data.video.file_id;
  else if (data.audio) file_id = data.audio.file_id;
  else if (data.photo) file_id = data.photo[data.photo.length - 1].file_id;
  else return new Response("Unsupported file", { status: 400 });

  const fileInfo = await Bot.getFile(file_id);

  // 🔥 FIX: Redirect (NO SIZE LIMIT)
  const fileUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${fileInfo.file_path}`;
  return Response.redirect(fileUrl, 302);
}

// ---------- Cryptic ---------- //

class Cryptic {
  static async Hash(text) {
    return btoa(text + "_secure");
  }

  static async deHash(hash) {
    const decoded = atob(hash);
    return decoded.replace("_secure", "");
  }
}

// ---------- Telegram Bot ---------- //

class Bot {
  static async handleWebhook(event) {
    if (
      event.request.headers.get("X-Telegram-Bot-Api-Secret-Token") !== BOT_SECRET
    ) {
      return new Response("Unauthorized", { status: 403 });
    }

    const update = await event.request.json();

    if (update.message) {
      await onMessage(update.message);
    }

    return new Response("OK");
  }

  static async registerWebhook(url) {
    const webhook = `${url.origin}${BOT_WEBHOOK}`;
    const res = await fetch(
      `https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${webhook}&secret_token=${BOT_SECRET}`
    );
    return new Response(await res.text());
  }

  static async sendMessage(chat_id, text) {
    return fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id, text })
    });
  }

  static async sendDocument(chat_id, file_id) {
    return fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendDocument`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id, document: file_id })
    });
  }

  // 🔥 IMPORTANT FIX (works for all files)
  static async getMessage(chat_id, message_id) {
    const res = await fetch(
      `https://api.telegram.org/bot${BOT_TOKEN}/forwardMessage?chat_id=${chat_id}&from_chat_id=${chat_id}&message_id=${message_id}`
    );
    return (await res.json()).result;
  }

  static async getFile(file_id) {
    const res = await fetch(
      `https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${file_id}`
    );
    return (await res.json()).result;
  }
}

// ---------- Message Handler ---------- //

async function onMessage(message) {
  if (message.chat.id.toString().includes("-100")) return;

  let file_id;
  let file_name = "file";

  if (message.document) {
    file_id = message.document.file_id;
    file_name = message.document.file_name;
  } else if (message.video) {
    file_id = message.video.file_id;
    file_name = "video.mp4";
  } else if (message.photo) {
    file_id = message.photo[message.photo.length - 1].file_id;
    file_name = "image.jpg";
  } else {
    return Bot.sendMessage(message.chat.id, "Send a file.");
  }

  const save = await Bot.sendDocument(BOT_CHANNEL, file_id);
  const data = await save.json();

  if (!data.ok) {
    return Bot.sendMessage(message.chat.id, "Upload failed.");
  }

  const msg_id = data.result.message_id;
  const hash = await Cryptic.Hash(msg_id);

  const link = `https://file-to-link.tube872007.workers.dev/?file=${hash}`;

  return Bot.sendMessage(
    message.chat.id,
    `✅ File stored\n📁 ${file_name}\n🔗 ${link}`
  );
}
