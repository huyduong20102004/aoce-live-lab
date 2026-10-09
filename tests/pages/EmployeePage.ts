import { expect, type Page } from '@playwright/test';
import { EmployeeElements } from '../elements/EmployeeElements.js';
export class EmployeePage {
  readonly elements: EmployeeElements;
  constructor(readonly page: Page) { this.elements = new EmployeeElements(page); }
  async open(scenario?: string) {
    await this.page.goto(scenario ? `/?scenario=${scenario}` : '/');
    await expect(this.page.getByRole('heading', { name: 'Employee directory', exact: true })).toBeVisible();
  }
  async create(id: string, department: string, expectUnknown = false) {
    await this.elements.create.click();
    await expect(this.elements.dialog).toHaveAccessibleName('Create employee');
    await this.elements.dialog.getByLabel('Employee ID', { exact: true }).fill(id);
    await this.elements.dialog.getByRole('combobox', { name: 'Department', exact: true }).selectOption(department);
    await expect(this.elements.save).toHaveCount(1);
    await this.elements.save.click();
    if (expectUnknown) await expect(this.elements.dialog.getByRole('alert')).toContainText('Write outcome UNKNOWN');
    else await expect(this.elements.dialog).not.toBeVisible();
  }
  async search(id: string) {
    await this.elements.directory.getByRole('textbox', { name: 'Search employee ID', exact: true }).fill(id);
    await this.elements.directory.getByRole('button', { name: 'Search', exact: true }).click();
  }
  async changeDepartment(id: string, department: string) {
    await this.search(id); await this.elements.row(id).getByRole('button', { name: 'Edit', exact: true }).click();
    await expect(this.elements.dialog).toHaveAccessibleName('Edit employee');
    await expect(this.elements.dialog.getByLabel('Employee ID', { exact: true })).toHaveValue(id);
    await this.elements.dialog.getByRole('combobox', { name: 'Department', exact: true }).selectOption(department);
    await this.elements.save.click(); await expect(this.elements.dialog).not.toBeVisible();
    await this.search(id);
  }
}
