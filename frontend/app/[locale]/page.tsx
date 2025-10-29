// frontend/app/[locale]/page.tsx
import { redirect } from 'next/navigation';

type Props = {
  params: { locale: string };
};

export default function LocaleIndex({ params }: Props) {
  // Redirect /en or /ar to their login page (adjust if you want /dashboard)
  redirect(`/${params.locale}/login`);
}
