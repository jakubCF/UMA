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
    fallbackLng: 'en', // Default language if a specific one isn't found
    debug: true, // Keep this true during development for helpful console logs
    
    interpolation: {
      escapeValue: false,
    },
    
    ns: ['translation'], // Your default namespace
    defaultNS: 'translation',

    // --- CRITICAL CHANGE HERE ---
    // This tells i18next to only use the language part (e.g., 'cs' from 'cs-CZ')
    // when looking for translation files.
    load: 'languageOnly', 

    react: {
      useSuspense: false 
    }
  });

export default i18n;
