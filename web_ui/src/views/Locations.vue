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
                :items="locations"
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
                        text: 'Location Id',
                        align: 'start',
                        value: 'id',
                    },
                    {text: 'Address', value: 'address'},
                    {text: 'Latitude', value: 'latitude'},
                    {text: 'Longitude', value: 'longitude'},
                ],
                locations: []
            }
        },
        mounted() {
            axios.get('locations').then(response => {
                this.locations = response.data.locations;
              });
        }
    }
</script>