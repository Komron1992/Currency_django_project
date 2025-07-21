// Обновленный сервис для работы с городами
// frontend/src/services/cities.js

// Статические данные городов как fallback (совпадают с cities.json)
const CITIES_DATA = [
  {
    id: 1,
    name: "Душанбе",
    name_en: "Dushanbe",
    region: "Душанбе",
    is_active: true
  },
  {
    id: 2,
    name: "Худжанд",
    name_en: "Khujand",
    region: "Согдийская область",
    is_active: true
  },
  {
    id: 3,
    name: "Истаравшан",
    name_en: "Istaravshan",
    region: "Согдийская область",
    is_active: true
  },
  {
    id: 4,
    name: "Куляб",
    name_en: "Kulob",
    region: "Хатлонская область",
    is_active: true
  },
  {
    id: 5,
    name: "Курган-Тюбе",
    name_en: "Qurghonteppa",
    region: "Хатлонская область",
    is_active: true
  },
  {
    id: 6,
    name: "Турсунзаде",
    name_en: "Tursunzoda",
    region: "Районы республиканского подчинения",
    is_active: true
  },
  {
    id: 7,
    name: "Канибадам",
    name_en: "Kanibadam",
    region: "Согдийская область",
    is_active: true
  },
  {
    id: 8,
    name: "Пенджикент",
    name_en: "Panjakent",
    region: "Согдийская область",
    is_active: true
  },
  {
    id: 9,
    name: "Хорог",
    name_en: "Khorog",
    region: "Горно-Бадахшанская автономная область",
    is_active: true
  },
  {
    id: 10,
    name: "Вахдат",
    name_en: "Vahdat",
    region: "Районы республиканского подчинения",
    is_active: true
  }
];

// Кэш для городов
let cachedCities = null;

// Загрузка городов из JSON файла
async function loadCitiesFromJSON() {
  try {
    console.log('🏙️ Загрузка городов из JSON файла...');
    const response = await fetch('/cities.json');

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ JSON данные загружены:', data);

    // ИСПРАВЛЕНИЕ: Проверяем структуру данных
    let cities;
    if (Array.isArray(data)) {
      // Если данные уже массив
      cities = data;
    } else if (data.cities && Array.isArray(data.cities)) {
      // Если данные в объекте с ключом "cities"
      cities = data.cities;
    } else {
      throw new Error('Неверная структура данных: ожидается массив или объект с ключом "cities"');
    }

    console.log('✅ Города загружены из JSON файла:', cities.length);

    // Возвращаем только активные города
    return cities.filter(city => city.is_active);

  } catch (error) {
    console.error('❌ Ошибка загрузки городов из JSON:', error);
    console.log('🔄 Используем встроенные данные как fallback');

    // Возвращаем встроенные данные как fallback
    return CITIES_DATA.filter(city => city.is_active);
  }
}

// Экспортируем сервис
export const citiesService = {
  // Получить все города (с кэшированием)
  async getAllCities() {
    if (!cachedCities) {
      cachedCities = await loadCitiesFromJSON();
    }
    return cachedCities;
  },

  // Получить город по ID
  async getCityById(id) {
    const cities = await this.getAllCities();
    const city = cities.find(city => city.id === parseInt(id));
    return city || null;
  },

  // Получить города по региону
  async getCitiesByRegion(region) {
    const cities = await this.getAllCities();
    return cities.filter(city => city.region === region);
  },

  // Поиск городов по названию
  async searchCities(query) {
    const cities = await this.getAllCities();
    const searchTerm = query.toLowerCase();

    return cities.filter(city =>
      city.name.toLowerCase().includes(searchTerm) ||
      (city.name_en && city.name_en.toLowerCase().includes(searchTerm))
    );
  },

  // Получить все регионы
  async getRegions() {
    const cities = await this.getAllCities();
    const regions = [...new Set(cities.map(city => city.region))];
    return regions.filter(region => region); // Убираем пустые регионы
  },

  // Принудительно перезагрузить города (очистить кэш)
  async reloadCities() {
    cachedCities = null;
    return await this.getAllCities();
  }
};

// Также экспортируем как default для совместимости
export default citiesService;