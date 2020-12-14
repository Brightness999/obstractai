<template>
  <section class="section app-card">
    <div class="columns">
        <div class="column is-one-third">
            <img alt="Nothing Here" :src="staticFiles.undraw_empty"/>
        </div>
        <div class="column is-two-thirds">
            <h1 class="title is-4">No Employees Yet!</h1>
            <h2 class="subtitle">Create your first employee below to get started.</h2>

            <p>
                <a class="button is-primary" v-on:click="$emit('add-employee')">
                    <span class="icon is-small"><i class="fa fa-plus"></i></span>
                    <span>Create Employee</span>
                </a>
            </p>
        </div>
    </div>
</section>
</template>

<script>
export default {
  name: 'NoData',
  props: {
    static_files: Object
  },
}

</script>
