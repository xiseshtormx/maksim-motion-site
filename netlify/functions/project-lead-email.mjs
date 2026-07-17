const BRAND = {
  ink: "#0b0d0f",
  blue: "#0b477f",
  brightBlue: "#0e67b8",
  paper: "#f3efe5",
  muted: "#77746d",
  line: "#d7d1c5",
};

const asText = (value, maxLength = 4000) => String(value ?? "").trim().slice(0, maxLength);

const escapeHtml = (value) => asText(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");

const formatDate = (value) => {
  const source = asText(value, 32);
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(source);
  return match ? `${match[3]}.${match[2]}.${match[1]}` : source || "Не указан";
};

const isEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(asText(value, 320));

const normalizeLead = (data = {}) => ({
  name: asText(data.name, 160) || "Без имени",
  contact: asText(data.contact, 320) || "Не указан",
  format: asText(data["project-format"], 160) || "Не выбран",
  scope: asText(data["selected-scope"], 200) || "Не указан",
  budget: asText(data["estimated-budget"], 120) || "По договорённости",
  brief: asText(data.brief, 6000) || "Комментарий не заполнен",
  deadline: formatDate(data.deadline),
  recommendedDeadline: formatDate(data["recommended-deadline"]),
  quantity: asText(data["reels-quantity"], 20),
  minutes: asText(data["video-minutes"], 20),
});

const detailRow = (label, value) => `
  <tr>
    <td style="padding:0 0 7px;color:${BRAND.muted};font:700 11px/1.4 Arial,sans-serif;letter-spacing:.12em;text-transform:uppercase;">${escapeHtml(label)}</td>
  </tr>
  <tr>
    <td style="padding:0 0 22px;color:${BRAND.ink};font:600 17px/1.45 Arial,sans-serif;word-break:break-word;">${escapeHtml(value)}</td>
  </tr>`;

export const buildProjectEmail = (rawData = {}) => {
  const lead = normalizeLead(rawData);
  const receivedAt = new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "long",
    timeStyle: "short",
    timeZone: "Europe/Moscow",
  }).format(new Date());
  const volume = lead.quantity
    ? `${lead.quantity} рол.`
    : lead.minutes
      ? `${lead.minutes} мин.`
      : "Индивидуально";

  const html = `<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <meta name="color-scheme" content="light only" />
    <title>Новая заявка KAIROS</title>
    <style>
      @media (max-width:660px){
        .mail-shell{width:100%!important;border-radius:0!important}
        .mail-pad{padding-left:24px!important;padding-right:24px!important}
        .summary-cell{display:block!important;width:100%!important;padding:0 0 12px!important}
        .headline{font-size:38px!important}
      }
    </style>
  </head>
  <body style="margin:0;padding:0;background:#ded9cf;color:${BRAND.ink};">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;background:#ded9cf;">
      <tr>
        <td align="center" style="padding:32px 12px;">
          <table role="presentation" width="640" cellspacing="0" cellpadding="0" border="0" class="mail-shell" style="width:640px;max-width:100%;overflow:hidden;border:1px solid #cbc5b9;border-radius:28px;background:${BRAND.paper};box-shadow:0 20px 60px rgba(11,13,15,.14);">
            <tr>
              <td class="mail-pad" style="padding:36px 42px 42px;background:${BRAND.ink};color:${BRAND.paper};">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                  <tr>
                    <td style="font:800 19px/1 Arial,sans-serif;letter-spacing:.28em;">KAIROS</td>
                    <td align="right" style="color:#8e969e;font:700 10px/1.4 Arial,sans-serif;letter-spacing:.14em;">PROJECT / NEW</td>
                  </tr>
                </table>
                <div style="width:42px;height:4px;margin:36px 0 22px;border-radius:99px;background:${BRAND.brightBlue};"></div>
                <p style="margin:0 0 12px;color:#91a6ba;font:700 10px/1.4 Arial,sans-serif;letter-spacing:.16em;text-transform:uppercase;">Новая заявка · ${escapeHtml(receivedAt)}</p>
                <h1 class="headline" style="margin:0;max-width:520px;font:500 52px/.96 Arial,sans-serif;letter-spacing:-.055em;">${escapeHtml(lead.name)} хочет обсудить проект.</h1>
                <p style="margin:24px 0 0;color:#bac1c7;font:400 16px/1.55 Arial,sans-serif;">Контакт для ответа: <strong style="color:${BRAND.paper};font-weight:700;">${escapeHtml(lead.contact)}</strong></p>
              </td>
            </tr>
            <tr>
              <td class="mail-pad" style="padding:32px 42px 18px;background:${BRAND.blue};color:white;">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                  <tr>
                    <td class="summary-cell" width="42%" valign="top" style="padding-right:20px;">
                      <p style="margin:0 0 7px;color:#aac6df;font:700 10px/1.4 Arial,sans-serif;letter-spacing:.13em;text-transform:uppercase;">Формат</p>
                      <p style="margin:0;font:700 20px/1.25 Arial,sans-serif;">${escapeHtml(lead.format)}</p>
                    </td>
                    <td class="summary-cell" width="28%" valign="top" style="padding-right:20px;">
                      <p style="margin:0 0 7px;color:#aac6df;font:700 10px/1.4 Arial,sans-serif;letter-spacing:.13em;text-transform:uppercase;">Объём</p>
                      <p style="margin:0;font:700 20px/1.25 Arial,sans-serif;">${escapeHtml(volume)}</p>
                    </td>
                    <td class="summary-cell" width="30%" valign="top">
                      <p style="margin:0 0 7px;color:#aac6df;font:700 10px/1.4 Arial,sans-serif;letter-spacing:.13em;text-transform:uppercase;">Ориентир</p>
                      <p style="margin:0;font:700 20px/1.25 Arial,sans-serif;">${escapeHtml(lead.budget)}</p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
            <tr>
              <td class="mail-pad" style="padding:36px 42px 12px;background:${BRAND.paper};">
                <p style="margin:0 0 28px;color:${BRAND.blue};font:800 11px/1.4 Arial,sans-serif;letter-spacing:.15em;text-transform:uppercase;">01 / Бриф проекта</p>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                  ${detailRow("Что требуется", lead.scope)}
                  ${detailRow("Желаемый срок", lead.deadline)}
                  ${detailRow("Рекомендованный срок", lead.recommendedDeadline)}
                </table>
                <div style="margin:2px 0 30px;padding:24px;border:1px solid ${BRAND.line};border-radius:18px;background:#ebe7dd;">
                  <p style="margin:0 0 10px;color:${BRAND.muted};font:700 10px/1.4 Arial,sans-serif;letter-spacing:.13em;text-transform:uppercase;">Комментарий клиента</p>
                  <p style="margin:0;color:${BRAND.ink};font:500 17px/1.6 Arial,sans-serif;white-space:pre-wrap;word-break:break-word;">${escapeHtml(lead.brief)}</p>
                </div>
              </td>
            </tr>
            <tr>
              <td class="mail-pad" style="padding:24px 42px 34px;border-top:1px solid ${BRAND.line};background:${BRAND.paper};">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                  <tr>
                    <td valign="middle">
                      <p style="margin:0 0 5px;color:${BRAND.ink};font:800 14px/1.3 Arial,sans-serif;">KAIROS · Максим Рыжиков</p>
                      <p style="margin:0;color:${BRAND.muted};font:500 11px/1.5 Arial,sans-serif;">Заявка сохранена в Netlify Forms</p>
                    </td>
                    <td align="right" valign="middle">
                      <a href="https://kairos-motion-maxim.netlify.app/" style="display:inline-block;padding:12px 18px;border-radius:999px;background:${BRAND.ink};color:white;font:700 12px/1 Arial,sans-serif;text-decoration:none;">Открыть сайт ↗</a>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>`;

  const text = [
    "KAIROS — новая заявка",
    "",
    `Имя: ${lead.name}`,
    `Контакт: ${lead.contact}`,
    `Формат: ${lead.format}`,
    `Объём: ${volume}`,
    `Ориентир: ${lead.budget}`,
    `Что требуется: ${lead.scope}`,
    `Желаемый срок: ${lead.deadline}`,
    `Рекомендованный срок: ${lead.recommendedDeadline}`,
    "",
    "Комментарий:",
    lead.brief,
  ].join("\n");

  return {
    lead,
    html,
    text,
    subject: `Новая заявка KAIROS · ${lead.format} · ${lead.name}`,
  };
};

const sendEmail = async ({ html, text, subject, lead }) => {
  const apiKey = process.env.RESEND_API_KEY;
  const recipients = asText(process.env.KAIROS_LEADS_TO, 1000)
    .split(",")
    .map((email) => email.trim())
    .filter(Boolean);
  const from = asText(process.env.KAIROS_MAIL_FROM, 320) || "KAIROS <onboarding@resend.dev>";

  if (!apiKey || recipients.length === 0) {
    console.warn("[KAIROS] Email skipped: configure RESEND_API_KEY and KAIROS_LEADS_TO in Netlify.");
    return;
  }

  const payload = { from, to: recipients, subject, html, text };
  if (isEmail(lead.contact)) payload.reply_to = lead.contact;

  const response = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(`[KAIROS] Resend failed (${response.status}): ${message.slice(0, 500)}`);
  }
};

export default {
  async formSubmitted(event) {
    const data = event?.data ?? {};
    if (data["form-name"] && data["form-name"] !== "project-request") return;
    await sendEmail(buildProjectEmail(data));
  },
};
