import { djangoAdminHomeUrl, djangoAdminProjectSearchUrl } from '$lib/api/djangoAdmin';
import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = ({ url }) => {
	const project = url.searchParams.get('project');
	if (project) {
		throw redirect(302, djangoAdminProjectSearchUrl(project));
	}
	throw redirect(302, djangoAdminHomeUrl());
};
