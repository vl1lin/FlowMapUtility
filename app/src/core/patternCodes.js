/**
 * Единый словарь кодов режимов течения для всех корреляций.
 * Портировано из src/flowmaputility/correlations/base.py (FlowPatternCode)
 * и src/flowmaputility/visualization/palette.py (DEFAULT_COLORS, PATTERN_NAMES).
 */

export const FlowPatternCode = Object.freeze({
  SINGLE_LIQUID: 100,
  SINGLE_GAS: 101,
  BUBBLE: 102,
  SLUG: 103,
  DISPERSED_BUBBLE: 104,
  ANNULAR: 105,
  STRATIFIED: 106,
  UNKNOWN: 199,
});

export const PATTERN_NAMES = Object.freeze({
  100: "Однофазная жидкость",
  101: "Однофазный газ",
  102: "Пузырьковый",
  103: "Пробковый",
  104: "Дисперг. пузырьковый",
  105: "Кольцевой",
  106: "Стратифицированный",
  199: "Неизвестно",
});

export const DEFAULT_COLORS = Object.freeze({
  100: "#2196F3",
  101: "#E0E0E0",
  102: "#4CAF50",
  103: "#FF9800",
  104: "#8BC34A",
  105: "#F44336",
  106: "#9C27B0",
  199: "#000000",
});

/** @returns {Record<number,string>} код -> человекочитаемое имя (для всех известных кодов) */
export function patternLegend() {
  return { ...PATTERN_NAMES };
}
