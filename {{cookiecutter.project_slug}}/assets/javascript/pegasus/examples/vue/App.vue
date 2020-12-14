<template>
  <no-data v-if="employees.length === 0 && !editMode"
           v-on:add-employee="editMode = true" >
  </no-data>
  <employee-list v-else-if="!editMode"
                 v-bind:employees="employees"
                 v-bind:client="client"
                 v-on:add-employee="editMode = true"
                 v-on:edit-employee="editEmployee"
                 v-on:delete-employee="deleteEmployee" >
  </employee-list >
  <employee-edit-form v-else
                      v-bind:employee="currentEmployee"
                      v-bind:client="client"
                      v-bind:department-options="departmentChoices"
                      v-on:cancel-edit="editMode = false"
                      v-on:save-edit="saveEmployee"
  >
  </employee-edit-form>
</template>

<script>
import Vue from 'vue';
import EmployeeTableRow from './components/EmployeeTableRow.vue';
import EmployeeList from "./components/EmployeeList.vue";
import EmployeeEditForm from './components/EmployeeEditForm.vue';
import NoData from './components/NoData.vue';
import {API_ROOT} from "../const";
import {getAction} from '../../../api';

const auth = new coreapi.auth.SessionAuthentication({
    csrfCookieName: 'csrftoken',
    csrfHeaderName: 'X-CSRFToken'
});
const client = new coreapi.Client({auth: auth});

export default {
  name: 'App',
  components: {
    EmployeeList,
    NoData,
    EmployeeTableRow,
    EmployeeEditForm,
  },
  created() {
    let action = getAction(API_ROOT, ["employees", "list"]);
    client.action(window.schema, action).then((result) => {
      this.employees = result.results;
      // this._initializeData(result.results);
    });
  },
  data() {
    return {
      departmentChoices: EMPLOYEE_DEPARTMENT_CHOICES,
      client: client,
      currentEmployee: null,
      employees: [],
      editMode: false,
    }
  },
  methods: {
    addEmployee: function () {
      this.editMode = true;
    },
    deleteEmployee: function (employee) {
      const action = getAction(API_ROOT, ["employees", "delete"]);
      const params = {
        id: employee.id
      };
      this.client.action(window.schema, action, params).then((result) => {
        // and remove from list
        for (let i = 0; i < this.employees.length; i++) {
          if (this.employees[i].id === employee.id) {
            this.employees.splice(i, 1);
            break;
          }
        }
      });
    },
    editEmployee: function (employee) {
      this.currentEmployee = employee;
      this.editMode = true;
    },
    saveEmployee: function (employeeData) {
      let params = {
        name: employeeData.name,
        department: employeeData.department,
        salary: employeeData.salary,
      };
      if (employeeData.id) {
        // existing employee - use an update method with the id set
        params['id'] = employeeData.id;
        let action = getAction(API_ROOT, ["employees", "partial_update"]);
        client.action(window.schema, action, params).then((result) => {
          // find the appropriate item in the list and update in place
          for (let i = 0; i < this.employees.length; i++) {
            if (this.employees[i].id === result.id) {
              // use Vue.set to overcome change detection
              // https://vuejs.org/v2/guide/reactivity.html#Change-Detection-Caveats
              Vue.set(this.employees, i, result);
            }
          }
        }).catch((error) => {
          console.log("Error: ", error);
        });
      } else {
        let action = getAction(API_ROOT, ["employees", "create"]);
        client.action(window.schema, action, params).then((result) => {
          this.employees.push(result);
        });
      }
      // back to list view
      this.editMode = false;
      this.currentEmployee = null;
    }
  }
}
</script>
