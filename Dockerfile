FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Установка Chromium и необходимых зависимостей
RUN apt-get update && \
    apt-get install -y \
    chromium \
    chromium-driver \
    wget curl unzip gnupg netcat-openbsd \
    fonts-liberation libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 \
    libexpat1 libfontconfig1 libgcc1 libgdk-pixbuf2.0-0 \
    libglib2.0-0 libgtk-3-0 libnspr4 libnss3 \
    libpango-1.0-0 libx11-6 libx11-xcb1 libxcb1 \
    libxcomposite1 libxdamage1 libxext6 libxfixes3 \
    libxrandr2 libxss1 libxtst6 lsb-release xdg-utils \
    libxss1 libgconf-2-4 libdrm2 libxss1 libgconf-2-4 \
    xvfb \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Создаем пользователя для запуска Chrome (безопасность)
RUN groupadd -r chrome && useradd -r -g chrome -G audio,video chrome \
    && mkdir -p /home/chrome && chown -R chrome:chrome /home/chrome

# Создаем директории для Chrome
RUN mkdir -p /tmp/chrome /var/run/chrome /home/chrome/.config/chromium && \
    chmod 1777 /tmp/chrome && \
    chown -R chrome:chrome /home/chrome/.config

# Проверка установленных версий
RUN echo "Установленная версия Chromium:" && chromium --version
RUN echo "Установленная версия ChromeDriver:" && chromedriver --version || echo "ChromeDriver не найден в PATH"

# Создаем симлинки для совместимости
RUN ln -sf /usr/bin/chromium /usr/bin/google-chrome && \
    ln -sf /usr/bin/chromium /usr/bin/chrome

# Рабочая директория
WORKDIR /code

# Копируем requirements и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Переменные окружения для Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV DISPLAY=:99

# Дополнительные переменные для стабильности
ENV PYTHONUNBUFFERED=1
ENV CHROME_DEVEL_SANDBOX=/opt/google/chrome/chrome-sandbox
ENV CHROME_NO_SANDBOX=1

# Настройка прав доступа
RUN chown -R chrome:chrome /code

# Копируем и даём права на скрипты запуска
COPY entrypoint.sh /code/entrypoint.sh
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /code/entrypoint.sh /wait-for-it.sh

# Создаем скрипт для запуска с виртуальным дисплеем
RUN echo '#!/bin/bash\n\
# Запуск виртуального дисплея\n\
export DISPLAY=:99\n\
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &\n\
# Ожидание запуска Xvfb\n\
sleep 2\n\
# Выполнение переданной команды\n\
exec "$@"' > /usr/local/bin/with-xvfb.sh && \
chmod +x /usr/local/bin/with-xvfb.sh

# Команда по умолчанию
CMD ["/code/entrypoint.sh"]