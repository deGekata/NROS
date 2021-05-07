<script>
	//Importing Bubble class from the vue-chartjs wrapper
	import { Bubble } from "vue-chartjs";
	//Exporting this so it can be used in other components
	export default {
		extends: Bubble,
		data() {
			return {
				datacollection: {
					//Data to be represented on x-axis
					labels: ["Data"],
					datasets: [
						{
							label: "???",
							backgroundColor: "#f87979",
							pointBackgroundColor: "white",
							borderWidth: 1,
							pointBorderColor: "#249EBF",
							//Data to be represented on y-axis
							data: [
								{
									x: 100,
									y: 0,
									r: 20
								},
								{
									x: 60,
									y: 30,
									r: 20
								},
								{
									x: 40,
									y: 60,
									r: 25
								},
								{
									x: 80,
									y: 80,
									r: 50
								},
								{
									x: 20,
									y: 30,
									r: 25
								},
								{
									x: 0,
									y: 100,
									r: 5
								}
							]
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
									display: false
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
