import { NextResponse } from "next/server";

import type {
  NextRequest,
} from "next/server";

export function middleware(
  request: NextRequest
) {
  const token =
    request.cookies.get(
      "swarmlead_token"
    );

  const isLogin =
    request.nextUrl.pathname ===
    "/login";

  if (!token && !isLogin) {
    return NextResponse.redirect(
      new URL(
        "/login",
        request.url
      )
    );
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/leads/:path*",
    "/tickets/:path*",
    "/workflows/:path*",
    "/tenants/:path*",
    "/outreach/:path*",
    "/settings/:path*",
  ],
};