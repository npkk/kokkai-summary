import { test, expect } from '@playwright/test';

test.describe('Meeting Search E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // 検索画面が表示されていることを確認
    await expect(page.locator('h1', { hasText: '国会会議録検索' })).toBeVisible();
  });

  test('Test Case 1: Filter by Session, Meeting Name, and House', async ({ page }) => {
    // 2. `第217回 常会`を回次プルダウンから選択する
    await page.locator('select#session-select').waitFor({ state: 'visible' });
    await page.locator('select#session-select').selectOption({ value: '217' });
    await page.waitForLoadState('networkidle');

    // 3. `内閣委員会`を会議名プルダウンから選択する
    await page.locator('select#meeting-name-select').waitFor({ state: 'visible' });
    await page.locator('select#meeting-name-select').selectOption({ label: '内閣委員会' });

    // 4. `衆議院`を ON
    await page.locator('fieldset > button:has-text("衆議院")').waitFor({ state: 'visible' });
    await page.locator('fieldset > button:has-text("衆議院")').click();

    // 5. 検索
    await page.locator('button:has-text("検索")').click();

    // 6. 内閣委員会の各件が表示されること
    await expect(page.locator('.mt-6 > button').first()).toContainText('内閣委員会');
    await expect(page.locator('.mt-6 > button').last()).toContainText('内閣委員会');

    // 7. `衆議院`を OFF にして`参議院`を ON
    await page.locator('fieldset > button:has-text("衆議院")').click(); // 衆議院をOFF
    await page.locator('fieldset > button:has-text("参議院")').click(); // 参議院をON

    // 8. 検索
    await page.locator('button:has-text("検索")').click();
    await page.waitForLoadState('networkidle');

    // 9. 内閣委員会の各件が表示されること
    await expect(page.locator('.mt-6 > button').first()).toContainText('内閣委員会');
    await expect(page.locator('.mt-6 > button').last()).toContainText('内閣委員会');
  });

  test('Test Case 2: Filter by Session, Meeting Name, and House (No results / One result)', async ({ page }) => {
    // 2. `第218回 臨時会`を回次プルダウンから選択する
    await page.locator('select#session-select').waitFor({ state: 'visible' });
    await page.locator('select#session-select').selectOption({ value: '218' });
    await page.waitForLoadState('networkidle');

    // 3. `議院運営委員会`を会議名プルダウンから選択する
    await page.locator('select#meeting-name-select').waitFor({ state: 'visible' });
    await page.locator('select#meeting-name-select').selectOption({ label: '議院運営委員会' });

    // 4. `衆議院`を ON
    await page.locator('fieldset > button:has-text("衆議院")').waitFor({ state: 'visible' });
    await page.locator('fieldset > button:has-text("衆議院")').click();

    // 5. 検索
    await page.locator('button:has-text("検索")').click();

    // 6. 1件も表示されないこと
    await expect(page.locator('.mt-6 > button')).toHaveCount(0);

    // 7. `衆議院`を OFF にして`参議院`を ON
    await page.locator('fieldset > button:has-text("衆議院")').click(); // 衆議院をOFF
    await page.locator('fieldset > button:has-text("参議院")').click(); // 参議院をON

    // 8. 検索
    await page.locator('button:has-text("検索")').click();
    await page.waitForLoadState('networkidle');

    // 9. 1件表示されること
    await expect(page.locator('.mt-6 > button')).toHaveCount(1);
    await expect(page.locator('.mt-6 > button').first()).toContainText('議院運営委員会');
  });
});
