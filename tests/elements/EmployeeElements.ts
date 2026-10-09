import type { Page, Locator } from '@playwright/test';
export class EmployeeElements {
  constructor(readonly page: Page) {}
  get directory() { return this.page.frameLocator('iframe[title="Employee directory"]'); }
  get create() { return this.page.getByRole('button', { name: 'Create employee', exact: true }); }
  get dialog() { return this.page.getByRole('dialog'); }
  get save() { return this.dialog.getByRole('button', { name: 'Save', exact: true }); }
  row(id: string): Locator {
    return this.directory.getByRole('row').filter({ has: this.directory.getByRole('cell', { name: id, exact: true }) });
  }
}
