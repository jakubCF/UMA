export const getCsrfToken = (): string | null => {
  const metaTag = document.querySelector('meta[name="csrf-token"]');
  if (metaTag && metaTag.getAttribute('content')) {
    return metaTag.getAttribute('content');
  }
  // If not in meta tag, check cookies (common for Django)
  const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
  if (cookieMatch && cookieMatch[1]) {
    return cookieMatch[1];
  }
  return null;
};