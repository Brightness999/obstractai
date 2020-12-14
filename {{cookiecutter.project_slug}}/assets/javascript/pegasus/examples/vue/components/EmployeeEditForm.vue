<template>
  <section class="section app-card">
    <form>
      <h2 class="subtitle">Employee Details</h2>
      <div class="field"><label class="label">Name</label>
        <div class="control">
          <input class="input" type="text" placeholder="Michael Scott" v-model="name">
        </div>
        <p class="help">Your employee's name.</p>
      </div>
      <div class="field">
        <div class="control">
          <label class="label">Department</label>
          <div class="select">
            <select v-model="department">
              <option v-for="option in departmentOptions" v-bind:value="option.id">
                {{ option.name }}
              </option>
            </select>
          </div>
        </div>
        <p class="help">What department your employee belongs to.</p></div>
      <div class="field">
        <div class="control">
          <label class="label">Salary</label>
          <input class="input" type="number" min="0" placeholder="50000" v-model="salary">
        </div>
        <p class="help">Your employee's annual salary.</p></div>
      <div class="field is-grouped">
        <div class="control">
          <button class="button is-primary" v-on:click.prevent="saveEdit">
            <span class="icon is-small"><i :class="getSaveIconClass"></i></span>
            <span>{{ getSaveIconText }}</span>
          </button>
        </div>
        <div class="control">
          <button class="button is-text" v-on:click.prevent="$emit('cancel-edit')">
            <span>Cancel</span>
          </button>
        </div>
      </div>
    </form>
  </section>
</template>

<script>
export default {
  name: 'EmployeeEditForm',
  components: {},
  data() {
    if (this.employee) {
      return {
        id: this.employee.id,
        name: this.employee.name,
        department: this.employee.department,
        salary: this.employee.salary,
      };
    } else {
      return {
        id: null,
        name: "",
        department: "",
        salary: null,
      };
    }

  },
  props: {
    // initialName: String,
    // initialDepartment: String,
    // initialSalary: Number,
    employee: Object,
    client: Object,
    departmentOptions: Array,
  },
  computed: {
    getSaveIconClass: function () {
      return `fa ${this.employee === null  ? 'fa-plus' : 'fa-check'}`;
    },
    getSaveIconText: function () {
      return `${this.employee === null  ? 'Add' : 'Save'} Employee`;
    },
  },
  methods: {
    saveEdit: function () {
      // pass all data back through the event
      this.$emit('save-edit', this.$data);
    }
  }
};
</script>
