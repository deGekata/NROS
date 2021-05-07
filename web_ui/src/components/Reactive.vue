<script>
	//Importing Bar and mixins class from the vue-chartjs wrapper
	import { Bar, mixins } from "vue-chartjs";
	//Getting the reactiveProp mixin from the mixins module.
	const { reactiveProp } = mixins;
	export default {
		extends: Bar,
		mixins: [reactiveProp],
		data() {
			return {
				//Chart.js options that control the appearance of the chart
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
			// this.chartData is created in the mixin and contains all the data needed to build the chart.
			this.renderChart(this.chartData, this.options);
		},

		created() {
			//anytime the vue instance is created, call the fillData() function.
			this.fillData();
		},
		methods: {
			fillData() {
				this.datacollection = {
					// Data for the y-axis of the chart
					labels: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
					datasets: [
						{
							label: "Data One",
							backgroundColor: "#f87979",
							// Data for the x-axis of the chart
							data: [this.getRandomInt(), this.getRandomInt(), this.getRandomInt(), this.getRandomInt(), this.getRandomInt(), this.getRandomInt(), this.getRandomInt(), this.getRandomInt(), this.getRandomInt(), this.getRandomInt(), this.getRandomInt(), this.getRandomInt()]
						}
					]
				};
			},
			getRandomInt() {
				// JS function to generate numbers to be used for the chart
				return Math.floor(Math.random() * (50 - 5 + 1)) + 5;
			}
		}
	};
</script>
