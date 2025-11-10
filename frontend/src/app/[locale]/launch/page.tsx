import Link from "next/link";
import { getTranslations } from "next-intl/server";

export const metadata = {
  title: "Wazifni Launch",
};

export default async function LaunchPage({ params }: { params: { locale: string } }) {
  const t = await getTranslations({ locale: params.locale, namespace: "Launch" });
  const year = new Date().getFullYear();

  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col gap-12 px-6 py-16">
      <header className="space-y-4">
        <p className="text-sm uppercase tracking-wide text-muted-foreground">{t("badge")}</p>
        <h1 className="text-4xl font-bold sm:text-5xl">{t("title")}</h1>
        <p className="max-w-2xl text-lg text-muted-foreground">{t("subtitle")}</p>
        <div className="flex flex-wrap gap-3">
          <Link
            href={`/${params.locale}/dashboard`}
            className="rounded-md bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:bg-primary/90"
          >
            {t("ctaDashboard")}
          </Link>
          <a
            href="https://cal.com/wazifni/demo"
            target="_blank"
            rel="noreferrer"
            className="rounded-md border border-border px-6 py-3 text-sm font-semibold hover:bg-muted"
          >
            {t("ctaDemo")}
          </a>
        </div>
      </header>

      <section className="grid gap-8 md:grid-cols-2">
        <div className="space-y-3 rounded-lg border bg-background p-6 shadow-sm">
          <h2 className="text-xl font-semibold">{t("sections.automation.title")}</h2>
          <p className="text-sm text-muted-foreground">{t("sections.automation.copy")}</p>
        </div>
        <div className="space-y-3 rounded-lg border bg-background p-6 shadow-sm">
          <h2 className="text-xl font-semibold">{t("sections.analytics.title")}</h2>
          <p className="text-sm text-muted-foreground">{t("sections.analytics.copy")}</p>
        </div>
        <div className="space-y-3 rounded-lg border bg-background p-6 shadow-sm">
          <h2 className="text-xl font-semibold">{t("sections.notifications.title")}</h2>
          <p className="text-sm text-muted-foreground">{t("sections.notifications.copy")}</p>
        </div>
        <div className="space-y-3 rounded-lg border bg-background p-6 shadow-sm">
          <h2 className="text-xl font-semibold">{t("sections.security.title")}</h2>
          <p className="text-sm text-muted-foreground">{t("sections.security.copy")}</p>
        </div>
      </section>

      <footer className="space-y-2 border-t pt-6 text-sm text-muted-foreground">
        <p>{t("footer.contact", { email: "launch@wazifni.ai" })}</p>
  <p>{t("footer.legal", { year })}</p>
      </footer>
    </main>
  );
}
