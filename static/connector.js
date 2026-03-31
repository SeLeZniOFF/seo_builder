// This is the main function which you need to connect on your lead form as a handler on submit event
function onLeadSubmit(form) {
  const firstName = getInputValueByName(form, "name");
  const lastName = getInputValueByName(form, "LastName");
  const email = getInputValueByName(form, "email");
  const phoneCode = getInputValueByName(form, "country_code");
  const geoCode = getInputValueByName(form, "country_name");
  const offerName = getInputValueByName(form, "offerName");
  const phoneInput = form.querySelector('input[name="search2"]');

  let phoneWithoutCode = "";

  if (window.phoneMask) {
    phoneWithoutCode = window.phoneMask.unmaskedValue || "";
  } else {
    const raw = getInputValueByName(form, "search2") || "";
    phoneWithoutCode = raw.replace(/\D/g, "");
  }

  if (phoneWithoutCode.length < 5 || phoneWithoutCode.length > 15) {
    if (phoneInput) {
      phoneInput.classList.add("error");
      phoneInput.setCustomValidity("Пожалуйста, введите корректный номер телефона.");
      phoneInput.reportValidity();
    }
    return false;
  } else {
    if (phoneInput) {
      phoneInput.classList.remove("error");
      phoneInput.setCustomValidity("");
    }
  }

  const phoneWithCode = `${phoneCode}${phoneWithoutCode}`;

  saveProfileToLocalStorage({
    firstName,
    lastName,
    email,
    phoneWithoutCode,
    phoneWithCode,
    phoneCode,
    geoCode,
    offerName,
  });

  // --- НАШ КОД ДЛЯ АНАЛИТИКИ В АДМИНКЕ ---
  // ТЕПЕРЬ БЕРЕМ РЕАЛЬНЫЙ ПОДДОМЕН (test.aigarant.pro -> test)
  const subdomain = window.location.hostname.split('.')[0];

  fetch('/api/save-lead/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
          subdomain: subdomain,
          firstName: firstName,
          phoneWithCode: phoneWithCode,
          email: email
      })
  }).then(() => {
      sendLead(); // Сначала отправляем лид в CRM
      redirectToSuccessPage(); // Затем делаем редирект на Спасибо
  }).catch(() => {
      sendLead(); // Даже если наша база недоступна, все равно пускаем лид в CRM
      redirectToSuccessPage();
  });
  // --- КОНЕЦ ДОБАВЛЕНИЯ ---
}


function getInputValueByName(form, name) {
  const input = form.querySelector(`[name="${name}"]`);
  return input ? input.value : null;
}

function iMask() {}

// Function to send lead data
function sendLead() {
  const profileData = getProfileFromLocalStorage();
  const subId = getSubId(); // suitable for keitaro

  const form = document.querySelector("form");

  console.log("SubID: ", subId);
  console.log("Profile Data: ", profileData);

  if (!profileData) {
    alert("No Profile Data Found");
    return;
  }

  const locationInfo = getLocationInfo();
  const url = new URL(window.location.href);
  const landingURL = url.origin.concat(url.pathname);
  const { affc, vtc, apiKey, domain } = getConfig();
  const subs = getSUBs();
  const utms = getUTMs();
  const offerSettings = getOfferSettings();

  const data = {
    affc,
    vtc,
    subId,
    funnel: offerSettings.name, // Set your landing name here
    lang: offerSettings.lang, // Set your landing language here
    landingLang: offerSettings.lang, // Set your landing language here
    landingURL,
    profile: {
      firstName: profileData.firstName,
      lastName: profileData.lastName,
      email: profileData.email,
      phone: profileData.phoneWithCode,
      password: "aA1E23135167&", // use static pasword or that user passed
    },
    ip: locationInfo.ip,
    geo: (profileData.geoCode ?? locationInfo.geo).toUpperCase(), // use form geo code, if not set use by IP
    ...subs,
    ...utms,
  };

  const xhr = new XMLHttpRequest();
  xhr.open("POST", `https://${domain}/api/external/integration/lead`, false);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.setRequestHeader("Access-Control-Allow-Origin", "*");
  xhr.send(JSON.stringify(data));

  handleResponse(data, xhr, url);
}

// Function to handle response and redirect
function handleResponse(data, xhr, url) {
  if (xhr.status > 200 && xhr.status < 300) {
    // Fire FB pixel event
    onloadTrigger("Lead");
    const response = JSON.parse(xhr.response);
    localStorage.removeItem("profile-data");
    // Redirect lead to autologin page
    if (response.redirectUrl) {
      window.location.href = response.redirectUrl;
    }
  } else {
    // Fire FB pixel event
    onloadTrigger("Lead");
    console.warn("Registration error: ", xhr.response);
    sendMessageToTelegram(data?.funnel, data, xhr.response);
  }
}

// Get all query params from URL
function getQueryParams() {
  const params = new URLSearchParams(window.location.search);
  return params.toString();
}

// Redirect user to thankyou page
function redirectToSuccessPage() {
  const successPagePath = "/thanks/"; // USE YOUR PATH
  const queryParams = getQueryParams();
  const newUrl = `${successPagePath}?${queryParams}`;
  window.location.href = newUrl;
}

// Save user data to Local Storage
function saveProfileToLocalStorage(data) {
  localStorage.setItem("profile-data", JSON.stringify(data));
}

