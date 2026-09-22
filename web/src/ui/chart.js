/**
 * Отрисовка тепловой карты режимов через Plotly (адаптировано из
 * FlowMapFrontend/chart.js — API карты и подписи осей не менялись).
 */

/**
 * grid.vsg1d идёт по возрастанию, но codeMatrix[0] соответствует vsg = max
 * (см. web/src/core/grid.js) — поэтому для оси y передаём реверсированную
 * копию vsg1d, чтобы подписи осей совпадали со значениями в матрице.
 * @param {import("../core/grid.js").GridInfo} grid
 * @param {number[][]} codeMatrix
 * @param {boolean} [invertAxes] поменять местами оси X/Y (X=газ, Y=жидкость)
 */
export function renderHeatmap(grid, codeMatrix, invertAxes = false) {
  const vslAxis = grid.vsl1d;
  const vsgAxisReversed = grid.vsg1d.slice().reverse();

  let x = vslAxis;
  let y = vsgAxisReversed;
  let z = codeMatrix;
  let xLabel = "Скорость жидкости, м/с";
  let yLabel = "Скорость газа, м/с";

  if (invertAxes) {
    x = vsgAxisReversed;
    y = vslAxis;
    // codeMatrix[i][j] соответствует (x=vslAxis[j], y=vsgAxisReversed[i]);
    // при перестановке осей нужна транспонированная матрица.
    z = codeMatrix[0].map((_, j) => codeMatrix.map((row) => row[j]));
    [xLabel, yLabel] = [yLabel, xLabel];
  }

  const data = [{
    x,
    y,
    z,
    type: "heatmap",
    colorscale: "Portland",
    hovertemplate: `${xLabel}: %{x}<br>${yLabel}: %{y}<br>Код: %{z}<extra></extra>`,
  }];

  const layout = {
    xaxis: { title: xLabel, type: grid.logScale ? "log" : "linear" },
    yaxis: { title: yLabel, type: grid.logScale ? "log" : "linear" },
    margin: { t: 30 },
  };

  Plotly.newPlot("chart", data, layout, { responsive: true });
}

/**
 * @param {Record<number, string>} patternLegend
 */
export function renderLegend(patternLegend) {
  const legendEl = document.getElementById("legend");
  legendEl.innerHTML = "";
  const ul = document.createElement("ul");
  for (const [code, name] of Object.entries(patternLegend)) {
    const li = document.createElement("li");
    li.textContent = `${code} — ${name}`;
    ul.appendChild(li);
  }
  legendEl.appendChild(ul);
}
