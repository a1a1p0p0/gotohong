export const DEFAULT_USER_ID = "local_user";

export function getUserId(): string {
  if (typeof window === "undefined") return DEFAULT_USER_ID;
  const existing = window.localStorage.getItem("wuxing_user_id");
  if (existing) return existing;
  window.localStorage.setItem("wuxing_user_id", DEFAULT_USER_ID);
  return DEFAULT_USER_ID;
}
