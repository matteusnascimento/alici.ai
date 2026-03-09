import { redirect } from "next/navigation";

/**
 * Root route – always redirects to /dashboard.
 * In development (DEV_MODE=true on the backend), authentication is bypassed
 * and the dashboard loads immediately without requiring a login.
 * The login page remains available at /login for future use.
 */
export default function HomePage() {
  redirect("/dashboard");
}
