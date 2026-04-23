<section class="research-content">
	<p class="placeholder-note">
		This table is a placeholder for research datasets and will be populated from the backend database.
	</p>

	<div class="table-wrap">
		<table class="research-table">
			<thead>
				<tr>
					<th>Dataset</th>
					<th>Organization</th>
					<th>Cadence</th>
					<th>Status</th>
					<th>Last Updated</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td colspan="5" class="empty-row">No research records available yet.</td>
				</tr>
			</tbody>
		</table>
	</div>
</section>

<style>
	.research-content {
		max-width: 1100px;
		margin: 2rem auto;
		padding: 0 1rem 2rem;
	}

	.placeholder-note {
		font-family: 'GT Super Regular', serif;
		margin: 0 0 1rem 0;
		color: #222;
	}

	.table-wrap {
		overflow-x: auto;
		background: #fff;
		border: 1px solid rgba(0, 0, 0, 0.15);
	}

	.research-table {
		width: 100%;
		border-collapse: collapse;
		min-width: 650px;
	}

	.research-table th,
	.research-table td {
		padding: 0.75rem 0.85rem;
		text-align: left;
		border-bottom: 1px solid rgba(0, 0, 0, 0.12);
		font-family: 'GT Super Regular', serif;
	}

	.research-table th {
		font-family: 'GT Super Bold', serif;
		background: #f4f4f4;
	}

	.empty-row {
		text-align: center;
		color: #666;
	}
</style>