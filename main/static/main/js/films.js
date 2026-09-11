function changeContent(tabNumber) {
    // Скрываем вкладки
    const contents = document.querySelectorAll('.content');
    contents.forEach(content => {
        content.classList.remove('active');
    });

    // скрываем содержимое вкладок
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });

    // Показываем выбранное содержимое и добавляем активный класс к вкладке
    let targetTabElement = document.getElementById('tab' + tabNumber);
    targetTabElement.classList.add('active');
    let targetContentElement = document.getElementById('content' + tabNumber);
    targetContentElement.classList.add('active');
}

function preventUncheck(checkbox) {
  // Если пытаются снять галку с первого чекбокса, возвращаем ее обратно
  if (checkbox.id === 'checkbox1' && !checkbox.checked) {
    checkbox.checked = true;
  }
}

function toggleReady(checkbox) {
  const allCheckbox = document.getElementById('checkbox1');
  const aucCheckbox = document.getElementById('checkbox2');
  const buyCheckbox = document.getElementById('checkbox3');

  // Снимаем галки с других чекбоксов
  if (checkbox.id === 'checkbox1' && checkbox.checked) {
    aucCheckbox.checked = false;
    buyCheckbox.checked = false;
  } else if (checkbox.id === 'checkbox2' && checkbox.checked) {
    allCheckbox.checked = false;
    buyCheckbox.checked = false;
  } else if (checkbox.id === 'checkbox3' && checkbox.checked) {
    allCheckbox.checked = false;
    aucCheckbox.checked = false;
  }

  // Если снимают галку со второго или третьего чекбокса,
  // автоматически активируем первый чекбокс
  if ((checkbox.id === 'checkbox2' || checkbox.id === 'checkbox3') && !checkbox.checked) {
    allCheckbox.checked = true;
  }

  const rows = document.querySelectorAll('tbody tr');

  // Показываем все строки
  // класс check-ready означает, что строка должна быть активирована (показана) чекбоксом
  if (allCheckbox.checked) {
    rows.forEach(row => {
      if (row.classList.contains('month-active') && row.classList.contains('nickname-active')) {
          row.classList.remove('hidden');
      }
      row.classList.add('check-ready');
    })
  } else if (aucCheckbox.checked) {
    // Скрываем строки с классом "buy"
    rows.forEach(row => {
      if (row.classList.contains('buy')) {
        row.classList.add('hidden');
        row.classList.remove('check-ready');
      } else {
        // если строка не содержит отметку активированного фильтром месяца или никнейма, то не показываем её
        if (row.classList.contains('month-active') && row.classList.contains('nickname-active')) {
            row.classList.remove('hidden');
        }
        row.classList.add('check-ready');
      }
    });
  } else if (buyCheckbox.checked) {
    // Скрываем строки с классом "auc"
    rows.forEach(row => {
      if (row.classList.contains('auc')) {
        row.classList.add('hidden');
        row.classList.remove('check-ready');
      } else {
        // если строка не содержит отметку активированного фильтром месяца или никнейма, то не показываем её
        if (row.classList.contains('month-active') && row.classList.contains('nickname-active')) {
            row.classList.remove('hidden');
        }
        row.classList.add('check-ready');
      }
    });
  } else {
    // Если ни один чекбокс не выбран, показываем все строки
    rows.forEach(row => {
      if (row.classList.contains('month-active') && row.classList.contains('nickname-active')) {
          row.classList.remove('hidden');
      }
      row.classList.add('check-ready');
    })
  }
  updateResultsCounter();
}

const MONTHS_RU = { 1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня', 7: 'июля', 8: 'августа',
                    9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря' };
const MONTH_RU_2 = {
    'января': 'январь',
    'февраля': 'февраль',
    'марта': 'март',
    'апреля': 'апрель',
    'мая': 'май',
    'июня': 'июнь',
    'июля': 'июль',
    'августа': 'август',
    'сентября': 'сентябрь',
    'октября': 'октябрь',
    'ноября': 'ноябрь',
    'декабря': 'декабрь',
}

// Функция для фильтрации записей по выбранному месяцу
function filterByMonth() {
    const selectElement = document.querySelector('#month-select');
    const selectedMonthYear = selectElement.value.toLowerCase();
    const rows = Array.from(document.querySelectorAll('#results-table-body > tr'));

    if (!selectedMonthYear) {
        return;
    }

    // Сокрытие строк, которые не относятся к выбранному месяцу
    rows.forEach(row => {
        if (selectedMonthYear != 'all') {
            const month = row.cells[0].innerText.split(' ')[1];
            const year = row.cells[0].innerText.split(' ')[2];
            const currentDatetimeText = `${MONTH_RU_2[month]} ${year}`;

            if (currentDatetimeText !== selectedMonthYear) {
                row.classList.add('hidden');
                row.classList.remove('month-active');
            } else {
                if (row.classList.contains('nickname-active') && row.classList.contains('check-ready')) {
                    row.classList.remove('hidden');
                }
                row.classList.add('month-active');
            }
        } else {
            row.classList.add('month-active');
            if (row.classList.contains('nickname-active') && row.classList.contains('check-ready')) {
                row.classList.remove('hidden');
            } else {
                row.classList.add('hidden');
            }
        }
    });
    updateResultsCounter();
}

// Функция для фильтрации записей по выбранному никнейму
function filterByNickname() {
    const selectElement = document.querySelector('#nickname-select');
    const selectedNickname = selectElement.value;
    const rows = Array.from(document.querySelectorAll('#results-table-body > tr'));

    if (!selectedNickname) {
        return;
    }

    // Сокрытие строк, которые не относятся к выбранному месяцу
    rows.forEach(row => {
        if (selectedNickname != 'all') {
            const currentNickname = row.cells[5].innerText;
            if (!currentNickname.includes(selectedNickname)) {
                row.classList.add('hidden');
                row.classList.remove('nickname-active');
            } else {
                if (row.classList.contains('month-active') && row.classList.contains('check-ready')) {
                    row.classList.remove('hidden');
                }
                row.classList.add('nickname-active');
            }
        } else {
            row.classList.add('nickname-active');
            if (row.classList.contains('month-active') && row.classList.contains('check-ready')) {
                row.classList.remove('hidden');
            } else {
                row.classList.add('hidden');
            }
        }
    });
    updateResultsCounter();
}

function updateResultsCounter() {
    const rows = Array.from(document.querySelectorAll('#results-table-body > tr'));
    // Показываем все строки по умолчанию
    let counter = 0;
    rows.forEach(row => {
        if (!row.classList.contains('hidden')) { counter++; }
    });
    document.querySelector('.results-counter').querySelector('span').innerText = `${counter}`;
}

// закрытие всех открытых спойлеров при открытии нового
function toggleSpoilers(event) {
    const summaries = document.querySelectorAll('.film-main-container summary');

    summaries.forEach(summary => {
        const details = summary.parentElement;
        // Закрываем все спойлеры, кроме того, на который кликнули
        if (details !== event.currentTarget) {
            details.removeAttribute('open'); // Закрываем спойлер
        }
    });
}

// открытие или закрытие сразу всех спойлеров
function toggleSpoilersAll(option) {
    const summaries = document.querySelectorAll('.film-main-container summary');
    if (option == 'open') {
        summaries.forEach(summary => {
            const details = summary.parentElement;
            details.setAttribute('open', '');
        });
    } else {
        summaries.forEach(summary => {
            const details = summary.parentElement;
            details.removeAttribute('open');
        });
    }
}
