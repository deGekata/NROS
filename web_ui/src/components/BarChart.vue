<script>
	//Importing Bar class from the vue-chartjs wrapper
	import { Bar } from "vue-chartjs";
	//Exporting this so it can be used in other components
	export default {
		extends: Bar,
		data() {
			return {
				datacollection: {
					//Data to be represented on x-axis
					labels: ["Web UI", "Responsiveness", "DB", "Backend", "Frontend", "Flex"],
					datasets: [
						{
							label: "Specs of NROS",
							backgroundColor: "#00FFFF",
							pointBackgroundColor: "white",
							borderWidth: 1,
							pointBorderColor: "#249EBF",
							//Data to be represented on y-axis
							data: [100, 80, 10, 5, 90, -20]
						}
					]
				},
				//Chart.js options that controls the appearance of the chart
				options: {
					scales: {
						yAxes: [
							{
								ticks: {
									beginAtZero: true
								},
								gridLines: {
									display: true
								}
							}
						],
						xAxes: [
							{
								gridLines: {
									display: true
								}
							}
						]
					},
					legend: {
						display: true
					},
					responsive: true,
					maintainAspectRatio: false
				}
			};
		},
		mounted() {
			//renderChart function renders the chart with the datacollection and options object.
			this.renderChart(this.datacollection, this.options);
		}
	};
</script>
