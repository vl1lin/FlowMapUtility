/**
 * Расчёт матрицы кодов режима течения по сетке.
 * Упрощённая (однопоточная) замена src/flowmaputility/engine/manager.py +
 * engine/worker.py: там расчёт распараллеливался по строкам через
 * multiprocessing.Pool, здесь - обычный последовательный цикл (для
 * реалистичных resolution расчёт в браузере занимает доли секунды,
 * а однопоточный код заметно проще).
 */

/**
 * @param {import("./correlations/base.js").FlowModel} model
 * @param {import("./grid.js").GridInfo} grid
 * @param {(doneRows: number, totalRows: number) => void} [onProgress]
 * @returns {number[][]} матрица кодов режима, [resolution][resolution]
 */
export function calculateGrid(model, grid, onProgress) {
  const { resolution, vsl2d, vsg2d } = grid;
  const codeMatrix = new Array(resolution);

  for (let i = 0; i < resolution; i++) {
    const row = new Array(resolution);
    const vslRow = vsl2d[i];
    const vsgRow = vsg2d[i];
    for (let j = 0; j < resolution; j++) {
      row[j] = model.getPatternCode(vslRow[j], vsgRow[j]);
    }
    codeMatrix[i] = row;
    if (onProgress) onProgress(i + 1, resolution);
  }

  return codeMatrix;
}
