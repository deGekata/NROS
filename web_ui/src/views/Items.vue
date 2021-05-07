<template>
    <v-card max-width="1000" raised class="mx-auto">
        <v-card-title>
            Product Items
            <v-spacer></v-spacer>
            <v-text-field
                    v-model="search"
                    append-icon="mdi-magnify"
                    label="Search"
                    single-line
                    hide-details
            ></v-text-field>
        </v-card-title>
        <v-data-table
                :headers="headers"
                :items="items"
                :search="search"
        ></v-data-table>
    </v-card>
</template>

<script>
    import axios from 'axios'

    export default {
        data: function () {
            return {
                search: '',
                headers: [
                    {
                        text: 'Product Id',
                        align: 'start',
                        value: 'id',
                    },
                    {text: 'Product Type ID', value: 'product_type_id'},
                    {text: 'Count', value: 'count'},
                ],
                items: []
            }
        },
        mounted() {
            axios.get('product_items').then(response => {
                this.items = response.data.product_items;
            });
        }
    }
</script>