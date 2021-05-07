<template>
	<v-container grid-list-xs fluid class="px-10">
		<v-checkbox label="Vibe checkbox" v-model="check" value=""></v-checkbox>
		<h2>You {{ vibeCheck }} the vibe check.</h2>
		<v-img :src="vibeCheck + '.jpg'" alt="" contain height="400px" width="400px"> </v-img>
	</v-container>
</template>

<script>
	export default {
		name: "MainMenu",
		components: {},
		data() {
			return {
				check: false,
				message: "123"
			};
		},
		computed: {
			vibeCheck: function() {
				return this.check === true ? "passed" : "failed";
			}
		}
	};
</script>
