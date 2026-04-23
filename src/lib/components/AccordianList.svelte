<script lang="ts">
	import AccordionItem from '$lib/components/AccordianItem.svelte';

	/**
	 * @type {null}
	 */
	let show: null = null;

	export let items;
	export let text;
	export let type;
	// export let data;

	let module_data: ArrayLike<unknown> | { [s: string]: unknown };

	if (type === 'educational-modules') {
		module_data = {
			'Module I: Connectivity': '0, 1,2,3,4',
			'Module II: Landscape': '5,6,7,8',
			'Module III: Localism': '9,10,11,12'
		};

		console.log(module_data);
	}
	const showCollapse = (/** @type {null} */ i: null) => {
		i === show ? (show = null) : (show = i);
	};

	// if (type === 'educational-modules') {
	// 	for (let i = 0; i < data[0].length; i++) {
	// 		console.log(data[0][i].name);
	// 	}
	// }
</script>

<div class="accordian">
	{#if type === 'regular' || type === 'files'}
		{#each items as item, i}
			<AccordionItem {i} {show} {showCollapse} {item} text={text[i]} {type} />
		{/each}
	{:else if type == 'educational-modules'}
		{#each Object.entries(module_data) as [key, value], i}
			<AccordionItem {i} {show} {showCollapse} item={key} text={[value]} />
		{/each}
	{/if}
	<br /><br /><br />
</div>

<style>
	.accordian {
		padding-bottom: 10px;
	}
</style>
