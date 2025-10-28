import { defaultLocale } from "@/i18n/config";
import { redirect } from "next/navigation";

export default function Home() {
  redirect(`/${defaultLocale}`);
  return null;
}
