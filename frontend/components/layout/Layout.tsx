'use client';
import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useLocale, useTranslations } from 'next-intl';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/store';

export default function Layout({ children }: { children: React.ReactNode }) {
  const locale = useLocale();
  const t = useTranslations();
  const pathname = usePathname();
  const router = useRouter();
  const logout = useAuth((s) => s.logout);

  const switchLocale = () => {
    const next = locale === 'en' ? 'ar' : 'en';
    router.push(`/${next}${pathname}`);
  };

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 bg-slate-50 border-r p-4">
        <h2 className="text-xl font-bold">Wazifni</h2>
        <nav className="mt-6 flex flex-col gap-2">
          <Link href={`/${locale}/dashboard`} className="hover:underline">{t('Dashboard')}</Link>
        </nav>
        <div className="mt-6">
          <button onClick={switchLocale} className="text-sm text-sky-600">{locale === 'en' ? 'العربية' : 'English'}</button>
        </div>
      </aside>
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
