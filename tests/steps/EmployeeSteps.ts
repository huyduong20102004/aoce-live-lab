import { EmployeePage } from '../pages/EmployeePage.js';
export class EmployeeSteps {
  constructor(readonly employee: EmployeePage) {}
  async createAndSearch(id: string, department = 'QA') {
    await this.employee.create(id, department); await this.employee.search(id);
  }
  async changeAndSearch(id: string) { await this.employee.changeDepartment(id, 'Engineering'); }
}
