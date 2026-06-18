const SESSION_KEY = "bit_mesra_session_id";

export const generateSessionId = (): string => {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  // Robust fallback UUID v4 generator
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

export const getSessionId = (): string => {
  let sessionId = localStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = generateSessionId();
    localStorage.setItem(SESSION_KEY, sessionId);
  }
  return sessionId;
};

export const resetSessionId = (): string => {
  const newSessionId = generateSessionId();
  localStorage.setItem(SESSION_KEY, newSessionId);
  return newSessionId;
};

export const clearSession = (): void => {
  localStorage.removeItem(SESSION_KEY);
};
