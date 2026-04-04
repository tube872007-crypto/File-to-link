// ---------- Insert Your Data ---------- //

const BOT_TOKEN = "8613353608:AAF43Ri5n5CoMa2YWKzHpeIeSzv5d9dOHvg"; // Insert your bot token.
const BOT_WEBHOOK = "/endpoint"; // Let it be as it is.
const BOT_SECRET = "nY7kQ2_ZmP4xA9vLwRt8HcD1uE6sF3Jb"; // Insert a powerful secret text (only [A-Z, a-z, 0-9, _, -] are allowed).
const BOT_OWNER = 8014518098; // Insert your telegram account id.
const BOT_CHANNEL = -1003813217467; // Insert your telegram channel id which the bot is admin in.
const SIA_SECRET = "Xq8LzR5_Ty9VbC2mKp7WnE4hA6uDsJf0"; // Insert a powerful secret text and keep it safe.
const PUBLIC_BOT = false; // Make your bot public (only [true, false] are allowed).

// ---------- Do Not Modify ---------- //

const WHITE_METHODS = ["GET", "POST", "HEAD"];
const HEADERS_ERRR = {'Access-Control-Allow-Origin': '*', 'content-type': 'application/json'};

// ---------- Event Listener ---------- //

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event))
});

async function handleRequest(event) {
    const url = new URL(event.request.url);
    const file = url.searchParams.get('file');

    if (url.pathname === BOT_WEBHOOK) return Bot.handleWebhook(event);
    if (url.pathname === '/registerWebhook') return Bot.registerWebhook(event, url, BOT_WEBHOOK, BOT_SECRET);
    if (url.pathname === '/getMe') return new Response(JSON.stringify(await Bot.getMe()), {headers: HEADERS_ERRR});

    if (!file) return new Response("Missing file", {status: 400});

    let message_id;
    try {
        message_id = await Cryptic.deHash(file);
    } catch {
        return new Response("Invalid hash", {status: 400});
    }

    const data = await Bot.editMessage(BOT_CHANNEL, message_id, "ping");
    if (data.error_code) return new Response(JSON.stringify(data), {headers: HEADERS_ERRR});

    let fID;
    if (data.document) fID = data.document.file_id;
    else if (data.video) fID = data.video.file_id;
    else if (data.audio) fID = data.audio.file_id;
    else if (data.photo) fID = data.photo[data.photo.length - 1].file_id;
    else return new Response("Unsupported file", {status: 400});

    const fileInfo = await Bot.getFile(fID);
    if (fileInfo.error_code) return new Response(JSON.stringify(fileInfo), {headers: HEADERS_ERRR});

    // 🔥 FIX: Redirect to Telegram (NO SIZE LIMIT)
    const fileUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${fileInfo.file_path}`;
    return Response.redirect(fileUrl, 302);
}

// ---------- Cryptic ---------- //

class Cryptic {
    static async Hash(text) {
        return btoa(text);
    }
    static async deHash(hash) {
        return atob(hash);
    }
}

// ---------- Telegram Bot ---------- //

class Bot {
    static async handleWebhook(event) {
        if (event.request.headers.get('X-Telegram-Bot-Api-Secret-Token') !== BOT_SECRET) {
            return new Response('Unauthorized', { status: 403 });
        }
        const update = await event.request.json();
        if (update.message) await onMessage(update.message);
        return new Response('OK');
    }

    static async registerWebhook(event, url, path, secret) {
        const webhook = `${url.origin}${path}`;
        const res = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/setWebhook?url=${webhook}&secret_token=${secret}`);
        return new Response(await res.text());
    }

    static async getMe() {
        const res = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/getMe`);
        return (await res.json()).result;
    }

    static async sendMessage(chat_id, text) {
        return fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({chat_id, text})
        });
    }

    static async sendDocument(chat_id, file_id) {
        return fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendDocument`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({chat_id, document: file_id})
        });
    }

    static async editMessage(chat_id, message_id, text) {
        const res = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/editMessageCaption?chat_id=${chat_id}&message_id=${message_id}&caption=${text}`);
        return (await res.json()).result;
    }

    static async getFile(file_id) {
        const res = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${file_id}`);
        return (await res.json()).result;
    }
}

// ---------- Message Handler ---------- //

async function onMessage(message) {

    if (message.chat.id.toString().includes("-100")) return;

    let fID, fName;

    if (message.document) {
        fID = message.document.file_id;
        fName = message.document.file_name;
    } else if (message.video) {
        fID = message.video.file_id;
        fName = "video.mp4";
    } else if (message.photo) {
        fID = message.photo[message.photo.length - 1].file_id;
        fName = "image.jpg";
    } else {
        return Bot.sendMessage(message.chat.id, "Send a file.");
    }

    const save = await Bot.sendDocument(BOT_CHANNEL, fID);
    const data = await save.json();

    if (!data.ok) return Bot.sendMessage(message.chat.id, "Upload failed");

    const hash = await Cryptic.Hash(data.result.message_id);
    const link = `https://fille-to-link.tube872007.workers.dev/?file=${hash}`;
    return Bot.sendMessage(message.chat.id, `✅ File stored\n🔗 ${link}`);
}
