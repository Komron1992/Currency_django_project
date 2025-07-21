// frontend/src/utils/bankLogos.js

/**
 * Маппинг банков к их логотипам
 * Ключ - это название банка или ID банка из API
 * Значение - путь к логотипу
 */
export const bankLogos = {
  // Основные банки Таджикистана
  'alif': '/images/banks/alif.jpg',
  'amonatbonk': '/images/banks/amonatbonk.jpg',
  'arvand': '/images/banks/arvand.jpg',
  'azizimoliya': '/images/banks/azizimoliya.jpg',
  'Bonki Rushd': '/images/banks/brt.jpg',
  'kommersbank': '/images/banks/kommersbank.jpg',
  'eskhata': '/images/banks/eskhata.jpg',
  'finca': '/images/banks/finca.jpg',
  'humo': '/images/banks/humo.jpg',
  'ibt': '/images/banks/ibt.jpg',
  'imon': '/images/banks/imon.jpg',
  'matin': '/images/banks/matin.jpg',
  'nbt': '/images/banks/nbt.jpg',
  'oriyonbonk': '/images/banks/oriyonbank.jpg',
  'spitamenbank': '/images/banks/spitamenbank.jpg',
  'Sanoatsodirotbonk': '/images/banks/ssb.jpg',
  'tawhidbank': '/images/banks/tawhidbank.jpg',
  'tejaratbank': '/images/banks/tejaratbank.jpg',

  // Альтернативные названия (если API использует другие названия)
  'Алиф банк': '/images/banks/alif.jpg',
  'Амонатбанк': '/images/banks/amonatbank.jpg',
  'Арванд банк': '/images/banks/arvand.jpg',
  'Азизи молия': '/images/banks/azizimoliya.jpg',
  'БРТ': '/images/banks/brt.jpg',
  'ЦБТ': '/images/banks/cbt.jpg',
  'Эсхата банк': '/images/banks/eskhata.jpg',
  'Финка': '/images/banks/finca.jpg',
  'Хумо': '/images/banks/humo.jpg',
  'ИБТ': '/images/banks/ibt.jpg',
  'Имон': '/images/banks/imon.jpg',
  'Матин банк': '/images/banks/matin.jpg',
  'НБТ': '/images/banks/nbt.jpg',
  'Ориён банк': '/images/banks/oriyonbank.jpg',
  'Спитамен банк': '/images/banks/spitamenbank.jpg',
  'ССБ': '/images/banks/ssb.jpg',
  'Тавхид банк': '/images/banks/tawhidbank.jpg',
  'Теджарат банк': '/images/banks/tejaratbank.jpg',
}

/**
 * Получить логотип банка по названию
 * @param {string} bankName - Название банка
 * @returns {string} - Путь к логотипу или null
 */
export function getBankLogo(bankName) {
  if (!bankName) return null

  // Нормализуем название банка (убираем лишние пробелы, приводим к нижнему регистру)
  const normalizedName = bankName.toString().trim().toLowerCase()

  // Ищем точное совпадение
  if (bankLogos[normalizedName]) {
    return bankLogos[normalizedName]
  }

  // Ищем частичное совпадение
  for (const [key, logo] of Object.entries(bankLogos)) {
    if (key.toLowerCase().includes(normalizedName) || normalizedName.includes(key.toLowerCase())) {
      return logo
    }
  }

  return null
}

/**
 * Получить дефолтный логотип банка (SVG иконка)
 * @returns {string} - SVG иконка
 */
export function getDefaultBankIcon() {
  return `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <polyline points="9,22 9,12 15,12 15,22"/>
    </svg>
  `
}