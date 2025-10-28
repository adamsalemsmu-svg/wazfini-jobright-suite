import './globals.css';
import { Providers } from '@/lib/providers';
import { notFound } from 'next/navigation';
import type { ReactNode } from 'react';
import { NextIntlClientProvider, createTranslator } from 'next-intl/client';

export const metadata = {
  title: 'Wazifni',
};

export default async function RootLayout({ children, params }: { children: ReactNode; params: { locale?: string } }) {
  const locale = params?.locale ?? process.env.NEXT_PUBLIC_DEFAULT_LOCALE ?? 'en';
  let messages;
  try {
    messages = (await import(`../messages/${locale}.json`)).default;
  } catch (e) {
    notFound();
  }

  return (
    <html lang={locale} dir={locale === 'ar' ? 'rtl' : 'ltr'}>
      <body>
        <NextIntlClientProvider locale={locale} messages={messages}>
          <Providers>{children}</Providers>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
