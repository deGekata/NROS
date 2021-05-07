<template>
	<div class="home">
		<v-snackbar v-model="snackbar" bottom :color="'error'" :timeout="5000">
			Please check you product data!
			<br />
			Your Before range field should be positive
			<v-btn dark text @click="snackbar = false">
				Close
			</v-btn>
		</v-snackbar>
		<v-snackbar v-model="model_trained" bottom :color="'green'" :timeout="5000">
			Your model have trained
			<br />
			We officially congratulate you!
			<v-btn dark text @click="snackbar = false">
				Close
			</v-btn>
		</v-snackbar>

		<v-snackbar v-model="training_error" bottom :color="'error'" :timeout="5000">
			Not enough data for training the model
			<br />
			Should be >= 2 days
			<v-btn dark text @click="training_error = false">
				Close
			</v-btn>
		</v-snackbar>
		<v-snackbar v-model="prediction_error" bottom :color="'blue'" :timeout="5000">
			Not enough data to make prediction
			<br />
			;- (
			<v-btn dark text @click="prediction_error = false">
				Close
			</v-btn>
		</v-snackbar>
		<v-dialog v-model="edit_dialog">
			<v-card>
				<v-card-title>
					<span class="headline">{{ formTitle }}</span>
				</v-card-title>

				<v-card-text>
					<v-container>
						<v-row>
							<v-col cols="12" sm="6" md="4">
								<v-text-field v-model="editedItem.name" disabled label="Name"></v-text-field>
							</v-col>
							<v-col cols="12" sm="6" md="4">
								<v-text-field v-model="editedItem.product_type_id" lable="Product type ID" disabled hide-details label="ID"></v-text-field>
							</v-col>
							<v-col cols="12" sm="6" md="4">
								<v-text-field v-model="editedItem.sell_price" hide-details label="Price" disabled></v-text-field>
							</v-col>
							<v-col cols="12" sm="6" md="4">
								<v-text-field v-model="editedItem.seasonality" hide-details type="number" label="Season day"></v-text-field>
							</v-col>
							<v-col cols="12" sm="6" md="4">
								<v-checkbox v-model="editedItem.lstm" disabled label="Has lstm"></v-checkbox>
							</v-col>
							<v-col cols="12" sm="6" md="4">
								<v-text-field v-model="editedItem.fullness" disabled hide-details type="number" label="Fullness"></v-text-field>
							</v-col>
							<v-col cols="12" sm="6" md="4">
								<v-text-field v-model="editedItem.capacity" hide-details type="number" label="Capacity"></v-text-field>
							</v-col>
							<v-col cols="12" sm="6" md="4">
								<v-text-field v-model="editedItem.minimum" hide-details type="number" label="Minumum"></v-text-field>
							</v-col>
							<v-col cols="12" sm="6" md="4">
								<v-text-field v-model="editedItem.before_range" hide-details type="number" label="Before range (recomended: 3~10)"></v-text-field>
							</v-col>
						</v-row>
					</v-container>
				</v-card-text>

				<v-card-actions>
					<v-spacer></v-spacer>
					<v-btn color="blue darken-1" text @click="close">Cancel</v-btn>
					<v-btn color="blue darken-1" text @click="save">Save</v-btn>
				</v-card-actions>
			</v-card>
		</v-dialog>

		<v-container fluid>
			<v-row align="start" justify="space-around">
				<v-col>
					<v-card class="pa-1" outlined tile>
						<v-card-title class="mt-n2">
							Product Items
							<v-spacer></v-spacer>

							<v-text-field class="mt-n4" v-model="search1" append-icon="mdi-magnify" label="Search" hide-details></v-text-field>
						</v-card-title>
						<v-data-table :loading="!product_items_loaded" :height="180" :headers="product_items_headers" :items="product_items" :search="search1">
							<template v-slot:item.actions="{ item }">
								<v-row>
									<v-icon color="cyan accent-1" @click="getPrediction(item)">
										mdi-currency-usd
									</v-icon>
									<v-icon color="teal darken-1" class="pl-0" @click="trainAll(item)">
										mdi-currency-usd
									</v-icon>
								</v-row>
							</template>
						</v-data-table>
					</v-card>
				</v-col>
				<v-col>
					<v-card outlined tile>
						<v-card-text class="px-0 pa-0">
							<yandex-map disabled :zoom="13" :coords="[55.753, 37.62]" :controls="[]" style="height: 300px;" @map-was-initialized="initHandler">
								<ymap-marker v-bind:key="[item[0], item[1]]" :coords="[item[0], item[1]]" :icon="storeIcon" :hint-content="item[2]" v-for="item in store_coordinates"></ymap-marker>
							</yandex-map>
						</v-card-text>
					</v-card>
				</v-col>

				<v-responsive style="width: 100%"></v-responsive>
				<v-col>
					<v-card class="pa-0" outlined tile>
						<v-card-title class="mt-n2 mb-1">Products parameters</v-card-title>
						<v-divider></v-divider>
						<v-data-table class="mt-n3" :height="400" :headers="store_headers" :items="store_data" :single-expand="singleExpand" :expanded.sync="expanded_table" shop-key="point_id" show-expand :search="table_search" :options.sync="table_pagination" :loading="!store_data_loaded">
							<template v-if="store_data_loaded" v-slot:expanded-item="{ item }">
								<td :colspan="4">
									<v-data-table hide-default-footer :height="250" :headers="property_product_headers" :items="item.product_types" :option.sync="sub_table_pagination" elevation-0>
										<template v-slot:top>
											<v-toolbar flat>
												<v-toolbar-title caption>{{ each_store_products }}</v-toolbar-title>
											</v-toolbar>
										</template>
										<template v-slot:top>
											<v-toolbar flat>
												<v-toolbar-title>Products</v-toolbar-title>
											</v-toolbar>
										</template>
										<template v-slot:item.actions="{ item }">
											<v-icon small class="mr-2" @click="editItem(item)">
												mdi-pencil
											</v-icon>
											<v-icon small class="mr-2" @click="deleteItem(item)">
												mdi-delete
											</v-icon>
											<v-icon small @click="send4training(item)">
												mdi-check
											</v-icon>
										</template>
									</v-data-table>
								</td>
							</template>
						</v-data-table>
					</v-card>
				</v-col>
				<v-col v-if="prediction_loaded">
					<v-card style="width: 100%" class="pa-0" outlined tile>
						<v-card-title class="mt-n2 mb-1"
							>Predictions for:
							{{ prediction[0]["target_id"] }}
							<v-spacer></v-spacer>
						</v-card-title>
						<v-data-table class="mt-n3" :height="400" :headers="prediction_headers" :items="prediction[0]['predictions']" iteam-key="product_type_id"> </v-data-table>
					</v-card>
				</v-col>
			</v-row>
		</v-container>
	</div>
</template>
<script>
	import { yandexMap, ymapMarker } from "vue-yandex-maps";
	import axios from "axios";

	export default {
		name: "VueChartJS",
		components: {
			yandexMap,
			ymapMarker,
		},
		data() {
			return {
				markerIcon: {
					layout: "default#imageWithContent",
					imageHref: "https://cdn2.iconfinder.com/data/icons/maps-navigation-glyph-black/614/3719_-_Pointer_I-512.png",
					imageSize: [43, 43],
					imageOffset: [0, 0],
					contentOffset: [0, 15],
					contentLayout: '<div style="background: red; width: 50px; color: #FFFFFF; font-weight: bold;">$[properties.iconContent]</div>',
				},
				storeIcon: {
					layout: "default#imageWithContent",
					imageHref: "https://image.flaticon.com/icons/png/512/1892/1892627.png",
					imageSize: [43, 43],
					imageOffset: [0, 0],
					contentOffset: [0, 15],
					contentLayout: '<div style="background: red; width: 50px; color: #FFFFFF; font-weight: bold;">$[properties.iconContent]</div>',
				},
				wareHouseIcon: {
					layout: "default#imageWithContent",
					imageHref: "https://cdn4.iconfinder.com/data/icons/supermarket-32/512/warehouse-storage-stocks-store-512.png",
					imageSize: [43, 43],
					imageOffset: [0, 0],
					contentOffset: [0, 15],
					contentLayout: '<div style="background: red; width: 50px; color: #FFFFFF; font-weight: bold;">$[properties.iconContent]</div>',
				},
				search1: "",
				table_search: "",
				switch1: false,
				module1: "",
				singleExpand: true,
				editedProductIndex: -1,
				editedShopIndex: -1,
				model_trained: false,
				store_data_loaded: false,
				table_pagination: {},
				prediction_error: false,
				prediction_loaded: false,
				expanded_table: [],
				snackbar: false,
				training_error: false,
				search_prediction_product_id: "",
				expanded: [],
				edit_dialog: false,
				store_coordinates: [],
				product_items_loaded: false,
				editedItem: {
					name: "",
					product_type_id: 0,
					sell_price: 0,
					seasonality: 0,
					lstm: false,
					fullness: 0,
					capacity: 0,
					minimum: 0,
				},
				defaultItem: {
					name: "",
					product_type_id: 0,
					sell_price: 0,
					seasonality: 0,
					lstm: false,
					fullness: 0,
					capacity: 0,
					minimum: 0,
				},
				property_product_headers: [
					{ text: "Name", value: "name" },
					{ text: "Product ID", value: "product_type_id" },
					{ text: "Price", value: "sell_price" },
					{ text: "Popular season", value: "seasonality" },
					{ text: "Has neural model", value: "lstm" },
					{ text: "Fullness", value: "fullness" },
					{ text: "Capacity", value: "capacity" },
					{ text: "Before range", value: "before_range" },
					{ text: "Minimum", value: "minimum" },
					{ text: "Actions", value: "actions", sortable: false },
				],
				store_headers: [
					{ text: "Store ID", value: "point_id" },
					{ text: "Address", value: "address" },
					{ text: "Longtitude", value: "longitude" },
					{ text: "Latitude", value: "latitude" },
				],
				prediction_headers: [
					{ text: "From warehouse", value: "war_id" },
					{ text: "Warehouse quantity", value: "war_c" },
					{ text: "To retail point", value: "shop_id" },
					{ text: "Retail point quantity", value: "shop_c" },
				],
				sub_table_pagination: [],
				table_selected: [],
				product_items_headers: [
					{ text: "Name", value: "name" },
					{ text: "Product ID", value: "id" },
					{ text: "Price", value: "price" },
					{ text: "Popular season", value: "seasonality" },
					{ text: "Actions", value: "actions", sortable: false },
				],

				store_data: [],
				product_items: [],
				property_items: [],
				prediction: [],
			};
		},
		created() {
			axios
				.get("product_types", {
					Authorization: localStorage.getItem("token") || "",
				})
				.then((response) => {
					this.product_items = response.data.product_types;
					this.product_items_loaded = true;
				});
			axios
				.post("user/integrate", {
					Authorization: localStorage.getItem("token") || "",
				})
				.then((response) => {
					this.store_data = response.data.result;
					this.store_data_loaded = true;
					for (let i = 0; i < this.store_data.length; i++) {
						for (let j = 0; j < this.store_data[i].product_types.length; j++) {
							this.store_data[i].product_types[j]["shop_index"] = i;
						}
						let coord = [this.store_data[i].latitude, this.store_data[i].longitude, this.store_data[i].address];
						this.store_coordinates.push(coord);
					}
				});
		},
		computed: {
			formTitle() {
				return this.editedProductIndex === -1 ? "New Item" : "Edit Item";
			},
		},
		watch: {
			edit_dialog(val) {
				val || this.close();
			},
		},
		methods: {
			editItem(item) {
				this.editedShopIndex = item["shop_index"];
				console.log(this.editedShopIndex, item, item["shop_index"]);
				this.editedProductIndex = this.store_data[this.editedShopIndex].product_types.indexOf(item);
				Object.assign(this.editedItem, this.store_data[this.editedShopIndex].product_types[this.editedProductIndex]);
				this.edit_dialog = true;
			},

			deleteItem(item) {
				this.editedShopIndex = item["shop_index"];
				var index = this.store_data[this.editedShopIndex].product_types.indexOf(item);
				this.store_data[this.editedShopIndex].product_types.splice(index, 1);
			},

			close() {
				this.edit_dialog = false;
				this.$nextTick(() => {
					this.editedItem = Object.assign({}, this.defaultItem);
					this.editedProductIndex = -1;
					this.editedShopIndex = -1;
				});
			},

			save() {
				Object.assign(this.store_data[this.editedShopIndex].product_types[this.editedProductIndex], this.editedItem);
				this.editStoreProduct(this.editedItem);
				this.close();
			},

			send4training(product) {
				if ((product.lstm === true || (!product.lstm && product.before_range > 0)) && product.before_range > 0) {
					axios
						.post("lstms", {
							Authorization: localStorage.getItem("token") || "",
							before_range: product.before_range,
							point_id: product.point_id,
							product_type_id: product.product_type_id,
						})
						.then(() => {
							this.model_trained = true;
						})
						.catch((error) => {
							console.log(error);
							if (error.response.status == 409) {
								this.training_error = true;
							}
						});
				} else {
					this.snackbar = true;
				}
			},

			trainAll(product) {
				axios
					.post("train_all", {
						Authorization: localStorage.getItem("token") || "",
						product_type_id: product.id,
					})
					.then(() => {
						this.getPrediction(product);
					});
			},

			getPrediction(product) {
				axios
					.post("predict", {
						Authorization: localStorage.getItem("token") || "",
						product_type_id: product.id,
					})
					.then((response) => {
						console.log(response.data);
						this.prediction.push(response.data);
						console.log(this.prediction);
					})
					.catch((error) => {
						if (error.response.status == 409) {
							this.prediction_error = true;
						}
					});
				this.prediction_loaded = true;
				console.log(product.id, product);
			},

			editStoreProduct(product) {
				let store = this.store_data[product["shop_index"]];
				console.log("Index:", product["shop_index"], store, store["point_id"]);
				console.log(product.minimum, product.capacity, product.sell_price, product.fullness, store.point_id, product.product_type_id);
				console.log(localStorage.getItem("token"));
				axios.put("tags", {
					Authorization: localStorage.getItem("token") || "",
					minimum: product.minimum,
					capacity: product.capacity,
					sell_price: product.sell_price,
					fullness: product.fullness,
					point_id: store.point_id,
					product_type_id: product.product_type_id,
				});
				axios.put("product_types/" + product.product_type_id.toString(), {
					Authorization: localStorage.getItem("token") || "",
					seasonality: product.seasonality,
					price: product.price,
					name: product.name,
				});
			},
		},
	};
</script>
