const ADMIN_PASSWORD = "videshi2026admin";
const STORAGE_KEY = "videshi-admin-auth";

export function isAdminAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return sessionStorage.getItem(STORAGE_KEY) === "true";
}

export function adminLogin(password: string): boolean {
  if (password === ADMIN_PASSWORD) {
    sessionStorage.setItem(STORAGE_KEY, "true");
    return true;
  }
  return false;
}

export function adminLogout(): void {
  sessionStorage.removeItem(STORAGE_KEY);
}
