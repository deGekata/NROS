<template>
    <v-card max-width="1000" raised class="mx-auto">
        <v-card-title>
            Product groups
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
                :items="groups"
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
                        text: 'Product Group Id',
                        align: 'start',
                        value: 'id',
                    },
                    {text: 'Product Items', value: 'product_items'},
                ],
                groups: []
            }
        },
        mounted() {
            axios.get('product_groups').then(response => {
                this.groups = response.data.product_groups;
                for (let i =0; i < this.groups.length; i++) {
                    for (let j =0 ; j < this.groups[i].product_items.length; j++) {
                        this.groups[i].product_items[j] = " " + this.groups[i].product_items[j].id;
                        console.log(i, j);
                    }
                }
              });
        }
    }
</script>