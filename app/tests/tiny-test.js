/**
 * Минимальный тестовый фреймворк для запуска в браузере (без Node.js/npm).
 * См. web/tests/test-runner.html.
 */

const tests = [];

/**
 * @param {string} name
 * @param {() => void | Promise<void>} fn
 */
export function test(name, fn) {
  tests.push({ name, fn });
}

export function assertEqual(actual, expected, msg = "") {
  if (actual !== expected) {
    throw new Error(`${msg} ожидалось ${expected}, получено ${actual}`);
  }
}

export function assertClose(actual, expected, eps, msg = "") {
  if (Math.abs(actual - expected) > eps) {
    throw new Error(`${msg} ожидалось ~${expected} (eps ${eps}), получено ${actual}`);
  }
}

export function assertThrows(fn, msg = "ожидалось исключение") {
  try {
    fn();
  } catch (e) {
    return;
  }
  throw new Error(msg);
}

export function assertTrue(value, msg = "ожидалось true") {
  if (!value) throw new Error(msg);
}

/**
 * @returns {Promise<{pass: number, fail: number, total: number, failures: {name: string, error: string}[]}>}
 */
export async function runAll() {
  let pass = 0;
  let fail = 0;
  const failures = [];
  for (const t of tests) {
    try {
      await t.fn();
      pass++;
    } catch (e) {
      fail++;
      failures.push({ name: t.name, error: e && e.message ? e.message : String(e) });
    }
  }
  return { pass, fail, total: tests.length, failures };
}
