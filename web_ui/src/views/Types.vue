<template>
    <v-card max-width="1000" raised class="mx-auto">
        <v-card-title>
            Product Types
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
                :items="types"
                :search="search"
        ></v-data-table>
    </v-card>
</template>

<script>
    import axios from 'axios'
    export default {
        data: function() {
            return {
                search: '',
                headers: [
                    {
                        text: 'Product Id',
                        align: 'start',
                        value: 'id',
                    },
                    {text: 'Name', value: 'name'},
                    {text: 'Price', value: 'price'},
                    {text: 'Volume', value: 'volume'},
                ],
                types: []
            }
        },
        mounted() {
            axios.get('product_types').then(response => {
                this.types = response.data.product_types;
              });
        }
    }
</script>