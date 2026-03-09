import { redirect } from "next/navigation";

export default function Page() {
  /**
   * Function: Page
   * Description: Redirect legacy knowledge-base route to canonical knowledge route.
   * Parameters:
   * Returns:
   *   Never returns because redirect terminates rendering.
   */
  redirect("/knowledge");
}

