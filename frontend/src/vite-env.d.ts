/// <reference types="vite/client" />

interface ImportMetaEnv {
	readonly VITE_API_URL?: string;
	readonly VITE_SHOW_DEV_LOGIN_HINT?: string;
	readonly VITE_DEV_LOGIN_EMAIL?: string;
	readonly VITE_DEV_LOGIN_PASSWORD?: string;
}

interface ImportMeta {
	readonly env: ImportMetaEnv;
}