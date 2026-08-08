// config.js
// -----------
// One single place to point the mobile app at your backend.
//
// IMPORTANT (common beginner trap): "localhost" on a phone/emulator
// means the PHONE itself, not your laptop running Flask. You must use
// your computer's LAN IP address instead.
//
//   Windows : run `ipconfig`        -> look for IPv4 Address
//   Mac     : run `ipconfig getifaddr en0`
//   Linux   : run `hostname -I`
//
// Then replace the IP below, e.g. "http://192.168.1.42:5000"
// Android emulator only (not a real phone): "http://10.0.2.2:5000" works.

export const API_BASE_URL = "https://swab-effects-unfounded.ngrok-free.dev";
