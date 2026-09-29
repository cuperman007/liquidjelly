import enquiries from '../../src/worker.js';

/** @type {import('@cloudflare/workers-types').PagesFunction<Env>} */
export const onRequest = ({request, env}) => enquiries.fetch(request, env);
