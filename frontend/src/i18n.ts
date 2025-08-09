import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

i18n
  // load translations using http (default public/locales/{{lng}}/{{ns}}.json)
  // learn more: https://github.com/i18next/i18next-http-backend
  .use(Backend)
  // detect user language
  // learn more: https://github.com/i18next/i18next-browser-languagedetector
  .use(LanguageDetector)
  // pass the i18n instance to react-i18next.
  .use(initReactI18next)
  // init i18next
  // for all options read: https://www.i18next.com/overview/configuration-options
  .init({
    fallbackLng: 'en', // default language if the detected one is not available
    debug: true, // Set to false in production
    
    interpolation: {
      escapeValue: false, // not needed for React as it escapes by default
    },
    
    ns: ['translation'], // default namespace, you can add more if you have different sections
    defaultNS: 'translation',

    react: {
      useSuspense: false // Set to true if you implement React.Suspense
    }
  });

export default i18n;