// Get user data from Local Storage
function getProfileFromLocalStorage() {
  const data = localStorage.getItem("profile-data");
  return data ? JSON.parse(data) : null;
}

// Function to get configuration data OR use default for one hub-affiliate connection
function getConfig() {
  const url = new URL(window.location.href);
  const { searchParams } = url;
  return {
    vtc: "VT-HP8XSRMKVS6E7",
    affc: searchParams.get("affc") || "AFF-MPO5DORWVF", // you can set static or pass value via query string
    domain: "solution-direct.com", // set your company domain
  };
}

// Function for sending failures to telegram bot to be able to not to miss registration data
function sendMessageToTelegram(offer, data, response) {
  const TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN";
  const TELEGRAM_CHAT_ID = "TELEGRAM_BOT_CHAT_ID";

  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;

  const payload = {
    chat_id: TELEGRAM_CHAT_ID,
    parse_mode: "HTML",
    text: `<b>REGISTRATION FAILED:</b>\n
LEad transfer for <a href="${
      window.location.href
    }">offer ${offer}</a> has been failed.
<b>Transfer request:</b>\n<code>${
      data ? JSON.stringify(data) : "NO_DATA"
    }</code>\n\n
<b>Transfer response:</b>\n<code>${response}</code>\n\n
#leads #transfer_failed`,
  };

  // const xhr = new XMLHttpRequest();
  // xhr.open("POST", url, false);
  // xhr.setRequestHeader("Content-Type", "application/json");
  // xhr.send(JSON.stringify(payload));
}

// Function to parse SUB identifiers from URL query params
function getSUBs() {
  const url = new URL(window.location.href);
  const { searchParams } = url;
  const savedData = getProfileFromLocalStorage();
  const offerName = savedData?.offerName;
  return {
    subId_a: searchParams?.get("token") ?? offerName, // reserved for Token
    subId_b: searchParams?.get("pid") ?? null, // reserved for PixelId
    subId_c: searchParams?.get("sub3") ?? null, // you can set static or pass value via query string
    subId_d: searchParams?.get("sub4") ?? null, // you can set static or pass value via query string
    subId_e: searchParams?.get("sub5") ?? null, // you can set static or pass value via query string
    subId_f: searchParams?.get("sub6") ?? null, // you can set static or pass value via query string
  };
}

// Function to parse UTM identifiers from URL query params
function getOfferSettings() {
  const url = new URL(window.location.href);
  const { searchParams } = url;
  const landingName = localStorage.getItem("landingName");
  return {
    name: landingName ?? "NeralyxAI", // you can set static or pass value via query string
    lang: searchParams?.get("lang") ?? "es", // you can set static or pass value via query string
  };
}

// Function to parse UTM identifiers from URL query params
function getUTMs() {
  const url = new URL(window.location.href);
  const { searchParams } = url;
  return {
    utmId: searchParams?.get("utmId") ?? getFBPixel() ?? null, // you can set static or pass value via query string
    utmSource: searchParams?.get("utmSource") ?? null, // you can set static or pass value via query string
    utmCampaign: searchParams?.get("utmCampaign") ?? null, // you can set static or pass value via query string
    utmMedium: searchParams?.get("utmMedium") ?? null, // you can set static or pass value via query string
  };
}

// Function to get cookie value
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}

// Function to parse Click ID from URL query params or cookies
function getSubId() {
  const localSubId = localStorage.getItem("subid");
  if (localSubId && localSubId != "{subid}") {
    return localSubId;
  }

  var params = new URLSearchParams(window.location.search);
  if (!"{subid}".match("{")) {
    return "{subid}";
  }

  var clientSubid = '<?php echo isset($client) ? $client->getSubid() : "" ?>';
  if (clientSubid && !/>/.test(clientSubid)) {
    return clientSubid;
  }

  return (
    params.get("_subid") ||
    params.get("subid") ||
    getCookie("subid") ||
    getCookie("_subid") ||
    Date.now().toString()
  );
}

// Function to get user location info
function getLocationInfo() {
  const xhr = new XMLHttpRequest();
  xhr.open("GET", "https://ipinfo.io/json", false);
  xhr.send();

  if (xhr.status === 200) {
    const response = JSON.parse(xhr.responseText);
    const { ip, country } = response;
    return { ip, geo: country };
  } else {
    console.error("Error fetching user info:", xhr.status);
  }
}

// Function to get Facebook pixel parameter
function getFBPixel() {
  const url = new URL(window.location.href);
  return url.searchParams.get("pid"); // you can pass your FB pixel ID via query param
}

// Function to trigger FB pixel on onload event
function onloadTrigger(event) {
  const pid = getFBPixel();
  console.log(`HERE YOURS PID: ${pid}`);

  !(function (f, b, e, v, n, t, s) {
    if (f.fbq) return;
    n = f.fbq = function () {
      n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
    };
    if (!f._fbq) f._fbq = n;
    n.push = n;
    n.loaded = !0;
    n.version = "2.0";
    n.queue = [];
    t = b.createElement(e);
    t.async = !0;
    t.src = v;
    s = b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t, s);
  })(
    window,
    document,
    "script",
    "https://connect.facebook.net/en_US/fbevents.js",
  );
  fbq("init", pid);
  fbq("track", event);
}
