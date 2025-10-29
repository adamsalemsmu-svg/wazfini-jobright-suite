import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import createMiddleware from 'next-intl/middleware';
import { routing } from '@/i18n/routing';

const nextIntlMiddleware = createMiddleware(routing);

export default function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  // Redirect `/` to default locale
  if (pathname === '/') {
    const url = req.nextUrl.clone();
    url.pathname = '/en/login'; // change if default locale differs
    return NextResponse.redirect(url);
  }

  // Redirect `/en` or `/ar` locale roots to login
  const match = pathname.match(/^\/(en|ar)\/?$/);
  if (match) {
    const url = req.nextUrl.clone();
    url.pathname = `/${match[1]}/login`;
    return NextResponse.redirect(url);
  }

  // Fallback to existing next-intl middleware
  return nextIntlMiddleware(req);
}

export const config = {
  matcher: ['/((?!api|_next|.*\\..*).*)'],
};
